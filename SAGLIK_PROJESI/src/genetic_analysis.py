class GeneticAnalysis:
    def __init__(self):
        self.genetic_risk_factors = {
            'diyabet': ['tip1_diyabet', 'tip2_diyabet'],
            'kalp_hastaliklari': ['koroner_arter', 'hipertansiyon'],
            'kanser': ['meme_kanseri', 'kolon_kanseri'],
            'norolojik': ['alzheimer', 'parkinson']
        }
        
        self.drug_genetic_interactions = {
            'warfarin': ['CYP2C9', 'VKORC1'],
            'clopidogrel': ['CYP2C19'],
            'simvastatin': ['SLCO1B1'],
            'codeine': ['CYP2D6']
        }
    
    def analyze_family_history(self, family_history):
        risk_scores = {}
        for disease, relatives in family_history.items():
            if disease in self.genetic_risk_factors:
                # Birinci derece akrabalar için risk puanı hesapla
                first_degree = len([r for r in relatives if r['degree'] == 1])
                # İkinci derece akrabalar için risk puanı hesapla
                second_degree = len([r for r in relatives if r['degree'] == 2])
                
                risk_score = (first_degree * 0.5 + second_degree * 0.25) / len(relatives)
                risk_scores[disease] = risk_score
        
        return risk_scores
    
    def check_drug_interactions(self, genetic_profile, medications):
        warnings = []
        for drug in medications:
            if drug in self.drug_genetic_interactions:
                relevant_genes = self.drug_genetic_interactions[drug]
                for gene in relevant_genes:
                    if gene in genetic_profile:
                        if genetic_profile[gene] == 'poor_metabolizer':
                            warnings.append(f"⚠️ {drug} için genetik risk: {gene} geni zayıf metabolize edici.")
                        elif genetic_profile[gene] == 'rapid_metabolizer':
                            warnings.append(f"⚠️ {drug} için genetik risk: {gene} geni hızlı metabolize edici.")
        
        return warnings
    
    def get_personalized_recommendations(self, genetic_risks, lifestyle_factors):
        recommendations = []
        
        for disease, risk in genetic_risks.items():
            if risk > 0.5:
                recommendations.append({
                    'disease': disease,
                    'risk_level': 'Yüksek',
                    'screening': self.get_screening_recommendations(disease),
                    'prevention': self.get_prevention_recommendations(disease, lifestyle_factors)
                })
            elif risk > 0.3:
                recommendations.append({
                    'disease': disease,
                    'risk_level': 'Orta',
                    'screening': self.get_screening_recommendations(disease),
                    'prevention': self.get_prevention_recommendations(disease, lifestyle_factors)
                })
        
        return recommendations
    
    def get_screening_recommendations(self, disease):
        screening_guidelines = {
            'diyabet': 'Yılda bir HbA1c testi',
            'kalp_hastaliklari': 'Yılda bir lipid profili',
            'kanser': 'Yaşa ve cinsiyete uygun tarama testleri',
            'norolojik': 'Düzenli nörolojik muayene'
        }
        return screening_guidelines.get(disease, 'Doktorunuza danışın')
    
    def get_prevention_recommendations(self, disease, lifestyle_factors):
        prevention_strategies = {
            'diyabet': ['Düzenli egzersiz', 'Şeker tüketimini sınırlama'],
            'kalp_hastaliklari': ['Düşük tuzlu diyet', 'Düzenli kardiyovasküler egzersiz'],
            'kanser': ['Sigarayı bırakma', 'Alkol tüketimini sınırlama'],
            'norolojik': ['Zihinsel aktiviteler', 'Omega-3 açısından zengin beslenme']
        }
        return prevention_strategies.get(disease, ['Sağlıklı yaşam tarzını sürdürün']) 