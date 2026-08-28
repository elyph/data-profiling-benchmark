"""Regenerate DataXID + ydata HTML reports for the UCI Appliances Energy dataset."""

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

CSV = ROOT / "datasets" / "appliances_energy" / "energydata_complete.csv"
OUT_DIR = ROOT / "benchmark_outputs" / "html_reports" / "three_real_datasets"


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(CSV)
    df["datetime"] = pd.to_datetime(df["date"])
    df = df.drop(columns=["date"])
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

    dx_path = OUT_DIR / "dataxid_appliances_energy.html"
    print(f"[+] DataXID raporu üretiliyor -> {dx_path}")
    dx_report = DataxidReport(
        df_pl,
        config=ProfileConfig(
            title="DataXID Appliances Energy (Time Series)",
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
        print(f"    n_series: {tia.get('n_series')}")
        print(f"    plotted_series: {tia.get('plotted_series')}")
        print(f"    period: {tia.get('period')}")
    del dx_report

    yd_path = OUT_DIR / "ydata_appliances_energy.html"
    print(f"[+] ydata raporu üretiliyor -> {yd_path}")
    yd_report = YdataReport(
        df_pd,
        title="ydata Appliances Energy (Time Series)",
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
