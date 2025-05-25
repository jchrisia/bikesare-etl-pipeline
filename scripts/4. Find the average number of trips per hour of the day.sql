SELECT
  hour,
  AVG(trip_count) AS avg_trips_per_hour
FROM (
  SELECT
    date,
    hour,
    COUNT(*) AS trip_count
  FROM
    `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
  GROUP BY
    date, hour
)
GROUP BY
  hour
ORDER BY
  hour;
