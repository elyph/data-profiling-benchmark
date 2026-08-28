"""DataXID vs Zarque — Complete Mode Benchmark"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import gc
import polars as pl
from benchmarks.common import generate_synthetic_data, profile_dataxid, profile_zarque
from benchmarks.common import plot_speed, plot_ram

ROW_COUNTS = [100_000, 500_000, 1_000_000, 2_000_000]
N_RUNS = 3

print("=" * 55)
print("  DataXID vs Zarque — COMPLETE Mode Benchmark")
print("  (Korelasyon + Etkileşim + Karakter Analizi dahil)")
print("=" * 55)

dx_times, dx_time_errs = [], []
zq_times, zq_time_errs = [], []
dx_mems, dx_mem_errs = [], []
zq_mems, zq_mem_errs = [], []

for rows in ROW_COUNTS:
    data_dict = generate_synthetic_data(rows, backend="polars")
    df = pl.DataFrame(data_dict)
    print(f"\n[+] {rows:,} satır, {df.estimated_size('mb'):.1f} MB")

    print(f"--> DataXID COMPLETE...")
    t_avg, t_std, m_avg, m_std = profile_dataxid(df, mode="complete", n_runs=N_RUNS)
    dx_times.append(t_avg); dx_time_errs.append(t_std)
    dx_mems.append(m_avg); dx_mem_errs.append(m_std)
    print(f"    {t_avg:.1f}s ± {t_std:.1f} | {m_avg:.1f}MB ± {m_std:.1f}")

    print(f"--> Zarque COMPLETE...")
    t_avg, t_std, m_avg, m_std = profile_zarque(df, mode="complete", n_runs=N_RUNS)
    zq_times.append(t_avg); zq_time_errs.append(t_std)
    zq_mems.append(m_avg); zq_mem_errs.append(m_std)
    if t_avg > 0:
        print(f"    {t_avg:.1f}s ± {t_std:.1f} | {m_avg:.1f}MB ± {m_std:.1f}")
    else:
        print(f"    CRASHED")

    del df; gc.collect()

# Özet
print("\n" + "=" * 75)
print(f"{'Satır':>12}  {'DX Süre':>12}  {'ZQ Süre':>12}  {'DX RAM':>12}  {'ZQ RAM':>12}")
print("-" * 75)
for i, rows in enumerate(ROW_COUNTS):
    print(f"{rows:>12,}  {dx_times[i]:>8.1f}s±{dx_time_errs[i]:.1f}  {zq_times[i]:>8.1f}s±{zq_time_errs[i]:.1f}  {dx_mems[i]:>8.1f}M±{dx_mem_errs[i]:.1f}  {zq_mems[i]:>8.1f}M±{zq_mem_errs[i]:.1f}")
print("=" * 75)

# Grafikler
speed_data = {
    "DataXID": (dx_times, dx_time_errs),
    "Zarque": (zq_times, zq_time_errs),
}
ram_data = {
    "DataXID": (dx_mems, dx_mem_errs),
    "Zarque": (zq_mems, zq_mem_errs),
}

plot_speed(speed_data, ROW_COUNTS, title_suffix="Complete Mode")
plot_ram(ram_data, ROW_COUNTS, title_suffix="Complete Mode")
print("\nComplete mode benchmark tamamlandı.")
