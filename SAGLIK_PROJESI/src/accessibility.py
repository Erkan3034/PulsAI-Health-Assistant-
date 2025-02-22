import streamlit as st
import pyttsx3
import speech_recognition as sr
import json
from PIL import Image
import numpy as np
import cv2
from gtts import gTTS
import tempfile
import os

class AccessibilityInterface:
    def __init__(self):
        self.font_sizes = {
            'küçük': 14,
            'orta': 18,
            'büyük': 24,
            'çok büyük': 32
        }
        self.color_schemes = {
            'standart': {
                'background': '#ffffff',
                'text': '#000000',
                'highlight': '#2196f3'
            },
            'yüksek_kontrast': {
                'background': '#000000',
                'text': '#ffffff',
                'highlight': '#ffeb3b'
            },
            'kolay_okuma': {
                'background': '#f0f8ff',
                'text': '#000080',
                'highlight': '#32cd32'
            }
        }
        self.voice_settings = self.load_voice_settings()
        self.accessibility_preferences = {}
        
    def load_voice_settings(self):
        """Ses ayarlarını yükle"""
        try:
            with open('data/voice_settings.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'rate': 150,
                'volume': 1.0,
                'voice': 'turkish',
                'pitch': 1.0
            }
    
    def apply_font_size(self, text, size):
        """Yazı boyutunu uygula"""
        return f"<span style='font-size: {self.font_sizes[size]}px'>{text}</span>"
    
    def apply_color_scheme(self, scheme_name):
        """Renk şemasını uygula"""
        if scheme_name in self.color_schemes:
            scheme = self.color_schemes[scheme_name]
            st.markdown(
                f"""
                <style>
                    .stApp {{
                        background-color: {scheme['background']};
                        color: {scheme['text']};
                    }}
                    .stButton>button {{
                        background-color: {scheme['highlight']};
                        color: {scheme['text']};
                    }}
                    .stTextInput>div>div>input {{
                        color: {scheme['text']};
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )
    
    def text_to_speech(self, text):
        """Metni sese çevir"""
        try:
            tts = gTTS(text=text, lang='tr')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                return fp.name
        except Exception as e:
            st.error(f"Ses dönüşümü hatası: {str(e)}")
            return None
    
    def speech_to_text(self):
        """Sesi metne çevir"""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Dinleniyor...")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language='tr-TR')
                return text
            except Exception as e:
                st.error(f"Ses tanıma hatası: {str(e)}")
                return None
    
    def create_keyboard_shortcuts(self):
        """Klavye kısayolları oluştur"""
        shortcuts = {
            'Alt + B': 'Büyük yazı tipi',
            'Alt + K': 'Küçük yazı tipi',
            'Alt + Y': 'Yüksek kontrast',
            'Alt + S': 'Sesli okuma',
            'Alt + M': 'Mikrofon'
        }
        return shortcuts
    
    def share_with_caregiver(self, patient_data, caregiver_email):
        """Bakıcı ile paylaş"""
        try:
            # E-posta gönderme işlemi burada implement edilecek
            shared_data = {
                'patient_name': patient_data['name'],
                'medications': patient_data['medications'],
                'appointments': patient_data['appointments'],
                'vital_signs': patient_data['vital_signs']
            }
            
            # Güvenli paylaşım linki oluştur
            share_link = f"https://sağlık-asistanı.com/share/{hash(str(shared_data))}"
            
            return share_link
            
        except Exception as e:
            st.error(f"Paylaşım hatası: {str(e)}")
            return None
    
    def create_gesture_controls(self):
        """Jest kontrollerini oluştur"""
        try:
            cap = cv2.VideoCapture(0)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # El hareketlerini algıla
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                ret, thresh = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                if len(contours) > 0:
                    # En büyük kontur el olarak kabul edilir
                    max_contour = max(contours, key=cv2.contourArea)
                    
                    # El hareketlerini yorumla
                    x, y, w, h = cv2.boundingRect(max_contour)
                    if w > 200:  # Yatay hareket
                        return "swipe_right"
                    elif h > 200:  # Dikey hareket
                        return "swipe_up"
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            st.error(f"Jest kontrolü hatası: {str(e)}")
            return None
    
    def save_preferences(self, preferences):
        """Kullanıcı tercihlerini kaydet"""
        try:
            self.accessibility_preferences.update(preferences)
            with open('data/accessibility_preferences.json', 'w', encoding='utf-8') as f:
                json.dump(self.accessibility_preferences, f)
        except Exception as e:
            st.error(f"Tercih kaydetme hatası: {str(e)}")
    
    def load_preferences(self):
        """Kullanıcı tercihlerini yükle"""
        try:
            with open('data/accessibility_preferences.json', 'r', encoding='utf-8') as f:
                self.accessibility_preferences = json.load(f)
                return self.accessibility_preferences
        except FileNotFoundError:
            return {} 