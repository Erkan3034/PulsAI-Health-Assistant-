import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import pytesseract
import cv2
import json
import re

class ClinicalWorkflow:
    def __init__(self):
        self.appointment_slots = self.generate_appointment_slots()
        self.medical_codes = self.load_medical_codes()
        self.report_templates = self.load_report_templates()
        self.ai_findings = {}
        
    def load_medical_codes(self):
        """ICD-10 ve diğer tıbbi kodları yükle"""
        try:
            with open('data/medical_codes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def load_report_templates(self):
        """Rapor şablonlarını yükle"""
        return {
            'radyoloji': {
                'xray': "RÖNTGEN RAPORU\nTarih: {date}\nHasta: {patient}\nBulgu: {findings}\nSonuç: {conclusion}",
                'mri': "MR RAPORU\nTarih: {date}\nHasta: {patient}\nSekans: {sequence}\nBulgu: {findings}\nSonuç: {conclusion}",
                'bt': "BT RAPORU\nTarih: {date}\nHasta: {patient}\nKesit: {section}\nBulgu: {findings}\nSonuç: {conclusion}"
            },
            'laboratuvar': {
                'kan': "KAN TAHLİLİ\nTarih: {date}\nHasta: {patient}\nParametreler:\n{parameters}\nSonuç: {conclusion}",
                'idrar': "İDRAR TAHLİLİ\nTarih: {date}\nHasta: {patient}\nParametreler:\n{parameters}\nSonuç: {conclusion}"
            }
        }
    
    def generate_appointment_slots(self):
        """Randevu slotları oluştur"""
        slots = []
        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for day in range(7):  # Bir haftalık randevu
            current_date = start_date + timedelta(days=day)
            
            # Hafta sonu kontrolü
            if current_date.weekday() >= 5:  # 5: Cumartesi, 6: Pazar
                continue
                
            # 09:00-17:00 arası 30'ar dakikalık slotlar
            current_time = current_date
            while current_time.hour < 17:
                slots.append({
                    'datetime': current_time,
                    'available': True,
                    'patient_id': None,
                    'reason': None
                })
                current_time += timedelta(minutes=30)
        
        return slots
    
    def schedule_appointment(self, patient_id, datetime_slot, reason):
        """Randevu planla"""
        for slot in self.appointment_slots:
            if slot['datetime'] == datetime_slot and slot['available']:
                slot.update({
                    'available': False,
                    'patient_id': patient_id,
                    'reason': reason
                })
                return True
        return False
    
    def get_available_slots(self, date=None):
        """Müsait randevu slotlarını getir"""
        available_slots = []
        for slot in self.appointment_slots:
            if slot['available']:
                if date is None or slot['datetime'].date() == date:
                    available_slots.append(slot)
        return available_slots
    
    def analyze_medical_image(self, image):
        """Tıbbi görüntüleri analiz et"""
        try:
            # OpenCV ile görüntüyü işle
            img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Görüntü iyileştirme
            enhanced = cv2.equalizeHist(gray)
            
            # Tesseract ile metin çıkarımı
            text = pytesseract.image_to_string(enhanced)
            
            # AI analizi (örnek)
            findings = self.analyze_image_findings(enhanced)
            
            return {
                'text': text,
                'findings': findings,
                'abnormalities': self.detect_abnormalities(findings)
            }
            
        except Exception as e:
            st.error(f"Görüntü analizi hatası: {str(e)}")
            return None
    
    def analyze_image_findings(self, image):
        """Görüntüdeki bulguları analiz et"""
        # Örnek bulgular (gerçek uygulamada AI modeli kullanılacak)
        findings = {
            'density_variations': True,
            'symmetry': 'normal',
            'contrast': 'good',
            'artifacts': False
        }
        return findings
    
    def detect_abnormalities(self, findings):
        """Anormallikleri tespit et"""
        abnormalities = []
        
        if findings['density_variations']:
            abnormalities.append("Dansite değişiklikleri tespit edildi")
        if findings['symmetry'] != 'normal':
            abnormalities.append("Asimetri tespit edildi")
        if findings['artifacts']:
            abnormalities.append("Artifaktlar mevcut")
            
        return abnormalities
    
    def generate_medical_report(self, report_type, subtype, data):
        """Tıbbi rapor oluştur"""
        if report_type in self.report_templates and subtype in self.report_templates[report_type]:
            template = self.report_templates[report_type][subtype]
            return template.format(**data)
        return None
    
    def analyze_lab_results(self, results):
        """Laboratuvar sonuçlarını analiz et"""
        analysis = {
            'normal': [],
            'high': [],
            'low': [],
            'critical': []
        }
        
        reference_ranges = {
            'hemoglobin': {'min': 12, 'max': 16},
            'wbc': {'min': 4000, 'max': 11000},
            'platelet': {'min': 150000, 'max': 450000},
            'glucose': {'min': 70, 'max': 100}
        }
        
        for test, value in results.items():
            if test in reference_ranges:
                ref = reference_ranges[test]
                if value < ref['min']:
                    if value < ref['min'] * 0.7:  # %30'dan fazla düşükse kritik
                        analysis['critical'].append(f"{test}: {value} (Kritik düşük)")
                    else:
                        analysis['low'].append(f"{test}: {value} (Düşük)")
                elif value > ref['max']:
                    if value > ref['max'] * 1.3:  # %30'dan fazla yüksekse kritik
                        analysis['critical'].append(f"{test}: {value} (Kritik yüksek)")
                    else:
                        analysis['high'].append(f"{test}: {value} (Yüksek)")
                else:
                    analysis['normal'].append(f"{test}: {value} (Normal)")
        
        return analysis
    
    def create_workflow_dashboard(self, appointments, lab_results, image_analyses):
        """İş akışı gösterge paneli oluştur"""
        # Randevu dağılımı grafiği
        appointment_df = pd.DataFrame(appointments)
        fig_appointments = px.timeline(
            appointment_df,
            x_start='datetime',
            y='reason',
            color='available',
            title="Randevu Takvimi"
        )
        
        # Laboratuvar sonuçları grafiği
        lab_analysis = self.analyze_lab_results(lab_results)
        fig_lab = go.Figure(data=[
            go.Bar(
                x=list(lab_analysis.keys()),
                y=[len(items) for items in lab_analysis.values()],
                marker_color=['green', 'yellow', 'orange', 'red']
            )
        ])
        fig_lab.update_layout(title="Laboratuvar Sonuçları Dağılımı")
        
        return fig_appointments, fig_lab 