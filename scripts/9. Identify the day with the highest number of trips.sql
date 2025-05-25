SELECT
  date,
  COUNT(*) AS trip_count
FROM
  `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
GROUP BY
  date
ORDER BY
  trip_count DESC
LIMIT 1;
