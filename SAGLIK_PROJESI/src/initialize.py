import pandas as pd
from model import veri_hazirlama

def main():
    try:
        print("Model eğitimi başlıyor...")
        
        # Modeli eğit ve kaydet
        # 4 değer döndürdüğü için 4 değişken tanımlıyoruz
        disease_model, severity_model, vectorizer, reference_data = veri_hazirlama()
        print("Model başarıyla oluşturuldu ve kaydedildi!")
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    main() 