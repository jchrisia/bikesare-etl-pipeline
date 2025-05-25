SELECT
  start_station_name,
  end_station_name,
  COUNT(*) AS route_count
FROM
  `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
GROUP BY
  start_station_name, end_station_name
ORDER BY
  route_count DESC
LIMIT 1;
