import pandas as pd
from datetime import datetime
import plotly.express as px

class HealthStatistics:
    def __init__(self):
        self.stats_file = 'data/health_statistics.csv'
        try:
            self.df = pd.read_csv(self.stats_file)
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=[
                'date', 'disease', 'severity', 'age', 'gender', 
                'feedback', 'accuracy'
            ])
    
    def add_record(self, data):
        new_record = pd.DataFrame([{
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'disease': data['disease'],
            'severity': data['severity'],
            'age': data['age'],
            'gender': data['gender'],
            'feedback': data['feedback'],
            'accuracy': data['accuracy']
        }])
        self.df = pd.concat([self.df, new_record], ignore_index=True)
        self.df.to_csv(self.stats_file, index=False)
    
    def get_weekly_stats(self):
        self.df['date'] = pd.to_datetime(self.df['date'])
        weekly = self.df[self.df['date'] > pd.Timestamp.now() - pd.Timedelta(days=7)]
        return weekly['disease'].value_counts()
    
    def generate_insights(self):
        fig = px.box(self.df, x='disease', y='age', 
                    title='Yaş Gruplarına Göre Hastalık Dağılımı')
        fig.update_layout(xaxis_title="Hastalık",
                         yaxis_title="Yaş")
        return fig 