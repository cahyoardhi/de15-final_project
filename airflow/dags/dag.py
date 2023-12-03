from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from codes.code import *

with DAG(
    "dag_automation_daily",
    default_args={
        "depends_on_past": False,
        "email": ["sebastiancahyoardhiiswara@gmail.com"],
        "email_on_failure": True,
        "email_on_retry": False,
        "retries": 1,
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
    description="Final project for digitalskola DE bootcamp 2023",
    schedule_interval="@daily",
    start_date=datetime(2023, 11, 30),
    catchup=False,
    tags=["daily scheduler"],
) as dag:
    task = BashOperator(
        task_id="running_automation",
        bash_command="python codes/automation.py",
        cwd=dag.folder,
        dag=dag
    ),

    task
