 SELECT aggregation_table.site,
    aggregation_table.month,
    aggregation_table.year,
    logs.get_timestamp(aggregation_table.site) AS get_timestamp,
    round(100::numeric - sum(aggregation_table.outage_in_minutes) * 100::numeric / (logs.get_month_days(logs.get_timestamp(aggregation_table.site))::numeric * 1440::numeric), 2) AS "Availability"
   FROM logs.aggregation_table
  WHERE aggregation_table.year = 2022::numeric
  GROUP BY aggregation_table.site, aggregation_table.month, aggregation_table.year;