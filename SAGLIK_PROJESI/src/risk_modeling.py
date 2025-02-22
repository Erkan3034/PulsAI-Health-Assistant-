import numpy as np

class RiskModeling:
    def __init__(self):
        self.genetic_factors = {}
        self.lifestyle_factors = {}

    def analyze_genetic_history(self, family_history):
        """Genetik geçmiş analizi yap"""
        # Örnek veriler
        self.genetic_factors = {
            'diabetes': 0.8 if 'diabetes' in family_history else 0.2,
            'heart_disease': 0.7 if 'heart_disease' in family_history else 0.3
        }

    def calculate_lifestyle_risk(self, lifestyle_choices):
        """Yaşam tarzı faktörlerini hesapla"""
        self.lifestyle_factors = {
            'smoking': 0.9 if lifestyle_choices.get('smoking') else 0.1,
            'exercise': 0.2 if lifestyle_choices.get('exercise') else 0.8
        }

    def dynamic_risk_score(self):
        """Dinamik risk skoru hesapla"""
        risk_score = np.mean(list(self.genetic_factors.values()) + list(self.lifestyle_factors.values()))
        return risk_score 