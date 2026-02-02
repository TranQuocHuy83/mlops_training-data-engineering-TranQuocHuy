from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import psycopg2

# =========================
# Default DAG arguments
# =========================
default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# =========================
# Define DAG
# =========================
dag = DAG(
    dag_id='sales_data_pipeline',
    default_args=default_args,
    description='Basic ETL pipeline with dbt transformation',
    schedule='@daily',
    start_date=datetime(2024, 1, 15),
    catchup=False,
)

# =========================
# Task 1: Load CSV to PostgreSQL
# =========================
def load_csv_to_postgres():
    csv_path = r'D:\Huy IT\PTN GLOBAL\DE\data-engineering-exercise\sales_sample.csv'

    df = pd.read_csv(csv_path)

    conn = psycopg2.connect(
        host='localhost',
        database='data_engineering_exercise',
        user='postgres',
        password='tqhtgckm', 
        port=5432
    )

    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO raw.sales_data
            (product_name, category, price, quantity_sold, sale_date, region)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            tuple(row)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} rows into raw.sales_data")

# =========================
# Define Tasks
# =========================
load_task = PythonOperator(
    task_id='load_csv_to_postgres',
    python_callable=load_csv_to_postgres,
    dag=dag,
)

dbt_run_task = BashOperator(
    task_id='run_dbt_models',
    bash_command=(
        'cd "D:\\Huy IT\\PTN GLOBAL\\DE\\data-engineering-exercise\\sales_analytics" '
        '&& dbt run --profiles-dir .'
    ),
    dag=dag,
)

dbt_test_task = BashOperator(
    task_id='run_dbt_tests',
    bash_command=(
        'cd "D:\\Huy IT\\PTN GLOBAL\\DE\\data-engineering-exercise\\sales_analytics" '
        '&& dbt test --profiles-dir .'
    ),
    dag=dag,
)

# =========================
# Task dependencies
# =========================
load_task >> dbt_run_task >> dbt_test_task
