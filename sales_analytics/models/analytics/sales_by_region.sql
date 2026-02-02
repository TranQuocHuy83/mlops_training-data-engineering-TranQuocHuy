{{ config(materialized='table') }}

SELECT
    region,
    COUNT(*) AS num_transactions,
    ROUND(SUM(total_sales)::NUMERIC, 2) AS total_revenue,
    ROUND(AVG(total_sales)::NUMERIC, 2) AS avg_sales
FROM {{ ref('stg_sales_data') }}
GROUP BY region
ORDER BY total_revenue DESC
