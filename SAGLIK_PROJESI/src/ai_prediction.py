import numpy as np

class AIPrediction:
    def __init__(self, model):
        self.model = model

    def predict_disease_probability(self, features):
        """Hastalık gelişim olasılığını tahmin et"""
        probability = self.model.predict_proba(features.reshape(1, -1), 'diagnosis')
        return probability

    def early_warning_system(self, probability):
        """Erken uyarı sistemi"""
        # probability bir dizi olduğu için, en yüksek olasılığı alıyoruz
        max_probability = np.max(probability)
        
        if max_probability > 0.7:
            return "Yüksek risk! Hemen bir doktora başvurun."
        elif max_probability > 0.4:
            return "Orta risk! Kontrol önerilir."
        else:
            return "Düşük risk. Sağlıklı yaşam tarzına devam edin." 