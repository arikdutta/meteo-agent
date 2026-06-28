from __future__ import annotations

import argparse
import sqlite3
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

EVENTS_TABLE = "meteobeguda_events"
VIEWS = ("meteobeguda_daily", "meteobeguda_monthly", "meteobeguda_yearly")

DEFAULT_BASE_URL = (
    "https://github.com/ber2/meteobeguda-etl/raw/refs/heads/main/data/warehouse"
)
PERIODS = ("pre_2010", "2010_2015", "2015_2020", "post_2020")
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "meteobeguda.sqlite"


def download_sources(base_url: str, dest_dir: Path) -> list[Path]:
    paths = []
    for period in PERIODS:
        name = f"meteobeguda_{period}.sqlite"
        url = f"{base_url}/{name}"
        target = dest_dir / name
        print(f"downloading {name} ...")
        try:
            urllib.request.urlretrieve(url, target)
        except urllib.error.URLError as error:
            raise SystemExit(f"failed to download {url}: {error}")
        paths.append(target)
    return paths


def read_definition(connection: sqlite3.Connection, name: str) -> str:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE name = ?", (name,)
    ).fetchone()
    if row is None or row[0] is None:
        raise SystemExit(f"missing definition for {name}")
    return row[0]


def build(source_files: list[Path], output_path: Path) -> None:
    output_path.unlink(missing_ok=True)

    with sqlite3.connect(source_files[0]) as template:
        table_ddl = read_definition(template, EVENTS_TABLE)
        view_ddls = {view: read_definition(template, view) for view in VIEWS}

    with sqlite3.connect(output_path) as out:
        out.execute(table_ddl)
        for source in source_files:
            out.execute("ATTACH DATABASE ? AS src", (str(source),))
            out.execute(
                f"INSERT INTO {EVENTS_TABLE} SELECT * FROM src.{EVENTS_TABLE}"
            )
            out.commit()
            out.execute("DETACH DATABASE src")
        out.execute(f"CREATE INDEX idx_events_date ON {EVENTS_TABLE}(date)")
        for view_ddl in view_ddls.values():
            out.execute(view_ddl)
        out.commit()


def summarize(output_path: Path) -> None:
    with sqlite3.connect(output_path) as connection:
        rows = connection.execute(f"SELECT COUNT(*) FROM {EVENTS_TABLE}").fetchone()[0]
        first, last = connection.execute(
            f"SELECT MIN(date), MAX(date) FROM {EVENTS_TABLE}"
        ).fetchone()
        years = connection.execute("SELECT COUNT(*) FROM meteobeguda_yearly").fetchone()[0]
    print(f"built {output_path}")
    print(f"  {EVENTS_TABLE}: {rows} rows, {first} -> {last}")
    print(f"  meteobeguda_yearly: {years} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description="Consolidate meteobeguda period databases.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    print(f"consolidating {len(PERIODS)} files from {arguments.base_url}")
    with tempfile.TemporaryDirectory() as tmp:
        source_files = download_sources(arguments.base_url, Path(tmp))
        build(source_files, arguments.out)
    summarize(arguments.out)


if __name__ == "__main__":
    main()
