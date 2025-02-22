import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import plotly.express as px
import plotly.graph_objects as go

class EnvironmentalHealth:
    def __init__(self):
        self.air_quality_thresholds = {
            'PM2.5': {'good': 12, 'moderate': 35.4, 'unhealthy': 55.4},
            'PM10': {'good': 54, 'moderate': 154, 'unhealthy': 254},
            'O3': {'good': 50, 'moderate': 100, 'unhealthy': 150},
            'NO2': {'good': 53, 'moderate': 100, 'unhealthy': 360},
        }
        
        self.climate_related_conditions = {
            'sıcak_hava': [
                'sıcak_çarpması',
                'dehidrasyon',
                'güneş_yanığı'
            ],
            'soğuk_hava': [
                'hipotermi',
                'soğuk_yanığı',
                'grip'
            ],
            'yüksek_nem': [
                'astım_alevlenmesi',
                'mantar_enfeksiyonları',
                'eklem_ağrıları'
            ],
            'hava_kirliliği': [
                'solunum_yolu_irritasyonu',
                'göz_irritasyonu',
                'baş_ağrısı'
            ],
            'polen': [
                'alerjik_rinit',
                'astım',
                'egzama'
            ]
        }
        
        self.carbon_footprint_factors = {
            'ilaç_üretimi': 0.25,  # kg CO2/ilaç
            'hastane_ziyareti': 2.5,  # kg CO2/ziyaret
            'ambulans': 5.0,  # kg CO2/km
            'tıbbi_atık': 0.5  # kg CO2/kg atık
        }

    def get_air_quality_data(self, location):
        """Hava kalitesi verilerini al"""
        try:
            # API key'i güvenli bir şekilde saklayın
            api_key = st.secrets["air_quality_api_key"]
            
            # OpenWeatherMap API'den hava kalitesi verilerini al
            url = f"http://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                "lat": location['lat'],
                "lon": location['lon'],
                "appid": api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'PM2.5': data['list'][0]['components']['pm2_5'],
                    'PM10': data['list'][0]['components']['pm10'],
                    'O3': data['list'][0]['components']['o3'],
                    'NO2': data['list'][0]['components']['no2']
                }
            else:
                st.error("Hava kalitesi verileri alınamadı.")
                return None
                
        except Exception as e:
            st.error(f"Hava kalitesi verisi alma hatası: {str(e)}")
            return None

    def analyze_environmental_risks(self, air_quality, weather_data, patient_conditions):
        """Çevresel risk analizi yap"""
        risks = []
        
        # Hava kalitesi riskleri
        for pollutant, value in air_quality.items():
            thresholds = self.air_quality_thresholds[pollutant]
            if value > thresholds['unhealthy']:
                risks.append({
                    'type': 'air_quality',
                    'severity': 'high',
                    'description': f"Yüksek {pollutant} seviyesi: {value}"
                })
            elif value > thresholds['moderate']:
                risks.append({
                    'type': 'air_quality',
                    'severity': 'medium',
                    'description': f"Orta {pollutant} seviyesi: {value}"
                })
        
        # Hava durumu riskleri
        temp = weather_data.get('temperature', 20)
        humidity = weather_data.get('humidity', 50)
        
        if temp > 35:
            risks.extend([
                {'type': 'weather', 'severity': 'high', 'description': risk}
                for risk in self.climate_related_conditions['sıcak_hava']
            ])
        elif temp < 0:
            risks.extend([
                {'type': 'weather', 'severity': 'high', 'description': risk}
                for risk in self.climate_related_conditions['soğuk_hava']
            ])
        
        if humidity > 70:
            risks.extend([
                {'type': 'weather', 'severity': 'medium', 'description': risk}
                for risk in self.climate_related_conditions['yüksek_nem']
            ])
        
        # Hasta koşullarına göre özel riskler
        for condition in patient_conditions:
            if 'astım' in condition.lower():
                risks.extend([
                    {'type': 'condition', 'severity': 'high', 'description': risk}
                    for risk in self.climate_related_conditions['hava_kirliliği']
                ])
            if 'alerji' in condition.lower():
                risks.extend([
                    {'type': 'condition', 'severity': 'medium', 'description': risk}
                    for risk in self.climate_related_conditions['polen']
                ])
        
        return risks

    def calculate_carbon_footprint(self, medical_data):
        """Karbon ayak izi hesapla"""
        total_carbon = 0
        breakdown = {}
        
        # İlaç kullanımı
        if 'medications' in medical_data:
            medication_carbon = len(medical_data['medications']) * self.carbon_footprint_factors['ilaç_üretimi']
            total_carbon += medication_carbon
            breakdown['İlaç Üretimi'] = medication_carbon
        
        # Hastane ziyaretleri
        if 'hospital_visits' in medical_data:
            visit_carbon = medical_data['hospital_visits'] * self.carbon_footprint_factors['hastane_ziyareti']
            total_carbon += visit_carbon
            breakdown['Hastane Ziyaretleri'] = visit_carbon
        
        # Ambulans kullanımı
        if 'ambulance_km' in medical_data:
            ambulance_carbon = medical_data['ambulance_km'] * self.carbon_footprint_factors['ambulans']
            total_carbon += ambulance_carbon
            breakdown['Ambulans Kullanımı'] = ambulance_carbon
        
        # Tıbbi atık
        if 'medical_waste' in medical_data:
            waste_carbon = medical_data['medical_waste'] * self.carbon_footprint_factors['tıbbi_atık']
            total_carbon += waste_carbon
            breakdown['Tıbbi Atık'] = waste_carbon
        
        return total_carbon, breakdown

    def create_environmental_report(self, air_quality, risks, carbon_data):
        """Çevresel rapor oluştur"""
        report = "ÇEVRESEL SAĞLIK RAPORU\n"
        report += f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Hava kalitesi
        report += "HAVA KALİTESİ:\n"
        for pollutant, value in air_quality.items():
            report += f"{pollutant}: {value}\n"
        
        # Riskler
        report += "\nÇEVRESEL RİSKLER:\n"
        for risk in risks:
            report += f"- {risk['description']} (Şiddet: {risk['severity']})\n"
        
        # Karbon ayak izi
        report += "\nKARBON AYAK İZİ:\n"
        total_carbon, breakdown = carbon_data
        report += f"Toplam: {total_carbon:.2f} kg CO2\n"
        for category, value in breakdown.items():
            report += f"{category}: {value:.2f} kg CO2\n"
        
        return report

    def create_environmental_dashboard(self, air_quality, risks, carbon_data):
        """Çevresel gösterge paneli oluştur"""
        # Hava kalitesi grafiği
        fig_air = go.Figure()
        
        for pollutant, value in air_quality.items():
            thresholds = self.air_quality_thresholds[pollutant]
            fig_air.add_trace(go.Indicator(
                mode = "gauge+number",
                value = value,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': pollutant},
                gauge = {
                    'axis': {'range': [None, thresholds['unhealthy']]},
                    'steps': [
                        {'range': [0, thresholds['good']], 'color': "lightgreen"},
                        {'range': [thresholds['good'], thresholds['moderate']], 'color': "yellow"},
                        {'range': [thresholds['moderate'], thresholds['unhealthy']], 'color': "red"}
                    ]
                }
            ))
        
        # Karbon ayak izi pasta grafiği
        total_carbon, breakdown = carbon_data
        fig_carbon = px.pie(
            values=list(breakdown.values()),
            names=list(breakdown.keys()),
            title="Karbon Ayak İzi Dağılımı"
        )
        
        return fig_air, fig_carbon 