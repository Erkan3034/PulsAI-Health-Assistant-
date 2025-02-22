import json
import os
from datetime import datetime
import hashlib
import uuid
import base64

class PatientManagement:
    def __init__(self):
        self.patients_dir = "data/patients"
        self.history_dir = "data/patient_history"
        self.users_file = 'data/users.json'
        self.users = {}
        os.makedirs(self.patients_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
        self.ensure_data_directory()
        self.load_users()
        
    def ensure_data_directory(self):
        """Data dizininin varlığını kontrol et ve oluştur"""
        if not os.path.exists('data'):
            os.makedirs('data')
        # JSON dosyasını temiz bir şekilde oluştur
        if not os.path.exists(self.users_file) or os.path.getsize(self.users_file) == 0:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def load_users(self):
        """Kullanıcıları yükle"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():  # Dosya boş değilse
                    self.users = json.loads(content)
                else:
                    self.users = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
            # Hatalı dosyayı yeniden oluştur
            self.save_users()

    def save_users(self):
        """Kullanıcıları kaydet"""
        # Bytes verisini string'e çevir
        users_copy = {}
        for username, user_data in self.users.items():
            user_copy = user_data.copy()
            if isinstance(user_data.get('password'), bytes):
                user_copy['password'] = base64.b64encode(user_data['password']).decode('utf-8')
            users_copy[username] = user_copy

        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users_copy, f, ensure_ascii=False, indent=2)

    def get_user(self, username):
        """Kullanıcı bilgilerini getir"""
        user = self.users.get(username)
        if user and isinstance(user.get('password'), str):
            # String'i bytes'a geri çevir
            try:
                user['password'] = base64.b64decode(user['password'].encode('utf-8'))
            except:
                return None
        return user

    def add_user(self, username, password_hash, name, email):
        """Yeni kullanıcı ekle"""
        if username in self.users:
            return False, "Bu kullanıcı adı zaten kullanılıyor."
        
        self.users[username] = {
            'id': str(len(self.users) + 1),
            'password': password_hash,
            'name': name,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        self.save_users()
        return True, "Kullanıcı başarıyla oluşturuldu."

    def update_user(self, username, data):
        """Kullanıcı bilgilerini güncelle"""
        if username not in self.users:
            return False, "Kullanıcı bulunamadı."
        
        self.users[username].update(data)
        self.save_users()
        return True, "Kullanıcı bilgileri güncellendi."

    def delete_user(self, username):
        """Kullanıcıyı sil"""
        if username not in self.users:
            return False, "Kullanıcı bulunamadı."
        
        del self.users[username]
        self.save_users()
        return True, "Kullanıcı silindi."

    def generate_patient_id(self, tc_no, birth_date):
        """Hasta için benzersiz ID oluştur"""
        unique_str = f"{tc_no}{birth_date}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def register_patient(self, tc_no, name, birth_date, gender, contact):
        """Yeni hasta kaydı oluştur"""
        patient_id = self.generate_patient_id(tc_no, birth_date)
        
        patient_data = {
            'id': patient_id,
            'tc_no': tc_no,
            'name': name,
            'birth_date': birth_date,
            'gender': gender,
            'contact': contact,
            'registration_date': datetime.now().isoformat(),
            'last_visit': None
        }
        
        file_path = os.path.join(self.patients_dir, f"{patient_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(patient_data, f, ensure_ascii=False, indent=4)
            
        return patient_id
    
    def get_patient(self, patient_id):
        """Hasta bilgilerini getir"""
        file_path = os.path.join(self.patients_dir, f"{patient_id}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def save_visit_history(self, patient_id, visit_data):
        """Hasta ziyaret geçmişini kaydet"""
        history_file = os.path.join(self.history_dir, f"{patient_id}_history.json")
        
        # Mevcut geçmişi yükle veya yeni oluştur
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        # Yeni ziyareti ekle
        visit_data['timestamp'] = datetime.now().isoformat()
        history.append(visit_data)
        
        # Geçmişi kaydet
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        
        # Son ziyaret tarihini güncelle
        patient_file = os.path.join(self.patients_dir, f"{patient_id}.json")
        with open(patient_file, 'r', encoding='utf-8') as f:
            patient_data = json.load(f)
        
        patient_data['last_visit'] = datetime.now().isoformat()
        
        with open(patient_file, 'w', encoding='utf-8') as f:
            json.dump(patient_data, f, ensure_ascii=False, indent=4)
    
    def get_visit_history(self, patient_id):
        """Hasta ziyaret geçmişini getir"""
        history_file = os.path.join(self.history_dir, f"{patient_id}_history.json")
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def clear_visit_history(self, patient_id):
        """Hasta ziyaret geçmişini sil"""
        history_file = os.path.join(self.history_dir, f"{patient_id}_history.json")
        if os.path.exists(history_file):
            os.remove(history_file) 