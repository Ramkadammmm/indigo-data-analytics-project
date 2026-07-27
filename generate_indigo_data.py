import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_dataset(num_records=100000, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    
    print(f"Generating {num_records} realistic IndiGo flight & passenger records...")
    
    airports = {
        'DEL': 'Indira Gandhi International Airport, Delhi',
        'BOM': 'Chhatrapati Shivaji Maharaj International Airport, Mumbai',
        'BLR': 'Kempegowda International Airport, Bengaluru',
        'MAA': 'Chennai International Airport, Chennai',
        'CCU': 'Netaji Subhash Chandra Bose International Airport, Kolkata',
        'HYD': 'Rajiv Gandhi International Airport, Hyderabad',
        'AMD': 'Sardar Vallabhbhai Patel International Airport, Ahmedabad',
        'PNQ': 'Pune Airport, Pune',
        'COK': 'Cochin International Airport, Kochi',
        'DXB': 'Dubai International Airport, Dubai (International)',
        'SIN': 'Singapore Changi Airport, Singapore (International)',
        'BKK': 'Suvarnabhumi Airport, Bangkok (International)'
    }
    
    routes = [
        ('DEL', 'BOM'), ('DEL', 'BLR'), ('DEL', 'HYD'), ('BOM', 'BLR'),
        ('BOM', 'MAA'), ('BLR', 'CCU'), ('DEL', 'CCU'), ('HYD', 'BLR'),
        ('BOM', 'PNQ'), ('DEL', 'COK'), ('DEL', 'DXB'), ('BOM', 'DXB'),
        ('MAA', 'SIN'), ('DEL', 'BKK'), ('BOM', 'BKK')
    ]
    
    fleet_types = ['Airbus A320neo', 'Airbus A321neo', 'ATR 72-600']
    fleet_weights = [0.55, 0.35, 0.10]
    
    cabin_classes = ['Economy', 'IndiGo Stretch (Business)']
    cabin_weights = [0.92, 0.08]
    
    booking_channels = ['IndiGo App', 'IndiGo Website', 'OTA (MakeMyTrip/Yatra)', 'Travel Agent', 'Corporate Portal']
    channel_weights = [0.40, 0.30, 0.18, 0.07, 0.05]
    
    delay_causes = ['None', 'Weather', 'ATC Congestion', 'Late Arriving Aircraft', 'Maintenance', 'Baggage Handling']
    
    feedback_samples = {
        'positive': [
            "Flight was strictly on time. Excellent service by IndiGo cabin crew!",
            "Smooth check-in process at Gurgaon counter and seamless boarding.",
            "IndiGo Stretch seats were very comfortable. Highly recommended!",
            "Great value for money. Punctual departure and friendly staff.",
            "Clean aircraft, polite crew, and quick baggage retrieval."
        ],
        'neutral': [
            "Flight was acceptable. Minor delay of 15 mins due to ATC.",
            "Standard low-cost carrier experience. No complimentary snacks.",
            "Seat pitch was okay for a short domestic flight.",
            "Normal flight experience, nothing extraordinary.",
            "Average baggage waiting time at Mumbai airport."
        ],
        'negative': [
            "Severe flight delay over 2 hours without proper communication.",
            "Baggage was damaged upon arrival. Horrible experience.",
            "Long queue at airport check-in desk and unhelpful ground staff.",
            "Flight got rescheduled twice. Very frustrating for corporate travel.",
            "Seat cushion was uncomfortable and web check-in had technical glitches."
        ]
    }
    
    start_date = datetime(2025, 1, 1)
    
    records = []
    for i in range(1, num_records + 1):
        flight_id = f"6E-{random.randint(100, 9999)}"
        origin, dest = random.choice(routes)
        is_international = 1 if origin in ['DXB', 'SIN', 'BKK'] or dest in ['DXB', 'SIN', 'BKK'] else 0
        
        flight_date = start_date + timedelta(days=random.randint(0, 360), minutes=random.randint(0, 1440))
        fleet = np.random.choice(fleet_types, p=fleet_weights)
        cabin = np.random.choice(cabin_classes, p=cabin_weights)
        channel = np.random.choice(booking_channels, p=channel_weights)
        
        distance_km = random.randint(500, 3500) if is_international else random.randint(250, 1800)
        base_fare = round(distance_km * random.uniform(3.5, 6.0) + (1500 if cabin == 'IndiGo Stretch (Business)' else 0), 2)
        ancillary_revenue = round(random.choice([0, 250, 450, 750, 1200, 2500]), 2)
        
        # On-Time Performance (OTP)
        is_delayed = np.random.choice([0, 1], p=[0.82, 0.18])
        if is_delayed:
            departure_delay_min = int(np.random.exponential(scale=35) + 15)
            arrival_delay_min = departure_delay_min + random.randint(-10, 20)
            delay_reason = np.random.choice(delay_causes[1:], p=[0.25, 0.30, 0.25, 0.10, 0.10])
        else:
            departure_delay_min = random.randint(-5, 5)
            arrival_delay_min = random.randint(-10, 5)
            delay_reason = 'None'
            
        checkin_rating = random.randint(3, 5) if departure_delay_min <= 15 else random.randint(1, 4)
        crew_rating = random.randint(3, 5)
        punctuality_rating = 5 if arrival_delay_min <= 15 else (3 if arrival_delay_min <= 45 else random.randint(1, 2))
        cleanliness_rating = random.randint(3, 5)
        overall_satisfaction = round((checkin_rating * 0.2 + crew_rating * 0.3 + punctuality_rating * 0.35 + cleanliness_rating * 0.15), 1)
        
        if overall_satisfaction >= 4.2:
            nps_score = random.randint(9, 10)
            nps_category = 'Promoter'
            feedback_text = random.choice(feedback_samples['positive'])
        elif overall_satisfaction >= 3.2:
            nps_score = random.randint(7, 8)
            nps_category = 'Passive'
            feedback_text = random.choice(feedback_samples['neutral'])
        else:
            nps_score = random.randint(0, 6)
            nps_category = 'Detractor'
            feedback_text = random.choice(feedback_samples['negative'])
            
        passenger_id = f"PNR-{i:07d}"
        gender = random.choice(['Male', 'Female', 'Other'])
        age = random.randint(18, 70)
        travel_purpose = random.choice(['Leisure', 'Business', 'Visiting Friends/Relatives'])
        
        records.append({
            'passenger_id': passenger_id,
            'flight_id': flight_id,
            'flight_date': flight_date.strftime('%Y-%m-%d %H:%M:%S'),
            'origin': origin,
            'destination': dest,
            'is_international': is_international,
            'fleet_type': fleet,
            'cabin_class': cabin,
            'booking_channel': channel,
            'distance_km': distance_km,
            'base_fare_inr': base_fare,
            'ancillary_revenue_inr': ancillary_revenue,
            'total_revenue_inr': round(base_fare + ancillary_revenue, 2),
            'departure_delay_min': departure_delay_min,
            'arrival_delay_min': arrival_delay_min,
            'is_delayed': is_delayed,
            'delay_reason': delay_reason,
            'checkin_rating': checkin_rating,
            'crew_rating': crew_rating,
            'punctuality_rating': punctuality_rating,
            'cleanliness_rating': cleanliness_rating,
            'overall_satisfaction': overall_satisfaction,
            'nps_score': nps_score,
            'nps_category': nps_category,
            'feedback_text': feedback_text,
            'passenger_gender': gender,
            'passenger_age': age,
            'travel_purpose': travel_purpose
        })
        
    df = pd.DataFrame(records)
    
    output_dir = os.path.join(os.getcwd(), 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, 'indigo_flight_passenger_data.csv')
    df.to_csv(file_path, index=False)
    print(f"Dataset generated successfully at: {file_path}")
    print(f"Dataset shape: {df.shape}")
    return file_path

if __name__ == '__main__':
    project_root = r"C:\Users\Lenovo\.gemini\antigravity\scratch\indigo_data_analytics_project"
    os.makedirs(project_root, exist_ok=True)
    os.chdir(project_root)
    generate_dataset(num_records=100000)
