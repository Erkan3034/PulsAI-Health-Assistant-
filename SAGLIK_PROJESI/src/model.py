import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def veri_hazirlama():
    df = pd.read_csv('data/symptom_dataset.csv')
    
    # Belirtileri birleştir
    belirti_sutunlari = ['Symptom_1', 'Symptom_2', 'Symptom_3']
    df['belirtiler'] = df[belirti_sutunlari].fillna('').agg(' '.join, axis=1)
    
    # Metin verilerini sayısal özelliklere dönüştür
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['belirtiler'])
    
    # Çoklu sınıflandırma için modeller
    disease_model = RandomForestClassifier(n_estimators=100)
    severity_model = RandomForestClassifier(n_estimators=100)
    
    # Modelleri eğit
    disease_model.fit(X, df['Disease'])
    severity_model.fit(X, df['Severity'])
    
    # Referans dataframe'i kaydet - TÜM SÜTUNLARI DAHİL ET
    reference_data = df[['Disease', 'Severity', 'Department', 'Recommendation', 
                        'Age_Risk', 'Gender_Risk', 'Additional_Info']].drop_duplicates()
    
    # Models klasörünü oluştur ve modelleri kaydet
    os.makedirs('models', exist_ok=True)
    with open('models/model.pkl', 'wb') as f:
        pickle.dump((disease_model, severity_model, vectorizer, reference_data), f)
    
    return disease_model, severity_model, vectorizer, reference_data 