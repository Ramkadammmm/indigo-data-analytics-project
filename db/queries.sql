-- ====================================================================
-- IndiGo Data Analytics - Executive SQL Queries Suite
-- Purpose: Advanced Data Extraction, Operations KPI Calculation, NPS Audit
-- ====================================================================

-- 1. Executive Summary KPI Query: Route-Level On-Time Performance (OTP) & Revenue Yield
WITH RouteSummary AS (
    SELECT 
        origin || '-' || destination AS route,
        COUNT(passenger_id) AS total_passengers,
        SUM(total_revenue_inr) AS total_revenue_inr,
        AVG(total_revenue_inr) AS avg_rev_per_pax,
        AVG(arrival_delay_min) AS avg_arrival_delay_min,
        SUM(CASE WHEN arrival_delay_min <= 15 THEN 1 ELSE 0 END) * 100.0 / COUNT(passenger_id) AS otp_percentage
    FROM flight_operations
    GROUP BY origin, destination
)
SELECT 
    route,
    total_passengers,
    ROUND(total_revenue_inr, 2) AS total_revenue_inr,
    ROUND(avg_rev_per_pax, 2) AS avg_rev_per_pax,
    ROUND(avg_arrival_delay_min, 1) AS avg_arrival_delay_min,
    ROUND(otp_percentage, 2) AS otp_percentage
FROM RouteSummary
ORDER BY total_revenue_inr DESC;


-- 2. Net Promoter Score (NPS) Audit & Breakdown by Fleet & Cabin Class
WITH NPS_Counts AS (
    SELECT 
        fo.fleet_type,
        fo.cabin_class,
        COUNT(fs.survey_id) AS total_surveys,
        SUM(CASE WHEN fs.nps_category = 'Promoter' THEN 1 ELSE 0 END) AS promoters,
        SUM(CASE WHEN fs.nps_category = 'Passive' THEN 1 ELSE 0 END) AS passives,
        SUM(CASE WHEN fs.nps_category = 'Detractor' THEN 1 ELSE 0 END) AS detractors
    FROM flight_operations fo
    JOIN flight_surveys fs ON fo.passenger_id = fs.passenger_id
    GROUP BY fo.fleet_type, fo.cabin_class
)
SELECT 
    fleet_type,
    cabin_class,
    total_surveys,
    promoters,
    passives,
    detractors,
    ROUND(((promoters - detractors) * 100.0 / total_surveys), 2) AS net_promoter_score
FROM NPS_Counts
ORDER BY net_promoter_score DESC;


-- 3. Window Function Query: Ranking Delay Causes by Average Arrival Delay per Booking Channel
WITH DelayRanking AS (
    SELECT 
        booking_channel,
        delay_reason,
        COUNT(*) AS occurrence_count,
        AVG(arrival_delay_min) AS avg_delay_min,
        RANK() OVER (PARTITION BY booking_channel ORDER BY AVG(arrival_delay_min) DESC) as delay_rank
    FROM flight_operations
    WHERE is_delayed = 1
    GROUP BY booking_channel, delay_reason
)
SELECT 
    booking_channel,
    delay_reason,
    occurrence_count,
    ROUND(avg_delay_min, 2) AS avg_delay_min,
    delay_rank
FROM DelayRanking
WHERE delay_rank <= 3;


-- 4. Monthly Trend & Cumulative Revenue Analysis (Window Functions)
WITH MonthlyMetrics AS (
    SELECT 
        strftime('%Y-%m', flight_date) AS yr_month,
        COUNT(passenger_id) AS pax_count,
        SUM(total_revenue_inr) AS monthly_revenue
    FROM flight_operations
    GROUP BY strftime('%Y-%m', flight_date)
)
SELECT 
    yr_month,
    pax_count,
    ROUND(monthly_revenue, 2) AS monthly_revenue,
    ROUND(SUM(monthly_revenue) OVER (ORDER BY yr_month), 2) AS cumulative_ytd_revenue,
    ROUND(AVG(monthly_revenue) OVER (ORDER BY yr_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS 3_month_moving_avg
FROM MonthlyMetrics
ORDER BY yr_month;
