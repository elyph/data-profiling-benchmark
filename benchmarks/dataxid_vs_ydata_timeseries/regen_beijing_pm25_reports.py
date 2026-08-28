"""Regenerate DataXID + ydata HTML reports for the UCI Beijing PM2.5 dataset."""

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

CSV = ROOT / "datasets" / "beijing_pm25" / "PRSA_data_2010.1.1-2014.12.31.csv"
OUT_DIR = ROOT / "benchmark_outputs" / "html_reports" / "three_real_datasets"


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(CSV, na_values=["NA"])
    df["datetime"] = pd.to_datetime(df[["year", "month", "day", "hour"]])
    # Keep year/month/day/hour as ordinal-code signals for `_is_ordinal_code`.
    df = df.drop(columns=["year", "month", "day", "hour"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return df


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df_pd = load_clean()
    df_pl = pl.from_pandas(df_pd)
    print(f"[+] Veri: {len(df_pd):,} satır, {df_pd.shape[1]} kolon")
    print(f"[+] Kolonlar: {list(df_pd.columns)}")

    dx_path = OUT_DIR / "dataxid_beijing_pm25.html"
    print(f"[+] DataXID raporu üretiliyor -> {dx_path}")
    dx_report = DataxidReport(
        df_pl,
        config=ProfileConfig(
            title="DataXID Beijing PM2.5 (Time Series)",
            mode="complete",
            ts_sortby="datetime",
        ),
    )
    dx_report.to_html(dx_path)

    dx_dict = dx_report.to_dict()
    ts_cols = [c for c, s in dx_dict["columns"].items() if s.get("is_timeseries")]
    print(f"    DataXID is_timeseries=True ({len(ts_cols)}): {ts_cols}")
    for c, s in dx_dict["columns"].items():
        if s.get("is_seasonal"):
            print(f"    seasonal: {c} -> periods={s.get('seasonal_periods')}")
    tia = dx_dict.get("time_index_analysis")
    if tia:
        print(f"    time_index_analysis: {tia}")
    del dx_report

    yd_path = OUT_DIR / "ydata_beijing_pm25.html"
    print(f"[+] ydata raporu üretiliyor -> {yd_path}")
    yd_report = YdataReport(
        df_pd,
        title="ydata Beijing PM2.5 (Time Series)",
        tsmode=True,
        sortby="datetime",
        minimal=False,
        progress_bar=False,
    )
    yd_path.write_text(yd_report.to_html(), encoding="utf-8")
    print(f"    ydata timeseries.active: {yd_report.config.vars.timeseries.active}")
    del yd_report

    print("Tamamlandı.")


if __name__ == "__main__":
    main()
