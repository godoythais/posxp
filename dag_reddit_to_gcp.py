import os
import subprocess
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
from airflow.utils.email import send_email

DAG_DIR = os.path.dirname(os.path.abspath(__file__))

GOOGLE_CREDENTIALS_PATH = os.path.join(DAG_DIR, "credenciais.json")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH

def run_script():
    """Executa o script de coleta de dados no Reddit e envia ao GCP"""
    try:
        result = subprocess.run(
            ["python3", "/home/script_collection.py"],
            check=True,
            capture_output=True,
            text=True,
            env={"GOOGLE_APPLICATION_CREDENTIALS": GOOGLE_CREDENTIALS_PATH, **os.environ},
        )
        print(f"Script executado com sucesso!\nSaída: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script!\nErro: {e.stderr}")

def enviar_alerta(context):
    msg = f"A DAG {context['task_instance'].dag_id} falhou!"
    send_email(to="email@gmail.com", subject="Alerta Airflow", html_content=msg)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 9),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": enviar_alerta
}

with DAG(
    "reddit_to_gcp",
    default_args=default_args,
    schedule_interval="0 9 * * *",
    catchup=False,
) as dag:

    # Dummy para indicar o início da DAG
    start_task = EmptyOperator(task_id="start")

    # Executa o script externo do Reddit
    task_run_script = PythonOperator(
        task_id="run_reddit_script",
        python_callable=run_script
    )

    # Dummy para indicar o final da DAG
    end_task = EmptyOperator(task_id="end")

    # Fluxo da DAG
    start_task >> task_run_script >> end_task
