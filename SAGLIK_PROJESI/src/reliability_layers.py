class ReliabilityLayers:
    def __init__(self):
        self.accuracy_data = {}

    def add_accuracy_data(self, model_name, accuracy):
        """Tanı doğruluk oranı ekle"""
        self.accuracy_data[model_name] = accuracy

    def get_accuracy_report(self):
        """Doğruluk raporunu döndür"""
        return self.accuracy_data 