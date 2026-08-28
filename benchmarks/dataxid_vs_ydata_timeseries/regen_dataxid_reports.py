"""Regenerate all DataXID HTML reports under three_real_datasets (TS datasets).

Only regenerates DataXID reports (ydata is intentionally left untouched).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import polars as pl

ROOT = Path(r"C:\Users\elify\Documents\GitHub\data-profiling-benchmark")
FORK_SRC = r"C:\Users\elify\Documents\GitHub\dataxid-profiling\src"
if FORK_SRC not in sys.path:
    sys.path.insert(0, FORK_SRC)

from dataxid_profiling import ProfileConfig, ProfileReport as DataxidReport  # noqa: E402

OUT_DIR = ROOT / "benchmark_outputs" / "html_reports" / "three_real_datasets"


def _report(df: pl.DataFrame, name: str, ts_sortby: str | None, title: str) -> None:
    config = ProfileConfig(title=title, mode="complete", ts_sortby=ts_sortby)
    report = DataxidReport(df, config=config)
    out = OUT_DIR / name
    report.to_html(out)
    d = report.to_dict()
    ts_cols = [c for c, s in d["columns"].items() if s.get("is_timeseries")]
    seasonal = [c for c, s in d["columns"].items() if s.get("is_seasonal")]
    print(f"[+] {name}: n_series={len(ts_cols)} seasonal={len(seasonal)} -> {out}")


def bike_hour() -> pl.DataFrame:
    df = pd.read_csv(ROOT / "datasets" / "bike_sharing" / "hour.csv")
    df["datetime"] = pd.to_datetime(df["dteday"]) + pd.to_timedelta(df["hr"], unit="h")
    if "instant" in df.columns:
        df = df.drop(columns=["instant"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return pl.from_pandas(df)


def electricity() -> pl.DataFrame:
    df = pd.read_csv(ROOT / "datasets" / "electricity_sample.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return pl.from_pandas(df)


def co2() -> pl.DataFrame:
    import statsmodels.api as sm

    df = sm.datasets.co2.load_pandas().data
    df = df.reset_index().rename(columns={"index": "datetime"})
    df = df.dropna(subset=["co2"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return pl.from_pandas(df)


def air_quality() -> pl.DataFrame:
    csv = ROOT / "datasets" / "air_quality" / "AirQualityUCI.csv"
    df = pd.read_csv(csv, sep=";", decimal=",", na_values=["-200"])
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    time_str = df["Time"].str.replace(".", ":", regex=False)
    df["datetime"] = pd.to_datetime(df["Date"] + " " + time_str, format="%d/%m/%Y %H:%M:%S")
    df = df.drop(columns=["Date", "Time"])
    df = df.dropna(subset=["datetime"]).drop_duplicates(subset=["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return pl.from_pandas(df)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _report(
        bike_hour(),
        "dataxid_bike_hour.html",
        ts_sortby="datetime",
        title="DataXID Bike Hour (Time Series)",
    )
    _report(
        electricity(),
        "dataxid_electricity.html",
        ts_sortby="timestamp",
        title="DataXID electricity (Time Series)",
    )
    _report(
        co2(),
        "dataxid_co2.html",
        ts_sortby="datetime",
        title="DataXID co2 (Time Series)",
    )
    _report(
        air_quality(),
        "dataxid_air_quality.html",
        ts_sortby="datetime",
        title="DataXID Air Quality (Time Series)",
    )
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
