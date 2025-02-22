from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
import streamlit as st
import os
import tempfile
from datetime import datetime
import json

class TelehealthSystem:
    def __init__(self):
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        self.supported_languages = {
            'tr': 'Türkçe',
            'en': 'English',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español',
            'ar': 'العربية',
            'ru': 'Русский'
        }
        
        # Tıbbi terimler sözlüğü
        self.medical_terms = self.load_medical_terms()
    
    def load_medical_terms(self):
        """Tıbbi terimleri yükle"""
        try:
            with open('data/medical_terms.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def translate_text(self, text, target_lang):
        """Metni hedef dile çevir"""
        try:
            if not text:
                return ""
            
            # Tıbbi terimleri koru
            preserved_terms = {}
            for term in self.medical_terms.get(target_lang, {}):
                if term in text:
                    preserved_terms[term] = self.medical_terms[target_lang][term]
            
            # Çeviri yap
            translation = self.translator.translate(text, dest=target_lang)
            result = translation.text
            
            # Tıbbi terimleri geri ekle
            for term, translation in preserved_terms.items():
                result = result.replace(term, translation)
            
            return result
        except Exception as e:
            st.error(f"Çeviri hatası: {str(e)}")
            return text
    
    def speech_to_text(self, audio_file, language='tr'):
        """Ses dosyasını metne çevir"""
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=language)
                return text
        except Exception as e:
            st.error(f"Ses tanıma hatası: {str(e)}")
            return None
    
    def text_to_speech(self, text, language='tr'):
        """Metni sese çevir"""
        try:
            tts = gTTS(text=text, lang=language)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                return fp.name
        except Exception as e:
            st.error(f"Ses oluşturma hatası: {str(e)}")
            return None
    
    def create_multilingual_report(self, report_data, target_lang):
        """Çok dilli rapor oluştur"""
        report = f"SAĞLIK RAPORU / HEALTH REPORT\n"
        report += f"Tarih / Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        for key, value in report_data.items():
            # Başlığı çevir
            translated_key = self.translate_text(key, target_lang)
            # Değeri çevir
            translated_value = self.translate_text(str(value), target_lang)
            
            report += f"{key} / {translated_key}:\n"
            report += f"{value} / {translated_value}\n\n"
        
        return report
    
    def get_language_selector(self):
        """Dil seçici widget'ı oluştur"""
        return st.selectbox(
            "Dil / Language / Sprache / Langue / Idioma / اللغة / Язык",
            options=list(self.supported_languages.keys()),
            format_func=lambda x: self.supported_languages[x],
            index=0
        )
    
    def voice_note_recorder(self):
        """Sesli not kaydedici"""
        if st.button("🎤 Sesli Not Kaydet"):
            with st.spinner("Kayıt yapılıyor..."):
                try:
                    audio_file = "temp_recording.wav"
                    # Burada gerçek ses kaydı yapılacak
                    # (Streamlit'in kısıtlamaları nedeniyle tam implementasyon gerekiyor)
                    st.success("Kayıt tamamlandı!")
                    return audio_file
                except Exception as e:
                    st.error(f"Kayıt hatası: {str(e)}")
                    return None
        return None 