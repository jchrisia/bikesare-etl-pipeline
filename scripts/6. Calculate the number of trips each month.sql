SELECT
  FORMAT_DATE('%Y-%m', date) AS month,
  COUNT(*) AS trips
FROM
  `capable-acrobat-388708.bikeshare.external_bikeshare_trips`
GROUP BY
  month
ORDER BY
  month;
