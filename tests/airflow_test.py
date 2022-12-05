import os
from airflow.models import DagBag
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.bash_operator import BashOperator


# Create DAG to load data from the landing table to the KPI table
ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
DAG_ID = "load_kpi_view_dag"
POSTGRES_CONNECTION_ID = 'postgres_db'
SCHEMA = 'postgres'

def test_no_import_errors():
    dag_bag = DagBag()
    dag = dag_bag.get_dag(dag_id='load_kpi_view_dag')
    assert len(dag_bag.import_errors) == 0, "No Import Failures"
    assert dag is not None


def count_all_sites():
    sql_stmt = "SELECT * FROM LOGS.KPI_VIEW"
    pg_hook = PostgresHook(postgres_conn_id='postgres_db',
                           schema='postgres'
                           )
    pg_conn = pg_hook.get_conn()
    cursor = pg_conn.cursor()
    cursor.execute(sql_stmt)

    result = cursor.fetchall()
    print('result', result)
    return result

result = count_all_sites()
assert result == 502