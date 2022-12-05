
--Clear out the table
truncate logs.aggregation_table_new;
 --aggregation_view

insert into logs.aggregation_table_new
SELECT l.id,
        l.site,
        EXTRACT(year FROM l.start_timestamp) AS "Year",
        EXTRACT(month FROM l.start_timestamp) AS "Month",
        sum(EXTRACT(epoch FROM (l.end_timestamp - l.start_timestamp) / 60::double precision))::bigint AS outage_in_minutes
        FROM logs.all_sites l
        GROUP BY l.site, (EXTRACT(year FROM l.start_timestamp)), (EXTRACT(month FROM l.start_timestamp)), l.id
       
