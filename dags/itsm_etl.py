from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import psycopg2
import os


def fetch_dashboard_data():
    # Use host.docker.internal for accessing host APIs from inside Docker
    url = "http://host.docker.internal:5000/dashboard-data"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def store_dashboard_data():
    import logging

    # PostgreSQL connection
    conn = psycopg2.connect(
        host="postgres",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()

    try:
        data = fetch_dashboard_data()

        # 1. Insert incident_status_summary
        for record in data["incident_status_summary"]:
            cur.execute("""
                INSERT INTO incident_status_summary (month, closed, pending, resolved, total)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                record["month"],
                record["closed"],
                record["pending"],
                record["resolved"],
                record["total"]
            ))

        # 2. Insert attack_vector_summary
        for record in data["attack_vector_summary"]:
            cur.execute("""
                INSERT INTO attack_vector_summary (month, external_internal, internal_external, internal_internal)
                VALUES (%s, %s, %s, %s)
            """, (
                record["month"],
                record["external_internal"],
                record["internal_external"],
                record["internal_internal"]
            ))

        conn.commit()
        logging.info("Data inserted successfully.")

    except Exception as e:
        logging.error(f"Error while inserting data: {e}")
        conn.rollback()

    cur.close()
    conn.close()


# Define DAG
default_args = {
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="itsm_dashboard_etl",
     schedule_interval="* * * * *",
    default_args=default_args,
    catchup=False
) as dag:

    extract_and_store = PythonOperator(
        task_id="store_dashboard_data",
        python_callable=store_dashboard_data
    )

    extract_and_store
