{{ config(materialized='view') }}

SELECT
    id,
    product_name,
    category,
    price,
    quantity_sold,
    sale_date,
    region,
    (price * quantity_sold)::DECIMAL(10,2) AS total_sales
FROM {{ source('raw_data', 'sales_data') }}
WHERE sale_date IS NOT NULL
