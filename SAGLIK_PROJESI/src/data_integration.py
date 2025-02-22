import pandas as pd

class DataIntegration:
    def __init__(self):
        self.wearable_data = pd.DataFrame()
        self.genetic_data = pd.DataFrame()

    def integrate_wearable_data(self, data):
        """Wearable cihazlardan veri entegrasyonu"""
        self.wearable_data = pd.DataFrame(data)

    def integrate_genetic_data(self, data):
        """Genetik test sonuçları entegrasyonu"""
        self.genetic_data = pd.DataFrame(data)

    def get_combined_data(self):
        """Kombine veri setini döndür"""
        return pd.concat([self.wearable_data, self.genetic_data], axis=1) 