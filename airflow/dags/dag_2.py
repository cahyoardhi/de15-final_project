from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from codes.code import *

with DAG(
    "final_project_2",
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
    t1 = PythonOperator(
        task_id="get_data_from_api", python_callable=request_data_to_api, dag=dag
    )

    t2 = PythonOperator(
        task_id="json_to_dataframe", python_callable=json_to_df, dag=dag
    )

t1 >> t2
