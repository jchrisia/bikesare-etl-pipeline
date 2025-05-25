SELECT
  date,
  AVG(duration_minutes) AS avg_duration_minutes
FROM
  `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
GROUP BY
  date
ORDER BY
  date;
