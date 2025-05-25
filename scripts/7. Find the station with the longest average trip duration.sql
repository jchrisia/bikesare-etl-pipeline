SELECT
  start_station_name,
  AVG(duration_minutes) AS avg_duration
FROM
  `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
GROUP BY
  start_station_name
ORDER BY
  avg_duration DESC
LIMIT 1;
