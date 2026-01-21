# Data Engineering Exercise: Airflow, PostgreSQL & dbt

## Project Overview

This exercise demonstrates a simple data pipeline using Apache Airflow, PostgreSQL, and dbt. You'll build an ETL workflow that:
1. **Extracts** sample data from a CSV file
2. **Loads** it into PostgreSQL
3. **Transforms** it using dbt

**Learning Objectives:**
- Understand Airflow DAG structure
- Write basic SQL and dbt models
- Orchestrate a simple pipeline
- Connect tools together

---

## Prerequisites

### Step 1: Open Command Prompt (cmd) or PowerShell

All commands in this guide use Windows Command Prompt (`cmd`). You can also use PowerShell if you prefer.

### Option 1: Using UV (Recommended - Faster & Cleaner)

If you don't have UV installed:
```cmd
pip install uv
```

Create and activate UV virtual environment:
```cmd
uv venv venv
venv\Scripts\activate
```

Install dependencies using UV:
```cmd
uv pip install apache-airflow apache-airflow-providers-postgres dbt-postgres pandas psycopg2-binary
```

### Option 2: Using venv (Built-in Python)

Create virtual environment:
```cmd
python -m venv venv
venv\Scripts\activate
```

Install dependencies using pip:
```cmd
pip install apache-airflow apache-airflow-providers-postgres
pip install dbt-postgres
pip install pandas psycopg2-binary
```

**To save dependencies to a file for reproducibility:**
```cmd
pip freeze > requirements.txt
```

**To install from requirements.txt later:**
```cmd
pip install -r requirements.txt
```

**Clean up (when done with the project):**
```cmd
deactivate
rmdir /s /q venv
```

Or simply open File Explorer and delete the `venv` folder manually.

### Why Use Virtual Environments?

| Benefit | Explanation |
|---------|-------------|
| **Isolation** | Dependencies don't affect your system or other projects |
| **Clean Removal** | Simply delete the `venv` folder to remove everything |
| **Reproducibility** | `requirements.txt` lets you recreate the same environment anytime |
| **Compatibility** | Different projects can use different versions of the same package |

---

**Ensure PostgreSQL is running on your local machine (default: localhost:5432)**

Check if PostgreSQL is running:
- Open Task Manager (Ctrl + Shift + Esc)
- Look for `postgres.exe` or `pg_ctl.exe`
- Or use: `psql -U postgres -c "SELECT version();"`

---

## Step 2: Setup PostgreSQL Database

### Create Database and Schema

Open Command Prompt and connect to PostgreSQL:
```cmd
psql -U postgres
```

Then run these SQL commands:

```sql
-- Create database
CREATE DATABASE data_engineering_exercise;

-- Connect to the database
\c data_engineering_exercise

-- Create raw schema for ingested data
CREATE SCHEMA raw;

-- Create staging schema for dbt models
CREATE SCHEMA staging;

-- Create analytics schema for final models
CREATE SCHEMA analytics;

-- Create a simple raw table
CREATE TABLE raw.sales_data (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2),
    quantity_sold INTEGER,
    sale_date DATE,
    region VARCHAR(50)
);
```

Type `\q` to exit psql:
```sql
\q
```

---

## Step 3: Prepare Sample Data (CSV File)

Create a file named `sales_sample.csv` in your project directory (e.g., `C:\Users\YourName\data-engineering-project\`):

```csv
product_name,category,price,quantity_sold,sale_date,region
Laptop,Electronics,1200.00,5,2024-01-15,North
Mouse,Electronics,25.00,50,2024-01-15,South
Monitor,Electronics,350.00,10,2024-01-16,West
Keyboard,Electronics,80.00,30,2024-01-16,East
Desk,Furniture,150.00,8,2024-01-17,North
Chair,Furniture,120.00,12,2024-01-17,South
Lamp,Furniture,45.00,25,2024-01-18,West
Notebook,Supplies,5.00,200,2024-01-18,East
Pen,Supplies,2.00,500,2024-01-19,North
```

**How to create the CSV file:**
1. Open Notepad
2. Paste the CSV content above
3. Save as `sales_sample.csv` (use "All Files" format, not .txt)
4. Save in your project folder

---

## Step 4: Create Airflow DAG

Create folder structure:
```cmd
mkdir airflow\dags
```

Create a file `airflow\dags\sales_pipeline.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import pandas as pd
import psycopg2
import os

# Default DAG arguments
default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'sales_data_pipeline',
    default_args=default_args,
    description='Basic ETL pipeline with dbt transformation',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 15),
    catchup=False,
)

# Task 1: Load CSV to PostgreSQL
def load_csv_to_postgres():
    """Load CSV file to raw.sales_data table"""
    # Change this path to your actual CSV location
    csv_path = r'C:\Users\YourName\data-engineering-project\sales_sample.csv'
    
    df = pd.read_csv(csv_path)
    
    conn = psycopg2.connect(
        host='localhost',
        database='data_engineering_exercise',
        user='postgres',
        password='your_password',  # Change this to your PostgreSQL password
        port=5432
    )
    
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        insert_query = """
        INSERT INTO raw.sales_data 
        (product_name, category, price, quantity_sold, sale_date, region)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, tuple(row))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loaded {len(df)} rows to PostgreSQL")

# Define Tasks
load_task = PythonOperator(
    task_id='load_csv_to_postgres',
    python_callable=load_csv_to_postgres,
    dag=dag,
)

# Task 2: Run dbt models
dbt_run_task = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd C:\\Users\\YourName\\data-engineering-project\\sales_analytics && dbt run --profiles-dir .',
    dag=dag,
)

# Task 3: Run dbt tests (optional)
dbt_test_task = BashOperator(
    task_id='run_dbt_tests',
    bash_command='cd C:\\Users\\YourName\\data-engineering-project\\sales_analytics && dbt test --profiles-dir .',
    dag=dag,
)

# Set task dependencies
load_task >> dbt_run_task >> dbt_test_task
```

**Important:** Replace `C:\Users\YourName\data-engineering-project\` with your actual project path.

---

## Step 5: Setup dbt Project

### Initialize dbt Project

In Command Prompt, navigate to your project directory:
```cmd
cd C:\Users\YourName\data-engineering-project
```

Make sure your virtual environment is activated:
```cmd
venv\Scripts\activate
```

Then initialize dbt:
```cmd
dbt init sales_analytics
cd sales_analytics
```

### Configure `profiles.yml`

Find your `.dbt` folder location:
```cmd
echo %USERPROFILE%\.dbt
```

This typically expands to: `C:\Users\YourName\.dbt`

Create or edit `profiles.yml` in that folder:

```yaml
sales_analytics:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: postgres
      password: your_password
      port: 5432
      dbname: data_engineering_exercise
      schema: staging
      threads: 4
      keepalives_idle: 0
```

### Create dbt Models

#### File: `models\staging\stg_sales_data.sql`

```sql
{{ config(
    materialized='view'
) }}

SELECT
    id,
    product_name,
    category,
    price,
    quantity_sold,
    sale_date,
    region,
    CAST(price * quantity_sold AS DECIMAL(10, 2)) AS total_sales
FROM {{ source('raw_data', 'sales_data') }}
WHERE sale_date IS NOT NULL
```

#### File: `models\analytics\sales_by_category.sql`

```sql
{{ config(
    materialized='table'
) }}

SELECT
    category,
    COUNT(DISTINCT id) AS num_products,
    ROUND(SUM(total_sales)::NUMERIC, 2) AS total_revenue,
    ROUND(AVG(price)::NUMERIC, 2) AS avg_price,
    SUM(quantity_sold) AS total_quantity
FROM {{ ref('stg_sales_data') }}
GROUP BY category
ORDER BY total_revenue DESC
```

#### File: `models\analytics\sales_by_region.sql`

```sql
{{ config(
    materialized='table'
) }}

SELECT
    region,
    COUNT(DISTINCT id) AS num_transactions,
    ROUND(SUM(total_sales)::NUMERIC, 2) AS total_revenue,
    ROUND(AVG(total_sales)::NUMERIC, 2) AS avg_sales
FROM {{ ref('stg_sales_data') }}
GROUP BY region
ORDER BY total_revenue DESC
```

### Create `sources.yml`

File: `models\sources.yml`

```yaml
version: 2

sources:
  - name: raw_data
    description: Raw data from CSV ingestion
    database: data_engineering_exercise
    schema: raw
    tables:
      - name: sales_data
        description: Raw sales transactions
        columns:
          - name: id
            description: Primary key
          - name: product_name
            description: Product name
          - name: category
            description: Product category
          - name: price
            description: Unit price
          - name: quantity_sold
            description: Quantity sold
          - name: sale_date
            description: Date of sale
          - name: region
            description: Geographic region
```

### Create `schema.yml` for Tests

File: `models\schema.yml`

```yaml
version: 2

models:
  - name: stg_sales_data
    description: Staging layer for sales data
    columns:
      - name: id
        description: Product ID
        tests:
          - unique
          - not_null

  - name: sales_by_category
    description: Sales aggregated by product category
    columns:
      - name: category
        description: Product category
        tests:
          - not_null
```

---

## Step 6: Running the Pipeline

### Step 6.1: Test dbt Models Locally

Open Command Prompt and navigate to your dbt project:
```cmd
cd C:\Users\YourName\data-engineering-project\sales_analytics
venv\Scripts\activate
```

Parse the project:
```cmd
dbt parse
```

Run models:
```cmd
dbt run
```

Run tests:
```cmd
dbt test
```

Generate documentation:
```cmd
dbt docs generate
dbt docs serve
```

This will open documentation in your browser at `http://localhost:8000`

### Step 6.2: Start Airflow

Open Command Prompt (if not already in virtual environment):
```cmd
cd C:\Users\YourName\data-engineering-project
venv\Scripts\activate
```

Initialize Airflow database:
```cmd
airflow db init
```

Create an admin user:
```cmd
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

Start Airflow scheduler (open a new Command Prompt window):
```cmd
set AIRFLOW_HOME=C:\Users\YourName\data-engineering-project
airflow scheduler
```

Start Airflow webserver (open another new Command Prompt window):
```cmd
set AIRFLOW_HOME=C:\Users\YourName\data-engineering-project
airflow webserver --port 8080
```

### Step 6.3: Trigger the DAG

1. Open browser and go to `http://localhost:8080`
2. Login with credentials: **admin / admin**
3. Find `sales_data_pipeline` DAG
4. Click the play button to trigger
5. Monitor execution in the UI

---

## Step 7: Verify Results

After the DAG completes successfully, open Command Prompt and connect to PostgreSQL:
```cmd
psql -U postgres -d data_engineering_exercise
```

Query the results:

```sql
-- Check staging data
SELECT * FROM staging.stg_sales_data LIMIT 10;

-- Check sales by category
SELECT * FROM analytics.sales_by_category;

-- Check sales by region
SELECT * FROM analytics.sales_by_region;
```

Expected output for `sales_by_category`:
```
 category   | num_products | total_revenue | avg_price | total_quantity
------------|--------------|---------------|-----------|----------------
 Supplies   |      2       |    1100.00    |    3.50   |      700
 Electronics|      5       |    8590.00    |   355.00  |       95
 Furniture  |      3       |     677.00    |   105.00  |       45
```

Exit psql:
```sql
\q
```

---

## Troubleshooting

### PostgreSQL Connection Error
- Check if PostgreSQL is running (look in Task Manager)
- Verify credentials in your Airflow DAG and dbt profiles.yml
- Try connecting manually: `psql -U postgres`

### "Module not found" errors
- Make sure virtual environment is activated: `venv\Scripts\activate`
- Install missing packages: `pip install [package_name]`

### dbt Model Not Running
- Verify `profiles.yml` exists in `C:\Users\YourName\.dbt`
- Check dbt project path in BashOperator is correct
- Test manually: `dbt run` from your dbt project folder

### CSV File Not Found
- Use absolute path like: `r'C:\Users\YourName\data-engineering-project\sales_sample.csv'`
- Make sure file exists and is named exactly as specified

### Permission Denied for Insert
- Ensure PostgreSQL user has INSERT permissions:
  ```sql
  GRANT ALL PRIVILEGES ON SCHEMA raw TO postgres;
  GRANT ALL PRIVILEGES ON raw.sales_data TO postgres;
  ```

### Virtual Environment Issues
- **Can't find command `activate`?** Use: `venv\Scripts\activate.bat`
- **Packages not found?** Check if `(venv)` appears in your Command Prompt
- **Want to deactivate?** Type: `deactivate`

---

## File Structure

Your project should look like this:

```
C:\Users\YourName\data-engineering-project\
├── venv\                          # Virtual environment folder
├── airflow\
│   └── dags\
│       └── sales_pipeline.py       # Airflow DAG
├── sales_analytics\               # dbt project
│   ├── models\
│   │   ├── staging\
│   │   │   └── stg_sales_data.sql
│   │   ├── analytics\
│   │   │   ├── sales_by_category.sql
│   │   │   └── sales_by_region.sql
│   │   ├── sources.yml
│   │   └── schema.yml
│   └── dbt_project.yml
├── sales_sample.csv               # Sample data
└── requirements.txt               # List of dependencies
```

---

## Key Concepts to Understand

| Concept | Explanation |
|---------|-------------|
| **DAG** | Directed Acyclic Graph defining task dependencies |
| **Operator** | Airflow unit executing a specific task (Python, Bash, SQL) |
| **dbt Model** | SQL file transformed into table/view in data warehouse |
| **Staging** | Layer for cleaned/standardized raw data |
| **Analytics** | Layer with business-ready aggregated data |
| **Virtual Environment** | Isolated Python environment with specific package versions |

---

## Next Steps

1. Add error handling and logging to Airflow operators
2. Implement incremental loading (load only new data)
3. Add data quality checks (null checks, row count validation)
4. Create metrics dashboards using the analytics tables
5. Add more complex transformations in dbt models

---

## Resources

- [Apache Airflow Documentation](https://airflow.apache.org/)
- [dbt Documentation](https://docs.getdbt.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [UV Package Manager](https://astral.sh/blog/uv)
- [Python venv Documentation](https://docs.python.org/3/library/venv.html)
- [Windows Command Prompt Reference](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands-ref)
