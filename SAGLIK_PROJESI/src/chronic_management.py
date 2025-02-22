import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

class ChronicDiseaseManagement:
    def __init__(self):
        self.vital_ranges = {
            'kan_sekeri': {'min': 70, 'max': 140, 'unit': 'mg/dL'},
            'tansiyon_sistolik': {'min': 90, 'max': 120, 'unit': 'mmHg'},
            'tansiyon_diastolik': {'min': 60, 'max': 80, 'unit': 'mmHg'},
            'nabiz': {'min': 60, 'max': 100, 'unit': 'bpm'},
            'oksijen_saturasyonu': {'min': 95, 'max': 100, 'unit': '%'}
        }
        
        self.lifestyle_recommendations = {
            'diyabet': {
                'beslenme': [
                    'Düşük glisemik indeksli besinler tüketin',
                    'Öğün atlamamaya özen gösterin',
                    'Lifli gıdaları tercih edin'
                ],
                'egzersiz': [
                    'Günde en az 30 dakika yürüyüş yapın',
                    'Haftada 3 gün orta şiddette egzersiz yapın',
                    'Düzenli kas güçlendirme egzersizleri yapın'
                ],
                'stres_yonetimi': [
                    'Düzenli uyku düzenine dikkat edin',
                    'Meditasyon veya nefes egzersizleri yapın',
                    'Stres yönetimi için profesyonel destek alın'
                ]
            },
            'hipertansiyon': {
                'beslenme': [
                    'Tuz tüketimini azaltın',
                    'DASH diyetini uygulayın',
                    'Alkol tüketimini sınırlayın'
                ],
                'egzersiz': [
                    'Düzenli kardiyovasküler egzersiz yapın',
                    'Yüzme veya bisiklet gibi düşük etkili sporları tercih edin'
                ],
                'stres_yonetimi': [
                    'Düzenli kan basıncı ölçümü yapın',
                    'Stres azaltıcı aktivitelere zaman ayırın'
                ]
            }
        }

    def track_vitals(self, patient_id, vital_type, value, timestamp=None):
        """Yaşamsal değerleri kaydet"""
        if timestamp is None:
            timestamp = datetime.now()
            
        if 'vital_signs' not in st.session_state:
            st.session_state.vital_signs = {}
            
        if patient_id not in st.session_state.vital_signs:
            st.session_state.vital_signs[patient_id] = {}
            
        if vital_type not in st.session_state.vital_signs[patient_id]:
            st.session_state.vital_signs[patient_id][vital_type] = []
            
        st.session_state.vital_signs[patient_id][vital_type].append({
            'timestamp': timestamp,
            'value': value
        })

    def analyze_trends(self, patient_id, vital_type, time_range='7d'):
        """Yaşamsal değerlerin trendlerini analiz et"""
        if 'vital_signs' not in st.session_state or \
           patient_id not in st.session_state.vital_signs or \
           vital_type not in st.session_state.vital_signs[patient_id]:
            return None, None
            
        vitals = st.session_state.vital_signs[patient_id][vital_type]
        df = pd.DataFrame(vitals)
        
        # Zaman aralığına göre filtrele
        time_delta = {
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
            '90d': timedelta(days=90)
        }
        
        if time_range in time_delta:
            cutoff_date = datetime.now() - time_delta[time_range]
            df = df[df['timestamp'] >= cutoff_date]
            
        if len(df) < 2:
            return None, None
            
        # Trend analizi
        values = df['value'].values
        trend = 'stable'
        if values[-1] > values[0] * 1.1:
            trend = 'increasing'
        elif values[-1] < values[0] * 0.9:
            trend = 'decreasing'
            
        return df, trend

    def generate_vital_chart(self, df, vital_type):
        """Yaşamsal değerler için grafik oluştur"""
        if df is None or len(df) < 1:
            return None
            
        fig = go.Figure()
        
        # Değer çizgisi
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['value'],
            mode='lines+markers',
            name=vital_type,
            line=dict(color='blue')
        ))
        
        # Normal aralık
        if vital_type in self.vital_ranges:
            range_min = self.vital_ranges[vital_type]['min']
            range_max = self.vital_ranges[vital_type]['max']
            unit = self.vital_ranges[vital_type]['unit']
            
            fig.add_hline(y=range_min, line_dash="dash", line_color="red",
                         annotation_text=f"Min: {range_min} {unit}")
            fig.add_hline(y=range_max, line_dash="dash", line_color="red",
                         annotation_text=f"Max: {range_max} {unit}")
        
        fig.update_layout(
            title=f"{vital_type.replace('_', ' ').title()} Takibi",
            xaxis_title="Tarih",
            yaxis_title=f"Değer ({self.vital_ranges[vital_type]['unit']})",
            height=400
        )
        
        return fig

    def get_lifestyle_plan(self, chronic_conditions):
        """Kronik hastalıklara göre yaşam tarzı önerileri oluştur"""
        plan = {
            'beslenme': set(),
            'egzersiz': set(),
            'stres_yonetimi': set()
        }
        
        for condition in chronic_conditions:
            if condition in self.lifestyle_recommendations:
                for category, recommendations in self.lifestyle_recommendations[condition].items():
                    plan[category].update(recommendations)
        
        return {k: list(v) for k, v in plan.items()}

    def generate_report(self, patient_id, time_range='30d'):
        """Kronik hastalık yönetimi raporu oluştur"""
        report = "KRONIK HASTALIK YÖNETİMİ RAPORU\n"
        report += f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if 'vital_signs' in st.session_state and patient_id in st.session_state.vital_signs:
            for vital_type in st.session_state.vital_signs[patient_id]:
                df, trend = self.analyze_trends(patient_id, vital_type, time_range)
                if df is not None:
                    latest_value = df['value'].iloc[-1]
                    avg_value = df['value'].mean()
                    
                    report += f"{vital_type.replace('_', ' ').title()}:\n"
                    report += f"Son ölçüm: {latest_value} {self.vital_ranges[vital_type]['unit']}\n"
                    report += f"Ortalama: {avg_value:.1f} {self.vital_ranges[vital_type]['unit']}\n"
                    report += f"Trend: {trend}\n\n"
        
        return report 