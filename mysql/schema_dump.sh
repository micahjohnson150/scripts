# Dump the schema data for the RME test.
alias sqlin='mysql -u micahjohnson -p --port=32768 -h 0.0.0.0'
QRY="date_time > '1998-01-14 15:00:00+00:00' AND date_time >='1998-01-14 19:00:00+00:00' AND station_id IN ('RMESP','RME_176')"
mysqldump -umicahjohnson -p  --databases weather_db --tables tbl_level2 --where=$QRY > rme_database.sql

