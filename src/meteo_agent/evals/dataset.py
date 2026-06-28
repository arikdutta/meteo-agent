from __future__ import annotations

from dataclasses import dataclass

from meteo_agent.tools import read_only_connection


@dataclass(frozen=True)
class EvalCase:
    question: str
    reference_sql: str


# The reference SQL computes ground truth FROM the database, so the eval set
# can never go stale. Add or edit cases freely.
CASES = [
    EvalCase(
        "What was the hottest day on record, by highest daily maximum temperature? Give the date as YYYY-MM-DD.",
        "SELECT date FROM meteobeguda_daily ORDER BY temperature_max DESC LIMIT 1",
    ),
    EvalCase(
        "In which year did a single calendar month see the most total rainfall? Give the year.",
        "SELECT substr(month, 1, 4) FROM meteobeguda_monthly ORDER BY rain_total DESC LIMIT 1",
    ),
    EvalCase(
        "How many days in 2023 had a maximum temperature above 35 degrees Celsius?",
        "SELECT COUNT(*) FROM meteobeguda_daily WHERE temperature_max > 35 AND date LIKE '2023%'",
    ),
    EvalCase(
        "What is the earliest year present in the dataset?",
        "SELECT MIN(year) FROM meteobeguda_yearly",
    ),
    EvalCase(
        "What was the average temperature in 2003, to one decimal place?",
        "SELECT round(temperature_avg, 1) FROM meteobeguda_yearly WHERE year = '2003'",
    ),
]


def ground_truth(case: EvalCase) -> str:
    # TODO(checkpoint 07): run case.reference_sql against a read_only_connection
    # and return the single scalar result as a string.
    raise NotImplementedError("implement ground_truth")


def local_dataset() -> list[dict]:
    # TODO(checkpoint 07): build a list of {input, expected_output, metadata}
    # dicts from CASES, computing expected_output via ground_truth(case).
    raise NotImplementedError("implement local_dataset")
