-- IndiGo Executive Data Analytics Database Schema
-- Database Engine: SQLite / PostgreSQL compatible

DROP TABLE IF EXISTS flight_surveys;
DROP TABLE IF EXISTS flight_operations;
DROP TABLE IF EXISTS routes;

CREATE TABLE routes (
    origin_code VARCHAR(5) NOT NULL,
    destination_code VARCHAR(5) NOT NULL,
    distance_km INT NOT NULL,
    is_international INT DEFAULT 0,
    PRIMARY KEY (origin_code, destination_code)
);

CREATE TABLE flight_operations (
    passenger_id VARCHAR(20) PRIMARY KEY,
    flight_id VARCHAR(15) NOT NULL,
    flight_date DATETIME NOT NULL,
    origin VARCHAR(5) NOT NULL,
    destination VARCHAR(5) NOT NULL,
    is_international INT NOT NULL,
    fleet_type VARCHAR(30) NOT NULL,
    cabin_class VARCHAR(30) NOT NULL,
    booking_channel VARCHAR(40) NOT NULL,
    distance_km INT NOT NULL,
    base_fare_inr DECIMAL(10,2) NOT NULL,
    ancillary_revenue_inr DECIMAL(10,2) NOT NULL,
    total_revenue_inr DECIMAL(10,2) NOT NULL,
    departure_delay_min INT NOT NULL,
    arrival_delay_min INT NOT NULL,
    is_delayed INT NOT NULL,
    delay_reason VARCHAR(50) NOT NULL
);

CREATE TABLE flight_surveys (
    survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_id VARCHAR(20) NOT NULL,
    checkin_rating INT NOT NULL,
    crew_rating INT NOT NULL,
    punctuality_rating INT NOT NULL,
    cleanliness_rating INT NOT NULL,
    overall_satisfaction DECIMAL(3,1) NOT NULL,
    nps_score INT NOT NULL,
    nps_category VARCHAR(15) NOT NULL,
    feedback_text TEXT,
    passenger_gender VARCHAR(10),
    passenger_age INT,
    travel_purpose VARCHAR(30),
    FOREIGN KEY (passenger_id) REFERENCES flight_operations(passenger_id)
);

-- Indexes for Query Performance & Analytical Optimization
CREATE INDEX idx_flight_date ON flight_operations(flight_date);
CREATE INDEX idx_origin_dest ON flight_operations(origin, destination);
CREATE INDEX idx_nps_category ON flight_surveys(nps_category);
CREATE INDEX idx_delay_reason ON flight_operations(delay_reason);
