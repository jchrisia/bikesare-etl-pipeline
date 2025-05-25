SELECT
  date,
  COUNT(trip_id) AS total_trips
FROM
  `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
GROUP BY
  date
ORDER BY
  date;
