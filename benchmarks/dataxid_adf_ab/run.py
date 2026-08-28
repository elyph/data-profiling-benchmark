"""DataXID ADF / Statsmodels etkisi — ts_active A/B benchmark.

Sadece DataXID. Sentetik zaman serisi veriyle ADF'nin gerçekten çalıştığı senaryoda:
- ts_active=True  (numerik TS tespiti + ADF + statsmodels import)
- ts_active=False (TS yok, orijinale yakın)

OFF önce koşulur, ON sonra koşulur; böylece statsmodels'ın import maliyeti ON'a
atfedilir. Ayrıca aşağıda import + tek adfuller mikro-testi ile maliyet ayrıştırılır.
"""

import gc
import sys
import os
import time

import numpy as np
import polars as pl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dataxid_profiling import ProfileConfig, ProfileReport  # noqa: E402
from benchmarks.common import (  # noqa: E402
    ensure_output_dir,
    generate_timeseries_data,
    plot_ab,
    profile_dataxid_ts_ab,
)

ROW_COUNTS = [20_000, 50_000, 100_000]
N_RUNS = 3


def sanity_check():
    """ADF'nin gerçekten tetiklendiğini doğrula."""
    print("=" * 60)
    print("  Sanity Check: ADF tetikleniyor mu?")
    print("=" * 60)

    df = pl.DataFrame(generate_timeseries_data(2_000, seed=42))
    report = ProfileReport(df, config=ProfileConfig(title="sanity", mode="complete"))
    stats = report.to_dict()

    ts_count = 0
    for col_name, col_stats in stats["columns"].items():
        if isinstance(col_stats, dict) and col_stats.get("is_timeseries"):
            ts_count += 1

    print(f"    is_timeseries=True sütun sayısı: {ts_count}")
    if ts_count == 0:
        print("    [!] ADF tetiklenmedi — benchmark anlamsız, dur.")
        sys.exit(1)
    print("    OK\n")


def statsmodels_micro_test():
    """statsmodels import + tek adfuller maliyetini ayrı subprocess'te ölç."""
    import subprocess

    print("=" * 60)
    print("  statsmodels Mikro-Testi (temiz subprocess)")
    print("=" * 60)

    script = (
        "import time, psutil, os\n"
        "m0 = psutil.Process(os.getpid()).memory_info().rss / 1048576\n"
        "t0 = time.perf_counter()\n"
        "from statsmodels.tsa.stattools import adfuller\n"
        "t1 = time.perf_counter()\n"
        "m1 = psutil.Process(os.getpid()).memory_info().rss / 1048576\n"
        "import numpy as np\n"
        "x = np.arange(2000, dtype=np.float64)\n"
        "t2 = time.perf_counter()\n"
        "adfuller(x, autolag='AIC')\n"
        "t3 = time.perf_counter()\n"
        "print(f'{t1-t0:.3f}|{m1-m0:.1f}|{t3-t2:.3f}')\n"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    out = result.stdout.strip()
    try:
        import_elapsed, import_mem, adf_elapsed = out.split("|")
        print(f"    import statsmodels.tsa.stattools: {float(import_elapsed):.3f}s | +{float(import_mem):.1f}MB")
        print(f"    tek adfuller(n=2000, autolag=AIC): {float(adf_elapsed):.3f}s\n")
    except Exception:
        print("    mikro-test başarısız:", result.stderr or out, "\n")


def run_ab():
    on_times, on_errs, on_mems, on_mem_errs = [], [], [], []
    off_times, off_errs, off_mems, off_mem_errs = [], [], [], []

    for rows in ROW_COUNTS:
        data = generate_timeseries_data(rows, seed=42)
        df = pl.DataFrame(data)
        print(f"\n{'=' * 55}")
        print(f"  {rows:,} satır ({df.width} kolon)")
        print(f"{'=' * 55}")

        print(f"--> DataXID A/B (OFF önce, ON sonra)...")
        (on_t, on_ts, on_m, on_ms), (off_t, off_ts, off_m, off_ms) = profile_dataxid_ts_ab(
            df, mode="complete", n_runs=N_RUNS
        )

        on_times.append(on_t); on_errs.append(on_ts)
        on_mems.append(on_m); on_mem_errs.append(on_ms)
        off_times.append(off_t); off_errs.append(off_ts)
        off_mems.append(off_m); off_mem_errs.append(off_ms)

        delta_t = on_t - off_t
        delta_m = on_m - off_m
        print(f"    ON : {on_t:.2f}s ± {on_ts:.2f} | {on_m:.1f}MB ± {on_ms:.1f}")
        print(f"    OFF: {off_t:.2f}s ± {off_ts:.2f} | {off_m:.1f}MB ± {off_ms:.1f}")
        print(f"    Δ  : {delta_t:+.2f}s | {delta_m:+.1f}MB")

        del df, data
        gc.collect()

    print("\n" + "=" * 90)
    header = (
        f"{'Satır':>12}  {'ON Süre':>14}  {'OFF Süre':>14}  {'Δ Süre':>10}  "
        f"{'ON RAM':>10}  {'OFF RAM':>10}  {'Δ RAM':>10}"
    )
    print(header)
    print("-" * 90)
    for i, rows in enumerate(ROW_COUNTS):
        print(
            f"{rows:>12,}  "
            f"{on_times[i]:>10.2f}s±{on_errs[i]:.1f}  "
            f"{off_times[i]:>10.2f}s±{off_errs[i]:.1f}  "
            f"{on_times[i]-off_times[i]:>+8.2f}s  "
            f"{on_mems[i]:>8.1f}M  "
            f"{off_mems[i]:>8.1f}M  "
            f"{on_mems[i]-off_mems[i]:>+8.1f}M"
        )
    print("=" * 90)

    charts_dir = ensure_output_dir("charts/dataxid_adf_ab")
    plot_ab(
        on_times, off_times, on_errs, off_errs, ROW_COUNTS,
        f"{charts_dir}/dataxid_adf_ab_speed.png", chart_type="speed",
    )
    plot_ab(
        on_mems, off_mems, on_mem_errs, off_mem_errs, ROW_COUNTS,
        f"{charts_dir}/dataxid_adf_ab_ram.png", chart_type="ram",
    )
    print("\nDataXID ADF A/B benchmark tamamlandı.")


if __name__ == "__main__":
    sanity_check()
    statsmodels_micro_test()
    run_ab()
