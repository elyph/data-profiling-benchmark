"""Regenerate DataXID + ydata HTML reports for the active-client electricity sample."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
FORK_SRC = r"C:\Users\elify\Documents\GitHub\dataxid-profiling\src"
if FORK_SRC not in sys.path:
    sys.path.insert(0, FORK_SRC)

from dataxid_profiling import ProfileConfig, ProfileReport as DataxidReport  # noqa: E402
from ydata_profiling import ProfileReport as YdataReport  # noqa: E402

CSV = ROOT / "datasets" / "electricity_sample.csv"
OUT_DIR = ROOT / "benchmark_outputs" / "html_reports" / "three_real_datasets"


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df_pd = pd.read_csv(CSV)
    df_pd["timestamp"] = pd.to_datetime(df_pd["timestamp"])
    df_pl = pl.from_pandas(df_pd)

    dx_path = OUT_DIR / "dataxid_electricity.html"
    print(f"[+] DataXID raporu üretiliyor -> {dx_path}")
    dx_report = DataxidReport(
        df_pl,
        config=ProfileConfig(
            title="DataXID electricity (Time Series)",
            mode="complete",
            ts_sortby="timestamp",
        ),
    )
    dx_report.to_html(dx_path)
    del dx_report

    yd_path = OUT_DIR / "ydata_electricity.html"
    print(f"[+] ydata raporu üretiliyor -> {yd_path}")
    yd_report = YdataReport(
        df_pd,
        title="ydata electricity (Time Series)",
        tsmode=True,
        sortby="timestamp",
        minimal=False,
        progress_bar=False,
    )
    yd_path.write_text(yd_report.to_html(), encoding="utf-8")
    del yd_report

    print("Tamamlandı.")


if __name__ == "__main__":
    main()
