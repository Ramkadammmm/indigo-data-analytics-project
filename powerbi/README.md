# IndiGo Power BI Analytics Data Model & DAX Metrics Guide

This guide outlines the Star Schema Data Model and DAX (Data Analysis Expressions) measures designed for Power BI Desktop & Power BI Service integration.

---

## 1. Power BI Data Model (Star Schema Architecture)

```
[ FactTable: flight_operations ] 1 ---- * [ FactTable: flight_surveys ]
           |
           | *
           1
  [ DimTable: routes ]
```

### Table Relationships
- `flight_operations.passenger_id` (1) ➔ `flight_surveys.passenger_id` (1) *(1:1 Relationship)*
- `flight_operations.origin` & `destination` ➔ `routes.origin_code` & `destination_code` *(Many:1 Relationship)*

---

## 2. Executive DAX Measures Library

### On-Time Performance (OTP %)
```dax
OTP_Percentage = 
DIVIDE(
    CALCULATE(COUNT(flight_operations[passenger_id]), flight_operations[arrival_delay_min] <= 15),
    COUNT(flight_operations[passenger_id]),
    0
) * 100
```

### Net Promoter Score (NPS)
```dax
NPS_Score = 
VAR TotalSurveys = COUNT(flight_surveys[survey_id])
VAR Promoters = CALCULATE(COUNT(flight_surveys[survey_id]), flight_surveys[nps_category] = "Promoter")
VAR Detractors = CALCULATE(COUNT(flight_surveys[survey_id]), flight_surveys[nps_category] = "Detractor")
RETURN
    DIVIDE((Promoters - Detractors), TotalSurveys, 0) * 100
```

### Total Passenger Revenue
```dax
Total_Revenue_INR = SUM(flight_operations[total_revenue_inr])
```

### Ancillary Revenue Share (%)
```dax
Ancillary_Share_Pct = 
DIVIDE(
    SUM(flight_operations[ancillary_revenue_inr]),
    SUM(flight_operations[total_revenue_inr]),
    0
) * 100
```

### Average Arrival Delay (Minutes)
```dax
Avg_Arrival_Delay = AVERAGE(flight_operations[arrival_delay_min])
```

---

## 3. Step-by-Step Power BI Setup Instructions

1. **Open Power BI Desktop**.
2. Click **Get Data** ➔ Select **ODBC** or **SQLite / Python Script Connector**.
3. Choose the SQLite database at `db/indigo_analytics.db` or import `data/raw/indigo_flight_passenger_data.csv`.
4. Load `flight_operations` and `flight_surveys` tables.
5. Create New Measures using the DAX formulas above.
6. Publish to **Power BI Service** for executive stakeholder access.
