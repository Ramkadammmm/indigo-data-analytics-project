import os
import sqlite3
import pandas as pd
import numpy as np

class IndigoDataLoader:
    def __init__(self, db_path=None, csv_path=None):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(project_root, 'db', 'indigo_analytics.db')
        self.csv_path = csv_path or os.path.join(project_root, 'data', 'raw', 'indigo_flight_passenger_data.csv')

    def load_from_db(self):
        """Extract merged flight operations and survey dataset from SQLite DB using SQL JOIN."""
        if not os.path.exists(self.db_path):
            print(f"DB not found at {self.db_path}. Falling back to CSV...")
            return self.load_from_csv()
            
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT 
            fo.passenger_id, fo.flight_id, fo.flight_date, fo.origin, fo.destination,
            fo.is_international, fo.fleet_type, fo.cabin_class, fo.booking_channel,
            fo.distance_km, fo.base_fare_inr, fo.ancillary_revenue_inr, fo.total_revenue_inr,
            fo.departure_delay_min, fo.arrival_delay_min, fo.is_delayed, fo.delay_reason,
            fs.checkin_rating, fs.crew_rating, fs.punctuality_rating, fs.cleanliness_rating,
            fs.overall_satisfaction, fs.nps_score, fs.nps_category, fs.feedback_text,
            fs.passenger_gender, fs.passenger_age, fs.travel_purpose
        FROM flight_operations fo
        JOIN flight_surveys fs ON fo.passenger_id = fs.passenger_id
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return self._preprocess(df)

    def load_from_csv(self):
        df = pd.read_csv(self.csv_path)
        return self._preprocess(df)

    def _preprocess(self, df):
        """Data cleaning & Feature Engineering."""
        df['flight_date'] = pd.to_datetime(df['flight_date'])
        df['month'] = df['flight_date'].dt.strftime('%Y-%m')
        df['day_of_week'] = df['flight_date'].dt.day_name()
        df['route'] = df['origin'] + '-' + df['destination']
        df['ancillary_ratio'] = np.where(df['total_revenue_inr'] > 0, df['ancillary_revenue_inr'] / df['total_revenue_inr'], 0)
        df['is_detractor'] = np.where(df['nps_category'] == 'Detractor', 1, 0)
        df['is_promoter'] = np.where(df['nps_category'] == 'Promoter', 1, 0)
        return df

if __name__ == '__main__':
    loader = IndigoDataLoader()
    df = loader.load_from_db()
    print(f"Data Loaded Successfully: {df.shape[0]} rows, {df.shape[1]} columns.")
