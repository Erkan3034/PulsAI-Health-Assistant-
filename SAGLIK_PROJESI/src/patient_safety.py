import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

class PatientSafety:
    def __init__(self):
        self.drug_interactions = self.load_drug_interactions()
        self.emergency_levels = {
            'kirmizi': '🔴 ACİL! Hemen en yakın sağlık kuruluşuna başvurun!',
            'sari': '🟡 DİKKAT! 24 saat içinde doktora başvurun.',
            'yesil': '🟢 Düşük risk. Belirtiler devam ederse doktora başvurun.'
        }
        self.hospitals = self.load_hospitals()
        self.geolocator = Nominatim(user_agent="health_assistant")
        
    def load_drug_interactions(self):
        """İlaç etkileşimleri veritabanını yükle"""
        try:
            return pd.read_csv('data/drug_interactions.csv')
        except FileNotFoundError:
            return pd.DataFrame(columns=['drug1', 'drug2', 'severity', 'description'])
    
    def load_hospitals(self):
        """Hastane veritabanını yükle"""
        try:
            return pd.read_csv('data/hospitals.csv')
        except FileNotFoundError:
            return pd.DataFrame(columns=['name', 'lat', 'lon', 'type', 'emergency'])
    
    def check_drug_interactions(self, medications):
        """İlaç etkileşimlerini kontrol et"""
        warnings = []
        try:
            for i, drug1 in enumerate(medications):
                for drug2 in medications[i+1:]:
                    interaction = self.drug_interactions[
                        ((self.drug_interactions['drug1'] == drug1) & 
                         (self.drug_interactions['drug2'] == drug2)) |
                        ((self.drug_interactions['drug1'] == drug2) & 
                         (self.drug_interactions['drug2'] == drug1))
                    ]
                    if not interaction.empty:
                        warnings.append({
                            'drugs': f"{drug1} - {drug2}",
                            'severity': interaction.iloc[0]['severity'],
                            'description': interaction.iloc[0]['description']
                        })
            return warnings
        except Exception as e:
            st.error(f"İlaç etkileşimi kontrolü hatası: {str(e)}")
            return []
    
    def calculate_emergency_level(self, symptoms, vitals, age):
        """Aciliyet seviyesini hesapla"""
        try:
            # Yaşa göre normal vital değer aralıkları
            if age < 12:
                vital_ranges = {
                    'ates': {'min': 36.5, 'max': 37.5},
                    'nabiz': {'min': 70, 'max': 120},
                    'sistolik': {'min': 90, 'max': 110},
                    'diastolik': {'min': 60, 'max': 75}
                }
            else:
                vital_ranges = {
                    'ates': {'min': 36.5, 'max': 37.2},
                    'nabiz': {'min': 60, 'max': 100},
                    'sistolik': {'min': 90, 'max': 120},
                    'diastolik': {'min': 60, 'max': 80}
                }
            
            # Vital değerleri kontrol et
            vital_warnings = 0
            for vital, value in vitals.items():
                if value < vital_ranges[vital]['min'] or value > vital_ranges[vital]['max']:
                    vital_warnings += 1
            
            # Acil semptomları kontrol et
            emergency_symptoms = [
                'göğüs_ağrısı', 'nefes_darlığı', 'bilinç_kaybı',
                'şiddetli_kanama', 'felç_belirtileri'
            ]
            
            if any(symptom in emergency_symptoms for symptom in symptoms):
                return 'kirmizi'
            elif vital_warnings >= 2:
                return 'sari'
            else:
                return 'yesil'
                
        except Exception as e:
            st.error(f"Aciliyet seviyesi hesaplama hatası: {str(e)}")
            return 'sari'  # Hata durumunda orta seviye döndür
    
    def find_nearest_hospitals(self, location, radius_km=10, emergency_only=False):
        """En yakın hastaneleri bul"""
        try:
            user_location = self.geolocator.geocode(location)
            if not user_location:
                return None
            
            nearby_hospitals = []
            for _, hospital in self.hospitals.iterrows():
                distance = geodesic(
                    (user_location.latitude, user_location.longitude),
                    (hospital['lat'], hospital['lon'])
                ).km
                
                if distance <= radius_km:
                    if not emergency_only or hospital['emergency']:
                        nearby_hospitals.append({
                            'name': hospital['name'],
                            'distance': round(distance, 2),
                            'coords': (hospital['lat'], hospital['lon']),
                            'emergency': hospital['emergency']
                        })
            
            return sorted(nearby_hospitals, key=lambda x: x['distance'])
            
        except Exception as e:
            st.error(f"Hastane arama hatası: {str(e)}")
            return None
    
    def create_hospital_map(self, hospitals, location):
        """Hastane haritası oluştur"""
        try:
            user_location = self.geolocator.geocode(location)
            if not user_location or not hospitals:
                return None
            
            # Harita merkezi
            m = folium.Map(
                location=[user_location.latitude, user_location.longitude],
                zoom_start=13
            )
            
            # Kullanıcı konumu
            folium.Marker(
                [user_location.latitude, user_location.longitude],
                popup="Konumunuz",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
            
            # Hastaneleri ekle
            for hospital in hospitals:
                color = 'red' if hospital['emergency'] else 'green'
                folium.Marker(
                    hospital['coords'],
                    popup=f"{hospital['name']} ({hospital['distance']} km)",
                    icon=folium.Icon(color=color, icon='plus')
                ).add_to(m)
            
            return m
            
        except Exception as e:
            st.error(f"Harita oluşturma hatası: {str(e)}")
            return None
    
    def generate_safety_report(self, patient_data):
        """Güvenlik raporu oluştur"""
        try:
            report = "HASTA GÜVENLİĞİ RAPORU\n"
            report += f"Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            
            # İlaç etkileşimleri
            if 'medications' in patient_data:
                interactions = self.check_drug_interactions(patient_data['medications'])
                report += "İLAÇ ETKİLEŞİMLERİ:\n"
                if interactions:
                    for interaction in interactions:
                        report += f"- {interaction['drugs']}: {interaction['description']}\n"
                else:
                    report += "Bilinen ilaç etkileşimi bulunmamaktadır.\n"
            
            # Aciliyet seviyesi
            if 'symptoms' in patient_data:
                emergency_level = self.calculate_emergency_level(
                    patient_data['symptoms'],
                    patient_data.get('vitals', {}),
                    patient_data.get('age', 0)
                )
                report += f"\nACİLİYET SEVİYESİ: {self.emergency_levels[emergency_level]}\n"
            
            return report
            
        except Exception as e:
            st.error(f"Rapor oluşturma hatası: {str(e)}")
            return "Rapor oluşturulamadı." 