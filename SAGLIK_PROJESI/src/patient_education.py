import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from PIL import Image
import json
import requests
import base64
from io import BytesIO
import pandas as pd
import plotly.figure_factory as ff

class PatientEducation:
    def __init__(self):
        self.anatomical_models = self.load_anatomical_models()
        self.educational_content = self.load_educational_content()
        self.interactive_quizzes = self.load_quizzes()
        self.medical_animations = self.load_animations()
        
    def load_anatomical_models(self):
        """3D anatomik modelleri yükle"""
        try:
            with open('data/anatomical_models.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'organ_systems': {
                    'cardiovascular': {'model_path': 'models/heart.obj', 'texture_path': 'models/heart_texture.png'},
                    'respiratory': {'model_path': 'models/lungs.obj', 'texture_path': 'models/lungs_texture.png'},
                    'digestive': {'model_path': 'models/digestive.obj', 'texture_path': 'models/digestive_texture.png'},
                    'skeletal': {'model_path': 'models/skeleton.obj', 'texture_path': 'models/skeleton_texture.png'}
                }
            }
    
    def load_educational_content(self):
        """Eğitim içeriğini yükle"""
        try:
            with open('data/educational_content.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'hastalıklar': {
                    'diyabet': {
                        'tanım': 'Diyabet, vücudun insülin hormonunu...',
                        'belirtiler': ['Sık idrara çıkma', 'Aşırı susama', 'Açlık hissi'],
                        'risk_faktörleri': ['Obezite', 'Aile öyküsü', 'Hareketsiz yaşam'],
                        'önleme': ['Düzenli egzersiz', 'Sağlıklı beslenme', 'Kilo kontrolü'],
                        'tedavi': ['İlaç tedavisi', 'İnsülin', 'Yaşam tarzı değişiklikleri']
                    },
                    # Diğer hastalıklar...
                }
            }
    
    def load_quizzes(self):
        """İnteraktif sınavları yükle"""
        try:
            with open('data/quizzes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'genel_sağlık': [
                    {
                        'soru': 'Günde kaç bardak su içilmesi önerilir?',
                        'seçenekler': ['4-5', '6-8', '8-10', '10-12'],
                        'doğru_cevap': '8-10',
                        'açıklama': 'Günde 8-10 bardak su içmek optimal hidrasyon için önerilir.'
                    }
                    # Diğer sorular...
                ]
            }
    
    def load_animations(self):
        """Tıbbi animasyonları yükle"""
        return {
            'kalp_atışı': 'animations/heartbeat.gif',
            'solunum': 'animations/breathing.gif',
            'sindirim': 'animations/digestion.gif'
        }
    
    def create_3d_model_viewer(self, model_name):
        """3D model görüntüleyici oluştur"""
        if model_name in self.anatomical_models['organ_systems']:
            model_data = self.anatomical_models['organ_systems'][model_name]
            
            # Plotly ile 3D görselleştirme (örnek)
            fig = go.Figure(data=[go.Surface(z=np.random.randint(10, size=(10, 10)))])
            fig.update_layout(
                title=f'3D {model_name.title()} Modeli',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z'
                ),
                width=600,
                height=600
            )
            
            return fig
        return None
    
    def create_interactive_diagram(self, topic):
        """İnteraktif diyagram oluştur"""
        if topic in self.educational_content['hastalıklar']:
            content = self.educational_content['hastalıklar'][topic]
            
            # Sankey diyagramı oluştur
            fig = go.Figure(data=[go.Sankey(
                node = dict(
                    pad = 15,
                    thickness = 20,
                    line = dict(color = "black", width = 0.5),
                    label = ["Belirtiler", "Risk Faktörleri", "Önleme", "Tedavi"],
                    color = "blue"
                ),
                link = dict(
                    source = [0, 0, 1, 1, 2, 2],
                    target = [2, 3, 2, 3, 1, 3],
                    value = [1, 2, 1, 3, 1, 2]
                )
            )])
            
            return fig
        return None
    
    def create_quiz(self, topic):
        """İnteraktif sınav oluştur"""
        if topic in self.interactive_quizzes:
            questions = self.interactive_quizzes[topic]
            results = {'doğru': 0, 'yanlış': 0}
            
            for i, question in enumerate(questions):
                st.write(f"**Soru {i+1}:** {question['soru']}")
                answer = st.radio(
                    "Cevabınız:",
                    question['seçenekler'],
                    key=f"quiz_{topic}_{i}"
                )
                
                if st.button(f"Kontrol Et (Soru {i+1})"):
                    if answer == question['doğru_cevap']:
                        st.success("Doğru! " + question['açıklama'])
                        results['doğru'] += 1
                    else:
                        st.error(f"Yanlış. Doğru cevap: {question['doğru_cevap']}\n" + question['açıklama'])
                        results['yanlış'] += 1
            
            return results
        return None
    
    def create_progress_tracker(self, completed_content):
        """İlerleme takip grafiği oluştur"""
        total_content = len(self.educational_content['hastalıklar'])
        completion_rate = (len(completed_content) / total_content) * 100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = completion_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Eğitim İlerlemesi"},
            gauge = {
                'axis': {'range': [None, 100]},
                'steps': [
                    {'range': [0, 33], 'color': "lightgray"},
                    {'range': [33, 66], 'color': "gray"},
                    {'range': [66, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': completion_rate
                }
            }
        ))
        
        return fig
    
    def generate_personalized_content(self, patient_data):
        """Kişiselleştirilmiş eğitim içeriği oluştur"""
        personalized_content = {}
        
        # Hasta koşullarına göre içerik seç
        for condition in patient_data.get('conditions', []):
            if condition in self.educational_content['hastalıklar']:
                personalized_content[condition] = self.educational_content['hastalıklar'][condition]
        
        # Yaşa göre içeriği uyarla
        age = patient_data.get('age', 0)
        if age < 18:
            # Gençler için basitleştirilmiş içerik
            for condition, content in personalized_content.items():
                content['tanım'] = self.simplify_text(content['tanım'])
        elif age > 65:
            # Yaşlılar için daha detaylı açıklamalar
            for condition, content in personalized_content.items():
                content['önleme'].extend(['Düzenli doktor kontrolü', 'İlaç takibi'])
        
        return personalized_content
    
    def simplify_text(self, text):
        """Metni basitleştir"""
        # Basit kelimeler ve kısa cümleler kullan
        simplified = text.replace('kompleks', 'karmaşık')
        simplified = simplified.split('. ')[0] + '.'  # İlk cümleyi al
        return simplified
    
    def create_visual_aids(self, topic):
        """Görsel yardımcılar oluştur"""
        if topic in self.educational_content['hastalıklar']:
            content = self.educational_content['hastalıklar'][topic]
            
            # Belirti ve risk faktörleri için pasta grafik
            fig1 = px.pie(
                names=content['belirtiler'],
                title=f"{topic.title()} Belirtileri"
            )
            
            # Önleme ve tedavi için çubuk grafik
            prevention_treatment = pd.DataFrame({
                'Yöntem': content['önleme'] + content['tedavi'],
                'Tip': ['Önleme'] * len(content['önleme']) + ['Tedavi'] * len(content['tedavi'])
            })
            fig2 = px.bar(
                prevention_treatment,
                x='Yöntem',
                color='Tip',
                title=f"{topic.title()} Yönetimi"
            )
            
            return fig1, fig2
        return None, None 