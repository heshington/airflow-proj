import datetime
import glob
import os
from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import ShortCircuitOperator


# set current working directroy
WORKING_DIR = os.chdir("/Users/hirenpatel/airflow/csv_batch_files/")

# Create DAG to load data from the landing table to the KPI table
ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
DAG_ID = "load_kpi_view_dag"
POSTGRES_CONNECTION_ID = 'postgres_db'
SCHEMA = 'postgres'


def check_files():
    # Check if there are any CSV files.
    csv_files = (glob.glob("/Users/hirenpatel/airflow/csv_batch_files/*.csv"))
    if len(csv_files) == 0:
        return False
    else:
        return True


def get_all_kpis():
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


def get_csv_files():
    csv_files = (glob.glob("/Users/hirenpatel/airflow/csv_batch_files/*.csv"))
    file_names = []
    for i in csv_files:
        # files = i.split("/")
        file_names.append(i)  # append the full file path
    print(file_names)
    return file_names


def load_csv_to_table():
    csvs = get_csv_files()
    counter = 0
    print("csv files are: " + str(csvs))

    for csv_file in csvs:

        load_landing_table = PostgresOperator(
            task_id="create_landing_table_"+str(counter),
            postgres_conn_id=POSTGRES_CONNECTION_ID,
            params={
                'csv_file': csv_file
            },
            sql=open('/Users/hirenpatel/airflow/sql/landing_table.sql')
            .read(),

        )
        print("csv files that is being processed is: " + str(csv_file))
        print("counter is at " + str(counter))

        counter = counter+1


with DAG(
    dag_id=DAG_ID,
    start_date=datetime.datetime(year=2022, month=2, day=2),
    schedule="@hourly",
    catchup=False,

    # render_template_as_native_obj=True
) as dag:
    #1 check the folder for any CSV files, if none do not continue with rest of the tasks
    check_for_csv = ShortCircuitOperator(
        task_id='check_for_csv',
        python_callable=check_files,
        op_kwargs={
            'files': '{{ti.xcom_pull(task_ids="list_csv_files")}}'
        }
    )
    #2 clear out the loading table
    truncate_loading_table = PostgresOperator(
        task_id="truncate_loading_table",
        postgres_conn_id=POSTGRES_CONNECTION_ID,
        params={
            'test': "hello world"
        },
        sql=open('/Users/hirenpatel/airflow/sql/landing_table.sql')
        .read(),
    )
    # 3. load the csv files into the table

    load_landing_table = PostgresOperator(
        task_id="load_landing_table",
        postgres_conn_id=POSTGRES_CONNECTION_ID,
        params={
                'csv_file': get_csv_files()
        },
        sql=open('/Users/hirenpatel/airflow/sql/copy_into_landing.sql')
        .read(),
    )

    # 4.move csv's into processed folder
    move_csvs = BashOperator(
        task_id='move_csvs',
        bash_command='mv /Users/hirenpatel/airflow/csv_batch_files/*.csv /Users/hirenpatel/airflow/csv_processed/',
    )

    # 5. Copy data from landing table into all sites table
    load_all_sites_table = PostgresOperator(
        task_id="load_all_sites_table",
        postgres_conn_id=POSTGRES_CONNECTION_ID,
        sql="""
        INSERT INTO logs.all_sites
        SELECT *
        FROM logs.landing_table
        """
    )
    # 6. Update the Aggregation_table so the kpi view can have updated data.
    update_agg_table = PostgresOperator(
        task_id="update_agg_table",
        postgres_conn_id=POSTGRES_CONNECTION_ID,
        sql=open('/Users/hirenpatel/airflow/sql/generate_agg_table.sql')
        .read(),
    )

    # 4. Get the KPI data from a table in Postgres
    #get_all_kpis = PythonOperator(
    #    dag=dag,
    #    task_id='get_all_kpis',
    #    python_callable=get_all_kpi

    #)

check_for_csv >> truncate_loading_table >> load_landing_table >> move_csvs >> load_all_sites_table >> update_agg_table
