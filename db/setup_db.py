import os
import sqlite3
import pandas as pd

def setup_database():
    db_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(db_dir)
    
    csv_path = os.path.join(project_dir, 'data', 'raw', 'indigo_flight_passenger_data.csv')
    db_path = os.path.join(db_dir, 'indigo_analytics.db')
    schema_path = os.path.join(db_dir, 'schema.sql')
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV data file not found at {csv_path}. Please run generate_indigo_data.py first.")
        
    print(f"Loading raw dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    df['delay_reason'] = df['delay_reason'].fillna('On Time / None')
    df['feedback_text'] = df['feedback_text'].fillna('')
    
    print(f"Connecting to SQLite database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Executing database schema setup...")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    
    # 1. Populate flight_operations table
    operations_cols = [
        'passenger_id', 'flight_id', 'flight_date', 'origin', 'destination',
        'is_international', 'fleet_type', 'cabin_class', 'booking_channel',
        'distance_km', 'base_fare_inr', 'ancillary_revenue_inr', 'total_revenue_inr',
        'departure_delay_min', 'arrival_delay_min', 'is_delayed', 'delay_reason'
    ]
    df_operations = df[operations_cols]
    df_operations.to_sql('flight_operations', conn, if_exists='append', index=False)
    print(f"Inserted {len(df_operations)} rows into 'flight_operations'.")
    
    # 2. Populate flight_surveys table
    survey_cols = [
        'passenger_id', 'checkin_rating', 'crew_rating', 'punctuality_rating',
        'cleanliness_rating', 'overall_satisfaction', 'nps_score', 'nps_category',
        'feedback_text', 'passenger_gender', 'passenger_age', 'travel_purpose'
    ]
    df_surveys = df[survey_cols]
    df_surveys.to_sql('flight_surveys', conn, if_exists='append', index=False)
    print(f"Inserted {len(df_surveys)} rows into 'flight_surveys'.")
    
    # Data Quality QA Checks
    print("\n--- Running Data Quality Assurance (QA) Audits ---")
    cursor.execute("SELECT COUNT(*) FROM flight_operations WHERE total_revenue_inr IS NULL OR total_revenue_inr <= 0")
    null_rev_count = cursor.fetchone()[0]
    print(f"[QA Check 1] Revenue Integrity (Null/Negative Revenue): {null_rev_count} violations")
    
    cursor.execute("SELECT COUNT(*) FROM flight_surveys WHERE nps_score NOT BETWEEN 0 AND 10")
    invalid_nps_count = cursor.fetchone()[0]
    print(f"[QA Check 2] NPS Range Validity (0 to 10): {invalid_nps_count} violations")
    
    cursor.execute("SELECT COUNT(DISTINCT passenger_id) FROM flight_operations")
    unique_pax = cursor.fetchone()[0]
    print(f"[QA Check 3] Passenger PNR Uniqueness: {unique_pax} unique PNRs out of {len(df)} total rows.")
    
    conn.commit()
    conn.close()
    print("\nDatabase initialization and QA checks completed successfully.")

if __name__ == '__main__':
    setup_database()
