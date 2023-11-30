from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from codes.code import *

with DAG(
    "final_project_3",
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
    template_searchpath="/opt/airflow/dags",
) as dag:
    # t1 = BashOperator(task_id="running_automation", bash_command="echo pwd ", dag=dag)
    t0 = BashOperator(
        task_id="check_working_directory",
        bash_command="echo pwd",
        dag=dag,
        cwd=dag.folder,
    )
    t1 = BashOperator(
        task_id="check_working_directory_2",
        bash_command="echo ls",
        dag=dag,
        cwd=dag.folder,
    )
    t2 = BashOperator(
        task_id="running_automation_2",
        bash_command="python automation.py",
        dag=dag,
        cwd=dag.folder,
    )

    t0 >> t1
    t0 >> t2
