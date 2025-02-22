import streamlit as st
import hashlib
import jwt
import datetime
import bcrypt
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import logging
import re
from typing import Dict, Any, Optional

class SecurityManager:
    def __init__(self):
        self.key = self.generate_key()
        self.fernet = Fernet(self.key)
        self.session_duration = datetime.timedelta(hours=8)
        self.max_login_attempts = 3
        self.password_policy = {
            'min_length': 8,
            'require_upper': True,
            'require_lower': True,
            'require_digit': True,
            'require_special': True
        }
        
        # Loglama ayarları
        logging.basicConfig(
            filename='security.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def generate_key(self) -> bytes:
        """Şifreleme anahtarı oluştur"""
        try:
            with open('secret.key', 'rb') as key_file:
                return key_file.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open('secret.key', 'wb') as key_file:
                key_file.write(key)
            return key
    
    def hash_password(self, password: str) -> bytes:
        """Şifreyi güvenli bir şekilde hashle"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)
    
    def verify_password(self, password: str, hashed: bytes) -> bool:
        """Şifre doğrulaması yap"""
        try:
            return bcrypt.checkpw(password.encode(), hashed)
        except Exception as e:
            logging.error(f"Şifre doğrulama hatası: {str(e)}")
            return False
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Veriyi şifrele"""
        try:
            json_data = json.dumps(data)
            return self.fernet.encrypt(json_data.encode()).decode()
        except Exception as e:
            logging.error(f"Veri şifreleme hatası: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Şifrelenmiş veriyi çöz"""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted_data)
        except Exception as e:
            logging.error(f"Veri çözme hatası: {str(e)}")
            raise
    
    def generate_token(self, user_id: str) -> str:
        """JWT token oluştur"""
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.datetime.utcnow() + self.session_duration,
                'iat': datetime.datetime.utcnow()
            }
            return jwt.encode(payload, self.key, algorithm='HS256')
        except Exception as e:
            logging.error(f"Token oluşturma hatası: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Optional[str]:
        """JWT token doğrula"""
        try:
            payload = jwt.decode(token, self.key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            logging.warning("Süresi dolmuş token")
            return None
        except jwt.InvalidTokenError as e:
            logging.warning(f"Geçersiz token: {str(e)}")
            return None
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Şifre güçlülüğünü kontrol et"""
        if len(password) < self.password_policy['min_length']:
            return False, f"Şifre en az {self.password_policy['min_length']} karakter olmalıdır."
        
        if self.password_policy['require_upper'] and not re.search(r'[A-Z]', password):
            return False, "Şifre en az bir büyük harf içermelidir."
        
        if self.password_policy['require_lower'] and not re.search(r'[a-z]', password):
            return False, "Şifre en az bir küçük harf içermelidir."
        
        if self.password_policy['require_digit'] and not re.search(r'\d', password):
            return False, "Şifre en az bir rakam içermelidir."
        
        if self.password_policy['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Şifre en az bir özel karakter içermelidir."
        
        return True, "Şifre gereksinimleri karşılanıyor."
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hassas verileri anonimleştir"""
        anonymized = data.copy()
        
        # TC Kimlik No
        if 'tc_kimlik' in anonymized:
            anonymized['tc_kimlik'] = 'XXX-XX-' + str(anonymized['tc_kimlik'])[-4:]
        
        # Telefon numarası
        if 'telefon' in anonymized:
            anonymized['telefon'] = '+90-XXX-XXX-' + str(anonymized['telefon'])[-4:]
        
        # E-posta
        if 'email' in anonymized:
            email_parts = anonymized['email'].split('@')
            if len(email_parts) == 2:
                anonymized['email'] = email_parts[0][:3] + '...@' + email_parts[1]
        
        return anonymized
    
    def create_audit_log(self, user_id: str, action: str, data: Dict[str, Any]) -> None:
        """Denetim kaydı oluştur"""
        try:
            log_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'user_id': user_id,
                'action': action,
                'data': self.anonymize_data(data)
            }
            
            with open('audit_log.json', 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
                
            logging.info(f"Denetim kaydı oluşturuldu: {action} - Kullanıcı: {user_id}")
        except Exception as e:
            logging.error(f"Denetim kaydı oluşturma hatası: {str(e)}")
    
    def check_data_integrity(self, data: Dict[str, Any], signature: str) -> bool:
        """Veri bütünlüğünü kontrol et"""
        try:
            calculated_signature = hashlib.sha256(
                json.dumps(data, sort_keys=True).encode()
            ).hexdigest()
            return calculated_signature == signature
        except Exception as e:
            logging.error(f"Veri bütünlüğü kontrolü hatası: {str(e)}")
            return False 