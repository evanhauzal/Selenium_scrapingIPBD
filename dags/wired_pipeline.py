from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import psycopg2

def fetch_data(ti):
    # Pastikan API kamu (app.py/FastAPI) sudah mengirimkan field 'author'
    url = "http://host.docker.internal:8000/articles"
    data = requests.get(url).json()
    ti.xcom_push(key='data', value=data)

def save_to_db(ti):
    data = ti.xcom_pull(task_ids='fetch_task', key='data')

    conn = psycopg2.connect(
        host="postgres_new",  # Sesuaikan dengan nama service di docker-compose
        database="wired_db",
        user="admin",
        password="admin123",
        port=5432
    )

    cursor = conn.cursor()

    # PERBAIKAN 1: Tambahkan kolom 'author' pada skema tabel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wired_articles (
            id SERIAL PRIMARY KEY,
            title TEXT,
            link TEXT,
            author TEXT
        )
    """)

    for d in data:
        # PERBAIKAN 2: Masukkan nilai author ke dalam query INSERT
        # Menggunakan d.get('author') agar aman jika field author tidak ditemukan
        cursor.execute("""
            INSERT INTO wired_articles (title, link, author)
            VALUES (%s, %s, %s)
        """, (d['title'], d['link'], d.get('author', 'Unknown')))

    conn.commit()
    cursor.close()
    conn.close()

with DAG(
    dag_id='wired_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_task',
        python_callable=fetch_data
    )

    save_task = PythonOperator(
        task_id='save_task',
        python_callable=save_to_db
    )

    fetch_task >> save_task