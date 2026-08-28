"""DataXID vs Zarque — Minimal/Overview Mode Benchmark (common kütüphanesi ile)"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import gc
import polars as pl
from benchmarks.common import generate_synthetic_data, profile_dataxid, profile_zarque
from benchmarks.common import plot_speed

ROW_COUNTS = [1_000_000, 10_000_000, 25_000_000, 50_000_000, 75_000_000, 100_000_000]
N_RUNS = 1  # Detaylı istatistik için 5 yapın

print("=" * 50)
print("  DataXID vs Zarque — Minimal Mode Benchmark")
print("=" * 50)

dx_times, dx_time_errs = [], []
zq_times, zq_time_errs = [], []

for rows in ROW_COUNTS:
    data_dict = generate_synthetic_data(rows, backend="polars")
    df = pl.DataFrame(data_dict)
    print(f"\n[+] {rows:,} satır, {df.estimated_size('mb'):.1f} MB")

    print(f"--> DataXID OVERVIEW...")
    t_avg, t_std, _, _ = profile_dataxid(df, mode="overview", n_runs=N_RUNS)
    dx_times.append(t_avg); dx_time_errs.append(t_std)
    print(f"    {t_avg:.1f}s ± {t_std:.1f}")

    print(f"--> Zarque OVERVIEW...")
    t_avg, t_std, _, _ = profile_zarque(df, mode="overview", n_runs=N_RUNS)
    zq_times.append(t_avg); zq_time_errs.append(t_std)
    if t_avg > 0:
        print(f"    {t_avg:.1f}s ± {t_std:.1f}")
    else:
        print(f"    CRASHED")

    del df; gc.collect()

# Özet
print("\n" + "=" * 55)
print(f"{'Satır':>12}  {'DataXID':>12}  {'Zarque':>12}  {'Fark':>10}")
print("-" * 55)
for i, rows in enumerate(ROW_COUNTS):
    dx = dx_times[i]; zq = zq_times[i]
    if zq > 0 and dx > 0:
        diff = f"DX {zq/dx:.1f}x" if dx < zq else f"ZQ {dx/zq:.1f}x"
    else:
        diff = "CRASHED"
    print(f"{rows:>12,}  {dx:>8.1f}s±{dx_time_errs[i]:.1f}  {zq:>8.1f}s±{zq_time_errs[i]:.1f}  {diff:>10}")
print("=" * 55)

# Grafik (sadece speed)
speed_data = {
    "DataXID": (dx_times, dx_time_errs),
    "Zarque": (zq_times, zq_time_errs),
}
plot_speed(speed_data, ROW_COUNTS, title_suffix="Overview Mode")
print("\nBenchmark tamamlandı.")
