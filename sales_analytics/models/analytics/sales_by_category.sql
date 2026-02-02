{{ config(materialized='table') }}

SELECT
    category,
    COUNT(*) AS num_transactions,
    ROUND(SUM(total_sales)::NUMERIC, 2) AS total_revenue,
    ROUND(AVG(price)::NUMERIC, 2) AS avg_price,
    SUM(quantity_sold) AS total_quantity
FROM {{ ref('stg_sales_data') }}
GROUP BY category
ORDER BY total_revenue DESC
