from __future__ import annotations

import sqlite3

import pytest

EVENTS_DDL = """
CREATE TABLE meteobeguda_events (
    date DATE, temperature REAL, temperature_max REAL, temperature_min REAL,
    humidity INTEGER, windspeed REAL, windspeed_max REAL, pressure REAL, rain REAL
)
"""

DAILY_DDL = """
CREATE VIEW meteobeguda_daily AS SELECT date,
    avg(temperature) temperature_avg, min(temperature) temperature_min,
    max(temperature) temperature_max, avg(humidity) humidity_avg,
    avg(windspeed) windspeed_avg, max(windspeed_max) windspeed_max,
    avg(pressure) pressure_avg, sum(rain) rain_total
FROM meteobeguda_events GROUP BY 1
"""

MONTHLY_DDL = """
CREATE VIEW meteobeguda_monthly AS SELECT strftime('%Y-%m-01', date) month,
    avg(temperature_avg) temperature_avg, min(temperature_min) temperature_min,
    max(temperature_max) temperature_max, avg(humidity_avg) humidity_avg,
    avg(windspeed_avg) windspeed_avg, max(windspeed_max) windspeed_max,
    sum(rain_total) rain_total
FROM meteobeguda_daily GROUP BY 1
"""

YEARLY_DDL = """
CREATE VIEW meteobeguda_yearly AS SELECT strftime('%Y', month) year,
    avg(temperature_avg) temperature_avg, min(temperature_min) temperature_min,
    max(temperature_max) temperature_max, avg(humidity_avg) humidity_avg,
    avg(windspeed_avg) windspeed_avg, max(windspeed_max) windspeed_max,
    sum(rain_total) rain_total
FROM meteobeguda_monthly GROUP BY 1
"""

ROWS = [
    ("2010-08-16", 30.0, 40.6, 22.0, 50, 5.0, 12.0, 1010.0, 0.0),
    ("2010-08-16", 28.0, 39.0, 23.0, 55, 4.0, 10.0, 1009.0, 0.0),
    ("2003-07-01", 25.0, 33.0, 18.0, 60, 3.0, 8.0, 1012.0, 1.5),
    ("2002-03-28", 10.0, 14.0, 5.0, 70, 6.0, 15.0, 1015.0, 2.0),
]


@pytest.fixture
def meteo_db(tmp_path, monkeypatch):
    path = tmp_path / "test.sqlite"
    connection = sqlite3.connect(path)
    connection.execute(EVENTS_DDL)
    connection.executemany(
        "INSERT INTO meteobeguda_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ROWS
    )
    for ddl in (DAILY_DDL, MONTHLY_DDL, YEARLY_DDL):
        connection.execute(ddl)
    connection.commit()
    connection.close()
    monkeypatch.setenv("METEO_DB_PATH", str(path))
    return path
