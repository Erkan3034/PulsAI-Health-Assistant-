import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

def prepare_medical_dataset():
    """Genişletilmiş tıbbi veri setini hazırlar"""
    # Daha fazla veri örneği
    data = {
        'symptoms': [
            'ateş,öksürük,boğaz ağrısı,halsizlik',
            'baş ağrısı,mide bulantısı,kusma',
            'göğüs ağrısı,nefes darlığı,çarpıntı',
            'karın ağrısı,ishal,kusma',
            'eklem ağrısı,kas ağrısı,ateş',
            'baş dönmesi,bulantı,kusma',
            'öksürük,balgam,nefes darlığı',
            'ishal,karın ağrısı,ateş',
            'baş ağrısı,ateş,halsizlik',
            'göğüs ağrısı,terleme,nefes darlığı',
            'ateş,öksürük,halsizlik',
            'baş ağrısı,görme bozukluğu',
            'karın ağrısı,şişkinlik,iştahsızlık',
            'eklem ağrısı,şişlik,kızarıklık',
            'nefes darlığı,öksürük,balgam',
            'baş dönmesi,denge kaybı,bulantı',
            'ishal,kusma,karın ağrısı',
            'ateş,titreme,kas ağrısı',
            'göğüs ağrısı,çarpıntı,terleme',
            'boğaz ağrısı,öksürük,ateş'
        ],
        'age': [45, 28, 62, 35, 51, 42, 55, 30, 25, 68, 
                33, 47, 39, 52, 61, 29, 44, 37, 58, 31],
        'gender': ['E', 'K', 'E', 'K', 'E', 'K', 'E', 'K', 'E', 'K',
                  'E', 'K', 'E', 'K', 'E', 'K', 'E', 'K', 'E', 'K'],
        'diagnosis': [
            'Üst Solunum Yolu Enfeksiyonu',
            'Migren',
            'Kalp Krizi',
            'Gastroenterit',
            'Grip',
            'Vertigo',
            'Bronşit',
            'Bağırsak Enfeksiyonu',
            'Grip',
            'Kalp Krizi',
            'Covid-19',
            'Migren',
            'Gastrit',
            'Romatizma',
            'KOAH',
            'Vertigo',
            'Gastroenterit',
            'Grip',
            'Kalp Krizi',
            'Farenjit'
        ],
        'severity': ['orta', 'düşük', 'yüksek', 'orta', 'düşük', 'orta', 
                    'orta', 'düşük', 'düşük', 'yüksek', 'orta', 'düşük',
                    'orta', 'orta', 'yüksek', 'düşük', 'orta', 'düşük',
                    'yüksek', 'düşük'],
        'department': [
            'Dahiliye', 'Nöroloji', 'Kardiyoloji', 'Gastroenteroloji',
            'Dahiliye', 'Nöroloji', 'Göğüs Hastalıkları', 'Gastroenteroloji',
            'Dahiliye', 'Kardiyoloji', 'Göğüs Hastalıkları', 'Nöroloji',
            'Gastroenteroloji', 'Romatoloji', 'Göğüs Hastalıkları',
            'Nöroloji', 'Gastroenteroloji', 'Dahiliye', 'Kardiyoloji',
            'Dahiliye'
        ],
        'chronic_conditions': [
            'hipertansiyon', 'yok', 'diyabet,kalp hastalığı', 'yok',
            'astım', 'yok', 'astım,hipertansiyon', 'yok', 'yok',
            'diyabet,hipertansiyon', 'yok', 'migren', 'gastrit',
            'romatizma', 'KOAH', 'yok', 'yok', 'alerji', 'kalp hastalığı',
            'yok'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Veriyi kaydet
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/medical_dataset.csv', index=False)
    print("Ham veri seti oluşturuldu ve kaydedildi.")
    
    return df

def process_dataset(df):
    """Veri setini işler ve modele uygun hale getirir"""
    print("Veri seti işleniyor...")
    
    # Belirtileri ayır ve one-hot encoding uygula
    symptoms_list = []
    for symptom_str in df['symptoms']:
        symptoms_list.extend(symptom_str.split(','))
    unique_symptoms = list(set(symptoms_list))
    
    # Belirtiler için yeni sütunlar oluştur
    for symptom in unique_symptoms:
        df[f'symptom_{symptom}'] = df['symptoms'].apply(
            lambda x: 1 if symptom in x else 0
        )
    
    # Kategorik değişkenleri encode et
    le = LabelEncoder()
    df['gender_encoded'] = le.fit_transform(df['gender'])
    df['diagnosis_encoded'] = le.fit_transform(df['diagnosis'])
    df['severity_encoded'] = le.fit_transform(df['severity'])
    df['department_encoded'] = le.fit_transform(df['department'])
    
    # Kronik hastalıkları işle
    chronic_conditions = []
    for conditions in df['chronic_conditions']:
        if conditions != 'yok':
            chronic_conditions.extend(conditions.split(','))
    unique_conditions = list(set(chronic_conditions))
    
    # Kronik hastalıklar için yeni sütunlar oluştur
    for condition in unique_conditions:
        df[f'chronic_{condition}'] = df['chronic_conditions'].apply(
            lambda x: 1 if condition in x else 0
        )
    
    # Gereksiz sütunları kaldır
    columns_to_drop = ['symptoms', 'chronic_conditions']
    df = df.drop(columns=columns_to_drop)
    
    print("Veri seti işlendi.")
    print(f"Toplam özellik sayısı: {len(df.columns)}")
    print("Özellikler:", df.columns.tolist())
    
    return df

def main():
    print("Veri seti hazırlama başladı...")
    df = prepare_medical_dataset()
    
    print("Veri işleme başladı...")
    processed_df = process_dataset(df)
    
    # İşlenmiş veriyi kaydet
    processed_df.to_csv('data/processed_medical_dataset.csv', index=False)
    print("İşlenmiş veri seti kaydedildi.")
    
    return processed_df

if __name__ == "__main__":
    main() 