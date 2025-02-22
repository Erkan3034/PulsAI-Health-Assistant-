import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class AdvancedMedicalModel:
    def __init__(self):
        self.models = {
            'diagnosis': RandomForestClassifier(n_estimators=200, random_state=42),
            'severity': RandomForestClassifier(n_estimators=150, random_state=42),
            'department': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        self.best_models = {}
        self.feature_importance = {}
    
    def train_models(self, X, y, model_type):
        """Belirli bir tahmin türü için modeli eğitir"""
        print(f"\nTraining {model_type} model...")
        model = self.models[model_type]
        
        # Modeli eğit
        model.fit(X, y)
        
        # Eğitim skoru
        train_score = model.score(X, y)
        print(f"Training score: {train_score:.4f}")
        
        self.best_models[model_type] = model
        self.feature_importance[model_type] = model.feature_importances_
        
        return train_score
    
    def predict(self, X, model_type):
        """Tahmin yapar"""
        if model_type not in self.best_models:
            raise ValueError(f"Model {model_type} not trained yet!")
        return self.best_models[model_type].predict(X)
    
    def predict_proba(self, X, model_type):
        """Tahmin olasılıklarını döndürür"""
        if model_type not in self.best_models:
            raise ValueError(f"Model {model_type} not trained yet!")
        return self.best_models[model_type].predict_proba(X)
    
    def save_models(self):
        """Eğitilmiş modelleri kaydet"""
        os.makedirs('models', exist_ok=True)
        for model_type, model in self.best_models.items():
            joblib.dump(model, f'models/{model_type}_model.pkl')
        
        if self.feature_importance:
            np.save('models/feature_importance.npy', self.feature_importance)
    
    def load_models(self):
        """Kaydedilmiş modelleri yükle"""
        try:
            for model_type in ['diagnosis', 'severity', 'department']:
                model_path = f'models/{model_type}_model.pkl'
                if os.path.exists(model_path):
                    self.best_models[model_type] = joblib.load(model_path)
                else:
                    print(f"Warning: Model file {model_path} not found!")
        except Exception as e:
            print(f"Error loading models: {str(e)}")

def prepare_features(df):
    """Özellik matrisini hazırla"""
    # Belirti sütunlarını seç
    symptom_cols = [col for col in df.columns if col.startswith('symptom_')]
    
    # Kronik hastalık sütunlarını seç
    chronic_cols = [col for col in df.columns if col.startswith('chronic_')]
    
    # Temel özellikler
    feature_cols = symptom_cols + ['age', 'gender_encoded'] + chronic_cols
    
    return df[feature_cols]

def train_and_evaluate():
    """Ana eğitim ve değerlendirme fonksiyonu"""
    try:
        # Veriyi yükle
        print("Veri yükleniyor...")
        processed_df = pd.read_csv('data/processed_medical_dataset.csv')
        
        # Özellik matrisini hazırla
        print("Özellikler hazırlanıyor...")
        X = prepare_features(processed_df).values
        
        # Hedef değişkenler
        y_diagnosis = processed_df['diagnosis_encoded'].values
        y_severity = processed_df['severity_encoded'].values
        y_department = processed_df['department_encoded'].values
        
        # Model nesnesini oluştur
        print("Model eğitimi başlıyor...")
        medical_model = AdvancedMedicalModel()
        
        # Veriyi böl
        X_train, X_test, y_train_dict, y_test_dict = {}, {}, {}, {}
        for target, y in [('diagnosis', y_diagnosis), 
                         ('severity', y_severity), 
                         ('department', y_department)]:
            X_train[target], X_test[target], y_train_dict[target], y_test_dict[target] = \
                train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Her hedef için modelleri eğit ve değerlendir
        for target in ['diagnosis', 'severity', 'department']:
            print(f"\nTraining models for {target}...")
            train_score = medical_model.train_models(
                X_train[target], 
                y_train_dict[target], 
                target
            )
            print(f"Training score for {target}: {train_score:.4f}")
            
            # Test seti üzerinde değerlendir
            y_pred = medical_model.predict(X_test[target], target)
            print(f"\n{target.upper()} Model Evaluation:")
            print("Test Accuracy:", accuracy_score(y_test_dict[target], y_pred))
            print("\nClassification Report:")
            print(classification_report(y_test_dict[target], y_pred))
        
        # Modelleri kaydet
        medical_model.save_models()
        print("\nModels have been saved successfully!")
        
        return medical_model
        
    except Exception as e:
        print(f"Error in training: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    trained_model = train_and_evaluate()