from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from codes.code import *

with DAG(
    "final_project",
    default_args={
        "depends_on_past": False,
        "email": ["sebastiancahyoardhiiswara@gmail.com"],
        "email_on_failure": True,
        "email_on_retry": False,
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function,
        # 'on_success_callback': some_other_function,
        # 'on_retry_callback': another_function,
        # 'sla_miss_callback': yet_another_function,
        # 'trigger_rule': 'all_success'
    },
    description="Final project for digital skola DE bootcamp 2023",
    schedule_interval="@daily",
    start_date=datetime(2023, 11, 27),
    catchup=False,
    tags=["daily scheduler"],
) as dag:
    # t1 = PythonOperator(
    #     task_id="get data from api",
    #     python_callable=extract(credentials_db_mysql),
    #     dag=dag,
    # )
    t2 = PythonOperator(
        task_id="generate schema dwh",
        python_callable=generate_schema_dwh(credentials_db_postgres),
        dag=dag,
    )
    t3 = PythonOperator(
        task_id="transformm",
        python_callable=transform(credentials_db_postgres),
        dag=dag,
    )

# t1 >> t2
# t1 >> t3

t2 >> t3