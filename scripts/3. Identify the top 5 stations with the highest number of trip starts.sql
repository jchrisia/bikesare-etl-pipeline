SELECT
  start_station_name,
  COUNT(*) AS trip_starts
FROM
  `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
GROUP BY
  start_station_name
ORDER BY
  trip_starts DESC
LIMIT 5;
