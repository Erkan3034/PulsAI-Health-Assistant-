import pandas as pd

class PsychologicalSupport:
    def __init__(self):
        self.support_data = pd.DataFrame(columns=['symptom', 'psychological_effect', 'support_type'])

    def analyze_symptom_effects(self, symptoms):
        """Semptomların psikolojik etkilerini analiz et"""
        effects = {}
        for symptom in symptoms:
            if symptom in ['depresyon', 'anksiyete']:
                effects[symptom] = "Bu belirtiler psikolojik stresin bir göstergesi olabilir."
            # Diğer belirtiler için analiz ekleyin
        return effects

    def provide_emotional_support(self, psychological_effects):
        """Duygusal destek önerileri sun"""
        recommendations = []
        for effect in psychological_effects:
            if effect == 'depresyon':
                recommendations.append("Düzenli egzersiz yapmayı deneyin.")
            elif effect == 'anksiyete':
                recommendations.append("Meditasyon veya derin nefes alma tekniklerini uygulayın.")
            # Diğer öneriler ekleyin
        return recommendations