"""Regenerate datasets/electricity_sample.csv from LD2011_2014.txt.

Picks the first 8 active clients (MT_140..MT_147) instead of the all-zero
MT_001..MT_008 columns. Keeps the same CSV shape as the original sample:
timestamp + 8 client columns, comma delimiter, dot decimals, ISO timestamps,
first 20,000 rows.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "datasets" / "LD2011_2014.txt"
OUT = ROOT / "datasets" / "electricity_sample.csv"

START_CLIENT = 200
N_CLIENTS = 8
MAX_ROWS = 20_000


def main() -> None:
    clients = [f"MT_{i:03d}" for i in range(START_CLIENT, START_CLIENT + N_CLIENTS)]

    with SRC.open("r", encoding="utf-8", newline="") as f_in, OUT.open(
        "w", encoding="utf-8", newline=""
    ) as f_out:
        reader = csv.reader(f_in, delimiter=";")
        header = next(reader)

        # Header is quoted, first column is "" and holds the timestamp.
        by_name = {name.strip('"'): idx for idx, name in enumerate(header)}
        time_idx = 0
        client_idx = [by_name[c] for c in clients]

        writer = csv.writer(f_out)
        writer.writerow(["timestamp", *clients])

        for row_idx, row in enumerate(reader):
            if row_idx >= MAX_ROWS:
                break

            ts_raw = row[time_idx].strip('"')
            # Convert "2011-01-01 00:15:00" -> ISO-ish "2011-01-01T00:15:00.000000"
            date_part, time_part = ts_raw.split(" ", 1)
            iso_ts = f"{date_part}T{time_part}.000000"

            values = []
            for idx in client_idx:
                val = row[idx].replace(",", ".")
                values.append(val)

            writer.writerow([iso_ts, *values])

    print(f"[+] {OUT} yeniden üretildi ({MAX_ROWS:,} satır, {N_CLIENTS} client).")


if __name__ == "__main__":
    main()
