import pandas as pd
import os

# Genişletilmiş veri seti
data = {
    'Symptom_1': [
        'ateş', 'baş ağrısı', 'göğüs ağrısı', 'karın ağrısı', 'nefes darlığı',
        'eklem ağrısı', 'ishal', 'yüksek ateş', 'şiddetli baş ağrısı', 'ani göğüs ağrısı'
    ],
    'Symptom_2': [
        'öksürük', 'bulantı', 'terleme', 'kusma', 'çarpıntı',
        'ateş', 'karın ağrısı', 'bilinç bulanıklığı', 'kusma', 'sol kola yayılan ağrı'
    ],
    'Symptom_3': [
        'halsizlik', 'ışığa hassasiyet', 'sırt ağrısı', 'ishal', 'soğuk terleme',
        'titreme', 'gaz', 'ateş', 'baş dönmesi', 'terleme'
    ],
    'Disease': [
        'grip', 'migren', 'kas ağrısı', 'mide virüsü', 'astım',
        'covid-19', 'gastrit', 'menenjit', 'vertigo', 'kalp krizi'
    ],
    'Severity': [
        'düşük', 'orta', 'düşük', 'orta', 'yüksek',
        'yüksek', 'orta', 'acil', 'orta', 'acil'
    ],
    'Department': [
        'Aile Hekimi', 'Nöroloji', 'Fizik Tedavi', 'Dahiliye', 'Göğüs Hastalıkları',
        'Enfeksiyon', 'Gastroenteroloji', 'Acil', 'Nöroloji', 'Acil'
    ],
    'Recommendation': [
        'Evde dinlenin ve bol sıvı tüketin',
        'Karanlık bir odada dinlenin ve tetikleyicilerden kaçının',
        'Sıcak uygulama yapın ve istirahat edin',
        'Diyet yapın ve bol su için',
        'İnhaler kullanın ve tetikleyicilerden uzak durun',
        'İzole olun ve doktora başvurun',
        'Asitli yiyeceklerden kaçının',
        'HEMEN 112yi ARAYIN',
        'Ani hareketlerden kaçının',
        'HEMEN 112yi ARAYIN'
    ],
    'Age_Risk': [
        '65 yaş üstü grip komplikasyonları riski',
        '35 yaş altı migren başlangıcı yaygın',
        '50 yaş üstü eklem problemleri riski',
        'Tüm yaş grupları',
        'Çocuklarda astım riski yüksek',
        'Kronik hastalığı olanlarda risk yüksek',
        'Tüm yaş grupları',
        'Çocuklarda risk yüksek',
        '60 yaş üstü risk yüksek',
        '45 yaş üstü risk yüksek'
    ],
    'Gender_Risk': [
        'Eşit risk',
        'Kadınlarda daha yaygın',
        'Eşit risk',
        'Eşit risk',
        'Çocukluk çağında erkeklerde daha yaygın',
        'Eşit risk',
        'Eşit risk',
        'Eşit risk',
        'Kadınlarda daha yaygın',
        'Erkeklerde daha yaygın'
    ],
    'Additional_Info': [
        'Kronik hastalık varsa dikkat',
        'Hormonal değişimlerden etkilenir',
        'Önceki yaralanmalar önemli',
        'Gıda alerjileri önemli',
        'Alerji öyküsü önemli',
        'Bağışıklık sistemi önemli',
        'Beslenme alışkanlıkları önemli',
        'Aşı geçmişi önemli',
        'İç kulak problemleri önemli',
        'Kalp hastalığı öyküsü önemli'
    ]
}

# DataFrame oluştur
df = pd.DataFrame(data)

# data klasörünü oluştur
os.makedirs('data', exist_ok=True)

# CSV dosyası olarak kaydet
df.to_csv('data/symptom_dataset.csv', index=False)
print("Genişletilmiş veri seti oluşturuldu: data/symptom_dataset.csv") 