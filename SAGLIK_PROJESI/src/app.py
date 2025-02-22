import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from advanced_model import AdvancedMedicalModel, train_and_evaluate
from patient_management import PatientManagement
import joblib
import os
import traceback
from psychological_support import PsychologicalSupport
from risk_modeling import RiskModeling
from ai_prediction import AIPrediction
from data_integration import DataIntegration
from reliability_layers import ReliabilityLayers
from genetic_analysis import GeneticAnalysis

# Sayfa yapılandırması en üstte olmalı
st.set_page_config(page_title="PulsAI(Sağlık Asistanı)", layout="wide")

class HealthAssistantApp:
    def __init__(self):
        self.patient_manager = PatientManagement()
        
        # Model eğitimi ve yükleme
        try:
            if not self.check_model_files():
                with st.spinner("Modeller hazırlanıyor, lütfen bekleyin..."):
                    self.model = train_and_evaluate()
                    if self.model is None:
                        st.error("Model eğitimi başarısız oldu!")
                        st.stop()
            else:
                self.model = AdvancedMedicalModel()
                self.model.load_models()
            
            self.load_encoders_and_symptoms()
            
            self.psychological_support = PsychologicalSupport()
            self.risk_modeling = RiskModeling()
            self.ai_prediction = AIPrediction(self.model)
            self.data_integration = DataIntegration()
            self.reliability_layers = ReliabilityLayers()
            self.genetic_analysis = GeneticAnalysis()
            
        except Exception as e:
            st.error(f"Başlatma hatası: {str(e)}")
            st.error(traceback.format_exc())
            st.stop()
    
    def show_patient_login(self):
        """Hasta giriş/kayıt ekranını göster"""
        st.sidebar.header("Hasta Girişi")
        
        login_type = st.sidebar.radio("İşlem Seçin:", ["Giriş Yap", "Kayıt Ol"])
        
        if login_type == "Giriş Yap":
            tc_no = st.sidebar.text_input("T.C. Kimlik No:", max_chars=11)
            birth_date = st.sidebar.date_input("Doğum Tarihi:")
            
            if st.sidebar.button("Giriş"):
                if tc_no and birth_date:
                    patient_id = self.patient_manager.generate_patient_id(
                        tc_no, birth_date.strftime("%Y-%m-%d")
                    )
                    patient = self.patient_manager.get_patient(patient_id)
                    
                    if patient:
                        st.session_state['patient_id'] = patient_id
                        st.session_state['patient_name'] = patient['name']
                        st.rerun()
                    else:
                        st.sidebar.error("Hasta bulunamadı!")
                else:
                    st.sidebar.warning("Tüm alanları doldurun!")
        
        else:  # Kayıt Ol
            with st.sidebar.form("patient_registration"):
                tc_no = st.text_input("T.C. Kimlik No:", max_chars=11)
                name = st.text_input("Ad Soyad:")
                birth_date = st.date_input("Doğum Tarihi:")
                gender = st.selectbox("Cinsiyet:", ["Erkek", "Kadın"])
                contact = st.text_input("İletişim (Telefon):")
                
                if st.form_submit_button("Kayıt Ol"):
                    if all([tc_no, name, birth_date, contact]):
                        patient_id = self.patient_manager.register_patient(
                            tc_no, name, 
                            birth_date.strftime("%Y-%m-%d"),
                            gender, contact
                        )
                        st.session_state['patient_id'] = patient_id
                        st.session_state['patient_name'] = name
                        st.rerun()
                    else:
                        st.error("Tüm alanları doldurun!")
    
    def show_patient_history(self, patient_id):
        """Hasta geçmişini göster"""
        st.header("Geçmiş Ziyaretler")
        
        history = self.patient_manager.get_visit_history(patient_id)
        
        if not history:
            st.info("Henüz ziyaret geçmişi bulunmuyor.")
            return
        
        for visit in reversed(history):
            with st.expander(f"Ziyaret: {visit['timestamp'][:10]}"):
                st.write("**Belirtiler:**")
                st.write(", ".join(visit['symptoms']))
                
                if visit['additional_symptoms']:
                    st.write("**Ek Şikayetler:**")
                    st.write(visit['additional_symptoms'])
                
                st.write("**Tanı:**")
                st.write(f"{visit['diagnosis']} (Güven: %{visit['diagnosis_prob']:.1f})")
                
                st.write("**Risk Seviyesi:**")
                st.write(f"{visit['severity']} (Risk: %{visit['severity_prob']:.1f})")
                
                st.write("**Önerilen Bölüm:**")
                st.write(visit['department'])
    
    def check_model_files(self):
        """Model dosyalarının varlığını kontrol et"""
        required_files = [
            'models/diagnosis_model.pkl',
            'models/severity_model.pkl',
            'models/department_model.pkl'
        ]
        return all(os.path.exists(f) for f in required_files)
    
    def load_encoders_and_symptoms(self):
        """Etiket kodlayıcıları ve belirti listesini yükle"""
        try:
            self.processed_df = pd.read_csv('data/processed_medical_dataset.csv')
            self.symptom_cols = [col.replace('symptom_', '') for col in 
                               self.processed_df.columns if col.startswith('symptom_')]
            self.chronic_cols = [col.replace('chronic_', '') for col in 
                               self.processed_df.columns if col.startswith('chronic_')]
            
            # Label Encoder'ları yükle
            self.diagnosis_classes = sorted(self.processed_df['diagnosis'].unique())
            self.severity_classes = sorted(self.processed_df['severity'].unique())
            self.department_classes = sorted(self.processed_df['department'].unique())
            
        except Exception as e:
            st.error(f"Veri yüklenirken hata oluştu: {str(e)}")
            st.error(traceback.format_exc())
            st.stop()
    
    def prepare_input_features(self, selected_symptoms, age, gender, chronic_conditions):
        """Kullanıcı girdilerini model için hazırla"""
        try:
            # Belirti vektörü
            symptom_vector = np.zeros(len(self.symptom_cols))
            for i, symptom in enumerate(self.symptom_cols):
                if symptom in selected_symptoms:
                    symptom_vector[i] = 1
            
            # Hasta bilgileri
            patient_vector = np.array([age, 1 if gender == "Erkek" else 0])
            
            # Kronik hastalıklar
            chronic_vector = np.zeros(len(self.chronic_cols))
            for i, condition in enumerate(self.chronic_cols):
                if condition in chronic_conditions:
                    chronic_vector[i] = 1
            
            return np.hstack([symptom_vector, patient_vector, chronic_vector])
            
        except Exception as e:
            st.error(f"Özellik hazırlama hatası: {str(e)}")
            st.error(traceback.format_exc())
            return None
    
    def create_gauge(self, value, title):
        """Gösterge grafiği oluştur"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value * 100,
            title = {'text': title},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ]
            }
        ))
        return fig
    
    def generate_report(self, patient_info, analysis_results):
        """Detaylı rapor oluştur"""
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        report = f"""SAĞLIK RAPORU
Tarih: {now}

HASTA BİLGİLERİ
--------------
Yaş: {patient_info['age']}
Cinsiyet: {patient_info['gender']}
Kronik Hastalıklar: {', '.join(patient_info['chronic_conditions']) if patient_info['chronic_conditions'] else 'Yok'}

BELİRTİLER
----------
Seçilen Belirtiler: {', '.join(patient_info['symptoms'])}
Ek Şikayetler: {patient_info['additional_symptoms']}

ANALİZ SONUÇLARI
---------------
Olası Tanı: {analysis_results['diagnosis']}
Tanı Güven Oranı: %{analysis_results['diagnosis_prob']:.1f}

Risk Seviyesi: {analysis_results['severity']}
Risk Oranı: %{analysis_results['severity_prob']:.1f}

Önerilen Bölüm: {analysis_results['department']}

ÖNERİLER
--------
{analysis_results['recommendation']}

YAŞAM TARZI ÖNERİLERİ
---------------------
- Düzenli egzersiz yapmayı deneyin.
- Sağlıklı beslenmeye özen gösterin.
- Stres yönetimi tekniklerini uygulayın.

PSİKOLOJİK DESTEK
-----------------
- Meditasyon veya derin nefes alma tekniklerini uygulayın.
- Gerekirse bir terapiste başvurun.

NOT: Bu rapor bir yapay zeka asistanı (PulsAI) tarafından oluşturulmuştur ve 
sadece bilgilendirme amaçlıdır. Kesin tanı için mutlaka bir sağlık 
kuruluşuna başvurunuz.
"""
        return report
    
    def show_diagnosis_info(self, diagnosis):
        """Verilen tanının kısaca tanımını gösterir"""
        diagnosis_info = {
            'Soğuk algınlığı': "Soğuk algınlığı, üst solunum yollarını etkileyen viral bir enfeksiyondur. Belirtileri arasında burun akıntısı, boğaz ağrısı ve öksürük bulunur.",
            'Grip': "Grip, influenza virüsünün neden olduğu bir solunum yolu enfeksiyonudur. Yüksek ateş, baş ağrısı ve kas ağrıları ile kendini gösterir.",
            'Bronşit': "Bronşit, bronşların iltihaplanmasıdır. Öksürük, balgam ve göğüs ağrısı gibi belirtilerle kendini gösterir.",
            'Zatürre': "Zatürre, akciğerlerin iltihaplanmasıdır. Ateş, öksürük ve nefes darlığı gibi belirtilerle kendini gösterir.",
            'Astım': "Astım, hava yollarının daralması ve iltihaplanması ile karakterize bir hastalıktır. Nefes darlığı, hırıltılı solunum ve öksürük ile kendini gösterir.",
            'Vertigo': "Vertigo, baş dönmesi hissi ile karakterize bir durumdur. Genellikle iç kulak problemleri veya beyinle ilgili sorunlardan kaynaklanır. Belirtileri arasında dengesizlik, bulantı ve baş dönmesi bulunur.",
            'Diyabet': "Diyabet, vücudun insülin üretiminde veya kullanımında sorun yaşadığı bir durumdur. Belirtileri arasında aşırı susama, sık idrara çıkma ve yorgunluk bulunur.",
            'Hipertansiyon': "Hipertansiyon, kan basıncının normalden yüksek olduğu bir durumdur. Genellikle belirti vermez, ancak baş ağrısı ve burun kanaması gibi belirtiler görülebilir.",
            'Mide ülseri': "Mide ülseri, midenin iç yüzeyinde oluşan yaralardır. Belirtileri arasında karın ağrısı, mide bulantısı ve hazımsızlık bulunur.",
            'Migren': "Migren, genellikle başın bir tarafında yoğun ağrı ile karakterize bir baş ağrısı türüdür. Bulantı, kusma ve ışığa hassasiyet gibi belirtilerle birlikte olabilir.",
            'Anemi': "Anemi, vücudun yeterli sağlıklı kırmızı kan hücresine sahip olmaması durumudur. Belirtileri arasında yorgunluk, zayıflık ve soluk cilt bulunur.",
            'Romatizma': "Romatizma, eklemlerde ağrı ve iltihaplanma ile karakterize bir durumdur. Belirtileri arasında eklem ağrısı, şişlik ve hareket kısıtlılığı bulunur.",
            'Sedef hastalığı': "Sedef hastalığı, cildin aşırı hızlı bir şekilde yenilenmesi sonucu oluşan bir durumdur. Kırmızı, pullu lezyonlarla kendini gösterir.",
            'Böbrek taşı': "Böbrek taşı, böbreklerde oluşan sert mineral ve tuz birikintileridir. Belirtileri arasında şiddetli bel ağrısı, idrarda kan ve bulantı bulunur.",
            # Diğer tanılar ve açıklamaları buraya eklenebilir
        }
        
        return diagnosis_info.get(diagnosis, "Bu tanı için açıklama bulunmamaktadır.")
    
    def run(self):
        # Oturum kontrolü
        if 'patient_id' not in st.session_state or st.session_state['patient_id'] is None:
            self.show_patient_login()
            return
        
        st.title('Gelişmiş Sağlık Asistanı')
        
        # Hasta bilgileri ve çıkış
        st.sidebar.success(f"Hoş geldiniz, {st.session_state['patient_name']}")
        if st.sidebar.button("Çıkış Yap"):
            del st.session_state['patient_id']
            del st.session_state['patient_name']
            st.rerun()
            return
        
        # Geçmiş ziyaretleri göster
        self.show_patient_history(st.session_state['patient_id'])
        
        # Geçmiş ziyaretleri silme butonu
        if st.sidebar.button("Geçmiş Ziyaretleri Sil"):
            self.patient_manager.clear_visit_history(st.session_state['patient_id'])
            st.success("Geçmiş ziyaretler başarıyla silindi.")
            st.rerun()  # Sayfayı yenileyerek güncel durumu göster

        # Yeni analiz başlatma butonu
        if st.sidebar.button("Yeni Analiz Başlat"):
            st.session_state['patient_id'] = None  # Mevcut hasta bilgisini sıfırla
            st.session_state['patient_name'] = None
            st.success("Yeni analiz başlatılıyor...")
            st.rerun()  # Sayfayı yenileyerek yeni analiz başlat

        # Sidebar - Hasta Bilgileri
        st.sidebar.header("Hasta Bilgileri")
        age = st.sidebar.slider("Yaş", 0, 100, 25)
        gender = st.sidebar.radio("Cinsiyet", ["Erkek", "Kadın"])
        chronic_conditions = st.sidebar.multiselect(
            "Kronik Hastalıklar",
            self.chronic_cols if hasattr(self, 'chronic_cols') else []
        )
        
        # Ekstra bilgiler
        symptoms_duration = st.sidebar.number_input("Belirtilerin Süresi (gün)", min_value=0)
        symptoms_severity = st.sidebar.slider("Belirtilerin Şiddeti (1-10)", 1, 10, 5)
        
        # Aile geçmişi girişi
        family_history_data = {}
        with st.sidebar.expander("Aile Geçmişi"):
            for disease in self.genetic_analysis.genetic_risk_factors.keys():
                st.write(f"**{disease.title()} Geçmişi**")
                first_degree = st.number_input(f"1. derece akraba sayısı ({disease})", 0, 10)
                second_degree = st.number_input(f"2. derece akraba sayısı ({disease})", 0, 10)
                
                if first_degree > 0 or second_degree > 0:
                    family_history_data[disease] = [
                        {'degree': 1} for _ in range(int(first_degree))
                    ] + [
                        {'degree': 2} for _ in range(int(second_degree))
                    ]

        # Yaşam tarzı seçimleri
        lifestyle_choices = {
            'smoking': st.sidebar.checkbox("Sigara Kullanıyor Musunuz?"),
            'exercise': st.sidebar.checkbox("Düzenli Egzersiz Yapıyor Musunuz?"),
            'diet': st.sidebar.selectbox("Beslenme Alışkanlığınız:", ["Sağlıklı", "Orta", "Sağlıksız"])
        }
        
        # Ana panel - Belirti Seçimi
        st.header("Belirti Seçimi")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_symptoms = st.multiselect(
                "Belirtilerinizi seçin:",
                self.symptom_cols if hasattr(self, 'symptom_cols') else []
            )
        
        with col2:
            additional_symptoms = st.text_area(
                "Ek şikayetlerinizi yazın:",
                height=100,
                help="Listede bulunmayan şikayetlerinizi buraya yazabilirsiniz."
            )
        
        if st.button('Analiz Et'):
            if selected_symptoms or additional_symptoms.strip():
                if st.session_state['patient_id'] is None:
                    st.error("Lütfen önce hasta kaydı yapın veya giriş yapın.")
                    return
                
                try:
                    # Özellikleri hazırla
                    features = self.prepare_input_features(
                        selected_symptoms, age, gender, chronic_conditions
                    )
                    
                    if features is None:
                        st.error("Özellikler hazırlanamadı!")
                        return
                    
                    # Aile geçmişini analiz et
                    genetic_risks = self.genetic_analysis.analyze_family_history(family_history_data)
                    
                    # Yaşam tarzı riskini hesapla
                    self.risk_modeling.calculate_lifestyle_risk(lifestyle_choices)
                    
                    # Hastalık gelişim olasılığını tahmin et
                    disease_probability = self.ai_prediction.predict_disease_probability(features)
                    
                    # Tahminler
                    diagnosis_proba = self.model.predict_proba(
                        features.reshape(1, -1), 'diagnosis'
                    )
                    severity_proba = self.model.predict_proba(
                        features.reshape(1, -1), 'severity'
                    )
                    department_pred = self.model.predict(
                        features.reshape(1, -1), 'department'
                    )[0]
                    
                    # En olası tanı ve olasılığı
                    max_diagnosis_idx = np.argmax(diagnosis_proba)
                    max_diagnosis_prob = diagnosis_proba[0][max_diagnosis_idx]
                    predicted_diagnosis = self.diagnosis_classes[max_diagnosis_idx]
                    
                    # En olası şiddet ve olasılığı
                    max_severity_idx = np.argmax(severity_proba)
                    max_severity_prob = severity_proba[0][max_severity_idx]
                    predicted_severity = self.severity_classes[max_severity_idx]
                    
                    # Sonuçları göster
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Tanı Analizi")
                        st.write(f"Olası Tanı: {predicted_diagnosis}")
                        st.plotly_chart(
                            self.create_gauge(max_diagnosis_prob, "Tanı Güven Oranı")
                        )
                        
                        # Tanım bilgilerini göster
                        diagnosis_description = self.show_diagnosis_info(predicted_diagnosis)
                        st.write("**Tanım:**")
                        st.write(diagnosis_description)
                    
                    with col2:
                        st.subheader("Risk Analizi")
                        st.write(f"Risk Seviyesi: {predicted_severity}")
                        st.plotly_chart(
                            self.create_gauge(max_severity_prob, "Risk Seviyesi")
                        )
                    
                    # Öneriler
                    st.subheader("Öneriler ve Yönlendirme")
                    department = self.department_classes[department_pred]
                    st.write(f"Önerilen Bölüm: {department}")
                    
                    if max_severity_prob > 0.7:
                        recommendation = "⚠️ ACİL DURUM! En yakın acil servise başvurunuz!"
                        st.error(recommendation)
                    elif max_severity_prob > 0.4:
                        recommendation = f"En kısa sürede {department} bölümüne başvurunuz."
                        st.warning(recommendation)
                    else:
                        recommendation = (f"Durumunuz şu an için ciddi görünmüyor, "
                                          f"ancak şikayetleriniz devam ederse {department} "
                                          "bölümüne başvurun.")
                        st.info(recommendation)
                    
                    # Ziyaret verilerini kaydet
                    visit_data = {
                        'symptoms': selected_symptoms,
                        'additional_symptoms': additional_symptoms,
                        'diagnosis': predicted_diagnosis,
                        'diagnosis_prob': max_diagnosis_prob * 100,
                        'severity': predicted_severity,
                        'severity_prob': max_severity_prob * 100,
                        'department': department,
                        'recommendation': recommendation
                    }
                    
                    self.patient_manager.save_visit_history(
                        st.session_state['patient_id'], 
                        visit_data
                    )
                    
                    # Rapor oluştur
                    patient_info = {
                        'age': age,
                        'gender': gender,
                        'chronic_conditions': chronic_conditions,
                        'symptoms': selected_symptoms,
                        'additional_symptoms': additional_symptoms
                    }
                    
                    analysis_results = {
                        'diagnosis': predicted_diagnosis,
                        'diagnosis_prob': max_diagnosis_prob * 100,
                        'severity': predicted_severity,
                        'severity_prob': max_severity_prob * 100,
                        'department': department,
                        'recommendation': recommendation
                    }
                    
                    report = self.generate_report(patient_info, analysis_results)
                    
                    # Raporu indirme butonu
                    st.download_button(
                        label="Raporu İndir",
                        data=report,
                        file_name=f"saglik_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                    # Psikolojik destek analizi
                    psychological_effects = self.psychological_support.analyze_symptom_effects(selected_symptoms)
                    emotional_support = self.psychological_support.provide_emotional_support(psychological_effects)
                    st.write("Duygusal Destek Önerileri:", emotional_support)

                    # Erken uyarı mesajı
                    warning_message = self.ai_prediction.early_warning_system(disease_probability)
                    st.write("Erken Uyarı Mesajı:", warning_message)
                    
                    # Kişiselleştirilmiş öneriler
                    personalized_recommendations = self.genetic_analysis.get_personalized_recommendations(
                        genetic_risks,
                        lifestyle_choices
                    )
                    
                    st.subheader("Genetik Risk Analizi")
                    for disease, risk in genetic_risks.items():
                        risk_percentage = risk * 100
                        st.write(f"**{disease.title()}:** %{risk_percentage:.1f} risk")
                        
                    # Hata ayıklama: Genetik riskleri kontrol et
                    st.write("Genetik Riskler:", genetic_risks)
                    
                    st.subheader("Kişiselleştirilmiş Öneriler")
                    if personalized_recommendations:
                        for rec in personalized_recommendations:
                            st.write(f"**{rec['disease'].title()} için Kişiselleştirilmiş Öneriler:**")
                            with st.expander(f"{rec['disease'].title()} - {rec['risk_level']} Risk"):
                                st.write("**Tarama Önerileri:**")
                                st.write(rec['screening'])
                                st.write("**Önleme Stratejileri:**")
                                for strategy in rec['prevention']:
                                    st.write(f"- {strategy}")
                    else:
                        st.write("Kişiselleştirilmiş öneri bulunamadı.")
                    
                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {str(e)}")
                    st.error(traceback.format_exc())
            else:
                st.warning("Lütfen en az bir belirti seçin veya şikayetinizi yazın.")

if __name__ == '__main__':
    app = HealthAssistantApp()
    app.run()