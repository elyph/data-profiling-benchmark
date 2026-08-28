"""DataXID (Faz 4 fork) vs ydata-profiling — Time Series Benchmark (Gerçek Veri).

Bike Sharing (hour) verisiyle:
1. İkisinden de HTML rapor üretir (elle karşılaştırma).
2. İkisinin süre + RAM değerlerini ölçer.
3. Sonuçları PNG grafik + konsol tablosu olarak verir.

"""

from __future__ import annotations

import gc
import os
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import psutil

# ---------------------------------------------------------------------------
# Faz 4 fork'unu en başta sys.path'e bağla (her import'tan önce).
# ---------------------------------------------------------------------------
FORK_SRC = r"C:\Users\elify\Documents\GitHub\dataxid-profiling\src"
if FORK_SRC not in sys.path:
    sys.path.insert(0, FORK_SRC)

from dataxid_profiling import ProfileConfig, ProfileReport as DataxidReport  # noqa: E402
from ydata_profiling import ProfileReport as YdataReport  # noqa: E402

# ---------------------------------------------------------------------------
# Yollar
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "datasets" / "bike_sharing"
DATASET_PATH = DATASET_DIR / "hour.csv"
HTML_DIR = ROOT / "benchmark_outputs" / "html_reports" / "dataxid_vs_ydata_ts"
CHART_DIR = ROOT / "benchmark_outputs" / "charts" / "dataxid_vs_ydata_ts"

DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip"

COLORS = {
    "DataXID": "#4472C4",
    "DataXID (full)": "#2E75B6",
    "ydata": "#ED7D31",
}


def mem_mb() -> float:
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


# ---------------------------------------------------------------------------
# Veri yükleme + ön işleme
# ---------------------------------------------------------------------------
def ensure_dataset() -> None:
    if DATASET_PATH.exists():
        return
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DATASET_DIR / "Bike-Sharing-Dataset.zip"
    print(f"[+] Bike Sharing verisi indiriliyor: {DATASET_URL}")
    urllib.request.urlretrieve(DATASET_URL, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extract("hour.csv", DATASET_DIR)
    zip_path.unlink()
    print(f"    hour.csv çıkarıldı: {DATASET_PATH}")


def load_raw() -> pd.DataFrame:
    ensure_dataset()
    return pd.read_csv(DATASET_PATH)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["dteday"]) + pd.to_timedelta(df["hr"], unit="h")
    if "instant" in df.columns:
        df = df.drop(columns=["instant"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return df


def scale_rows(df: pd.DataFrame, target_rows: int) -> pd.DataFrame:
    """Gerçek deseni koruyarak satır sayısını tile ile ölçekle.

    datetime kolonu her tile'da saat başı ilerletilerek unique kalır.
    """
    df = df.sort_values("datetime").reset_index(drop=True)
    n = len(df)
    if target_rows <= n:
        return df.head(target_rows).reset_index(drop=True)

    span = df["datetime"].iloc[-1] - df["datetime"].iloc[0] + pd.Timedelta(hours=1)
    parts = []
    needed = target_rows
    i = 0
    while needed > 0:
        part = df.copy()
        part["datetime"] = part["datetime"] + i * span
        parts.append(part.head(needed))
        needed -= len(part)
        i += 1
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# HTML rapor fazı (ölçüme dahil değil)
# ---------------------------------------------------------------------------
def generate_html(df_pd: pd.DataFrame, df_pl: pl.DataFrame) -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    dx_path = HTML_DIR / "dataxid_bike_hour.html"
    print(f"\n[+] DataXID HTML raporu üretiliyor -> {dx_path}")
    dx_config = ProfileConfig(
        title="DataXID Bike Hour (Time Series)",
        mode="complete",
        ts_sortby="datetime",
    )
    dx_report = DataxidReport(df_pl, config=dx_config)
    dx_report.to_html(dx_path)

    yd_path = HTML_DIR / "ydata_bike_hour.html"
    print(f"[+] ydata HTML raporu üretiliyor -> {yd_path}")
    yd_report = YdataReport(
        df_pd,
        title="ydata Bike Hour (Time Series)",
        tsmode=True,
        sortby="datetime",
        minimal=False,
        progress_bar=False,
    )
    yd_path.write_text(yd_report.to_html(), encoding="utf-8")

    del dx_report, yd_report
    gc.collect()


# ---------------------------------------------------------------------------
# Benchmark fazı
# ---------------------------------------------------------------------------
def run_benchmark(profile_func, n_runs: int):
    times: list[float] = []
    mems: list[float] = []

    for run in range(n_runs):
        gc.collect()
        mem_before = mem_mb()
        t0 = time.perf_counter()

        try:
            profile_func()
        except Exception as e:
            print(f"    [!] Run {run + 1} hata: {e}")
            if run == 0:
                return 0.0, 0.0, 0.0, 0.0
            continue

        elapsed = time.perf_counter() - t0
        delta_mem = max(0.0, mem_mb() - mem_before)
        times.append(elapsed)
        mems.append(delta_mem)
        print(f"      run {run + 1}: {elapsed:.2f}s | +{delta_mem:.1f}MB")

    if not times:
        return 0.0, 0.0, 0.0, 0.0

    t_avg = float(np.mean(times))
    t_std = float(np.std(times, ddof=1)) if len(times) > 1 else 0.0
    m_avg = float(np.mean(mems))
    m_std = float(np.std(mems, ddof=1)) if len(mems) > 1 else 0.0
    return t_avg, t_std, m_avg, m_std


def make_dataxid_profiler(df_pl: pl.DataFrame):
    config = ProfileConfig(
        title="DataXID TS Benchmark",
        mode="complete",
        ts_sortby="datetime",
    )

    def _run():
        report = DataxidReport(df_pl, config=config)
        report.to_dict()

    return _run


def make_dataxid_profiler_full(df_pl: pl.DataFrame):
    config = ProfileConfig(
        title="DataXID TS Benchmark (full)",
        mode="complete",
        ts_sortby="datetime",
        ts_adf_max_points=None,
        ts_acf_pacf_max_points=None,
        ts_line_max_points=10_000_000,
    )

    def _run():
        report = DataxidReport(df_pl, config=config)
        report.to_dict()

    return _run


def make_ydata_profiler(df_pd: pd.DataFrame):
    def _run():
        report = YdataReport(
            df_pd,
            title="ydata TS Benchmark",
            tsmode=True,
            sortby="datetime",
            minimal=False,
            progress_bar=False,
        )
        report.get_description()

    return _run


# ---------------------------------------------------------------------------
# Grafik
# ---------------------------------------------------------------------------
def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n // 1_000_000}M"
    return f"{n // 1_000}K"


def plot_results(
    results: dict[str, tuple], row_labels: list[int], chart_type: str, suffix: str = ""
) -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    names = list(results.keys())
    n_names = len(names)
    labels = [_fmt(r) for r in row_labels]
    x = np.arange(len(row_labels))
    width = 0.8 / n_names

    fig, ax = plt.subplots(figsize=(11, 6))

    for i, name in enumerate(names):
        values, errors = results[name]
        err = errors if any(e > 0 for e in errors) else None
        offset = (i - (n_names - 1) / 2) * width
        bars = ax.bar(
            x + offset,
            values,
            width,
            label=name,
            color=COLORS.get(name, "#999999"),
            yerr=err,
            capsize=4,
            error_kw={"elinewidth": 1.5},
        )
        ax.bar_label(bars, padding=3, fmt="%.1f")

    ylabel = "Süre (saniye)" if chart_type == "speed" else "Ekstra RAM (MB)"
    ax.set_ylabel(ylabel, fontweight="bold")
    ax.set_xlabel("Satır Sayısı", fontweight="bold")
    ax.set_title(
        f"DataXID vs ydata — Time Series ({ylabel}) · Bike Sharing",
        fontweight="bold",
        pad=20,
        fontsize=12,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="y", linestyle="-", alpha=0.3)

    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
    plt.figtext(0.12, 0.02, f"Environment: {ram_gb} GB RAM | ts_sortby=datetime", ha="left", fontsize=9)
    plt.subplots_adjust(bottom=0.18)

    out = CHART_DIR / f"ts_{chart_type}{suffix}.png"
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"    {out} kaydedildi.")


# ---------------------------------------------------------------------------
# Sanity check
# ---------------------------------------------------------------------------
def sanity_check(df_pd: pd.DataFrame, df_pl: pl.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("  Sanity Check: TS analizi tetikleniyor mu?")
    print("=" * 60)

    dx_report = DataxidReport(
        df_pl,
        config=ProfileConfig(title="sanity", mode="complete", ts_sortby="datetime"),
    )
    d = dx_report.to_dict()
    ts_cols = [c for c, s in d["columns"].items() if s.get("is_timeseries")]
    has_time_index = d.get("time_index_analysis") is not None
    print(f"    DataXID is_timeseries=True sütunlar: {ts_cols}")
    print(f"    DataXID time_index_analysis var mı: {has_time_index}")
    if not ts_cols:
        print("    [!] DataXID TS tespit etmedi — benchmark anlamsız, dur.")
        sys.exit(1)

    yd_report = YdataReport(
        df_pd,
        title="sanity",
        tsmode=True,
        sortby="datetime",
        minimal=False,
        progress_bar=False,
    )
    yd_report.get_description()
    print(f"    ydata timeseries.active: {yd_report.config.vars.timeseries.active}")
    print(f"    ydata timeseries.sortby: {yd_report.config.vars.timeseries.sortby}")
    print("    OK\n")

    del dx_report, yd_report, d
    gc.collect()


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def parse_args(argv: list[str]) -> tuple[list[int], int]:
    sizes = [17_379, 50_000, 100_000]
    runs = 3

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--sizes" and i + 1 < len(argv):
            sizes = [int(x.strip()) for x in argv[i + 1].split(",")]
            i += 2
        elif arg == "--runs" and i + 1 < len(argv):
            runs = int(argv[i + 1])
            i += 2
        else:
            i += 1
    return sizes, runs


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    sizes, n_runs = parse_args(sys.argv[1:])

    print("=" * 70)
    print("  DataXID vs ydata — TIME SERIES Benchmark (Bike Sharing)")
    print(f"  Boyutlar: {sizes} | n_runs: {n_runs}")
    print("=" * 70)

    raw = load_raw()
    base_pd = preprocess(raw)
    print(f"\n[+] Gerçek veri: {len(base_pd):,} satır, {base_pd.shape[1]} kolon")

    # Sanity + HTML sadece gerçek veride
    base_pl = pl.from_pandas(base_pd)
    sanity_check(base_pd, base_pl)
    generate_html(base_pd, base_pl)

    # Benchmark
    dx_times, dx_errs, dx_mems, dx_mem_errs = [], [], [], []
    dxf_times, dxf_errs, dxf_mems, dxf_mem_errs = [], [], [], []
    yd_times, yd_errs, yd_mems, yd_mem_errs = [], [], [], []

    for rows in sizes:
        print(f"\n{'=' * 60}")
        print(f"  {rows:,} satır")
        print(f"{'=' * 60}")

        df_pd = scale_rows(base_pd, rows)
        df_pl = pl.from_pandas(df_pd)
        print(f"  kolon: {df_pd.shape[1]} | polars ~{df_pl.estimated_size('mb'):.1f}MB")

        print(f"--> DataXID ({n_runs} run)...")
        t_avg, t_std, m_avg, m_std = run_benchmark(make_dataxid_profiler(df_pl), n_runs)
        dx_times.append(t_avg)
        dx_errs.append(t_std)
        dx_mems.append(m_avg)
        dx_mem_errs.append(m_std)

        print(f"--> DataXID full ({n_runs} run)...")
        t_avg, t_std, m_avg, m_std = run_benchmark(make_dataxid_profiler_full(df_pl), n_runs)
        dxf_times.append(t_avg)
        dxf_errs.append(t_std)
        dxf_mems.append(m_avg)
        dxf_mem_errs.append(m_std)

        print(f"--> ydata ({n_runs} run)...")
        t_avg, t_std, m_avg, m_std = run_benchmark(make_ydata_profiler(df_pd), n_runs)
        yd_times.append(t_avg)
        yd_errs.append(t_std)
        yd_mems.append(m_avg)
        yd_mem_errs.append(m_std)

        del df_pd, df_pl
        gc.collect()

    # Özet tablo
    print("\n" + "=" * 110)
    print(
        f"{'Satır':>12}  {'DX Süre':>12}  {'DX full Süre':>14}  {'ydata Süre':>13}  "
        f"{'Speedup':>9}  {'DX RAM':>9}  {'DX full RAM':>12}  {'ydata RAM':>11}"
    )
    print("-" * 110)
    for i, rows in enumerate(sizes):
        speedup = (
            f"{yd_times[i] / dx_times[i]:.1f}x"
            if dx_times[i] > 0 and yd_times[i] > 0
            else "-"
        )
        print(
            f"{rows:>12,}  "
            f"{dx_times[i]:>8.1f}s±{dx_errs[i]:.1f}  "
            f"{dxf_times[i]:>8.1f}s±{dxf_errs[i]:.1f}  "
            f"{yd_times[i]:>9.1f}s±{yd_errs[i]:.1f}  "
            f"{speedup:>9}  "
            f"{dx_mems[i]:>7.1f}M  "
            f"{dxf_mems[i]:>9.1f}M  "
            f"{yd_mems[i]:>9.1f}M"
        )
    print("=" * 110)

    results_speed = {
        "DataXID": (dx_times, dx_errs),
        "DataXID (full)": (dxf_times, dxf_errs),
        "ydata": (yd_times, yd_errs),
    }
    results_ram = {
        "DataXID": (dx_mems, dx_mem_errs),
        "DataXID (full)": (dxf_mems, dxf_mem_errs),
        "ydata": (yd_mems, yd_mem_errs),
    }

    plot_results(results_speed, sizes, "speed", suffix="_full")
    plot_results(results_ram, sizes, "ram", suffix="_full")

    print("\nDataXID vs ydata time series benchmark tamamlandı.")


if __name__ == "__main__":
    main()
