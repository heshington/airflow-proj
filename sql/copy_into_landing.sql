do $$
<<first_block>>

DECLARE x varchar(500);
BEGIN
  --FOREACH x IN ARRAY array[['/Users/hirenpatel/airflow/csv_batch_files/task_1_logs_batch_2.csv'], ['/Users/hirenpatel/airflow/csv_batch_files/task_1_logs_batch_3.csv'], ['/Users/hirenpatel/airflow/csv_batch_files/task_1_logs_batch_1.csv']]
  FOREACH x IN ARRAY array[{{params.csv_file}}]
  LOOP
    RAISE NOTICE 'row = %', x;
        execute format(
                    'COPY logs.landing_table("site", "start_timestamp", "end_timestamp")
                    FROM '''||x||'''
                    DELIMITER '',''
                    CSV HEADER'
        );
  END LOOP;
END  first_block $$;
