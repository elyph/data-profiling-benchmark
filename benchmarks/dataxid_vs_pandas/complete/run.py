"""DataXID vs Pandas — Complete Mode Benchmark"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import gc
from benchmarks.common import generate_synthetic_data, profile_dataxid, profile_pandas
from benchmarks.common import plot_speed, plot_ram

ROW_COUNTS = [100_000, 500_000, 1_000_000, 2_000_000]
N_RUNS = 3

print("=" * 55)
print("  DataXID vs Pandas — COMPLETE Mode Benchmark")
print("  (Korelasyon + Etkileşim + Karakter Analizi dahil)")
print("=" * 55)

dx_times, dx_time_errs = [], []
pd_times, pd_time_errs = [], []
dx_mems, dx_mem_errs = [], []
pd_mems, pd_mem_errs = [], []

for rows in ROW_COUNTS:
    df = generate_synthetic_data(rows, backend="pandas")
    print(f"\n[+] {rows:,} satır ({len(df.columns)} kolon)")

    print(f"--> DataXID COMPLETE...")
    t_avg, t_std, m_avg, m_std = profile_dataxid(df, mode="complete", n_runs=N_RUNS)
    dx_times.append(t_avg); dx_time_errs.append(t_std)
    dx_mems.append(m_avg); dx_mem_errs.append(m_std)
    print(f"    {t_avg:.1f}s ± {t_std:.1f} | {m_avg:.1f}MB ± {m_std:.1f}")

    print(f"--> Pandas COMPLETE...")
    t_avg, t_std, m_avg, m_std = profile_pandas(df, mode="complete", n_runs=N_RUNS)
    pd_times.append(t_avg); pd_time_errs.append(t_std)
    pd_mems.append(m_avg); pd_mem_errs.append(m_std)
    if t_avg > 0:
        print(f"    {t_avg:.1f}s ± {t_std:.1f} | {m_avg:.1f}MB ± {m_std:.1f}")
    else:
        print(f"    CRASHED (OOM?)")

    del df; gc.collect()

# Özet
print("\n" + "=" * 75)
print(f"{'Satır':>12}  {'DX Süre':>12}  {'PD Süre':>12}  {'DX RAM':>12}  {'PD RAM':>12}  {'Fark':>10}")
print("-" * 75)
for i, rows in enumerate(ROW_COUNTS):
    dx_t = dx_times[i]; pd_t = pd_times[i]; dx_m = dx_mems[i]; pd_m = pd_mems[i]
    if pd_t > 0 and dx_t > 0:
        speedup = f"{pd_t/dx_t:.1f}x" if dx_t < pd_t else f"-{dx_t/pd_t:.1f}x"
        memup = f"{pd_m/dx_m:.1f}x" if dx_m < pd_m else f"-{dx_m/pd_m:.1f}x"
        diff = f"S:{speedup} M:{memup}"
    else:
        diff = "CRASHED"
    print(f"{rows:>12,}  {dx_t:>8.1f}s±{dx_time_errs[i]:.1f}  {pd_t:>8.1f}s±{pd_time_errs[i]:.1f}  {dx_m:>8.1f}M±{dx_mem_errs[i]:.1f}  {pd_m:>8.1f}M±{pd_mem_errs[i]:.1f}  {diff:>10}")
print("=" * 75)

# Grafikler
speed_data = {
    "DataXID": (dx_times, dx_time_errs),
    "Pandas": (pd_times, pd_time_errs),
}
ram_data = {
    "DataXID": (dx_mems, dx_mem_errs),
    "Pandas": (pd_mems, pd_mem_errs),
}

plot_speed(speed_data, ROW_COUNTS, title_suffix="Complete Mode")
plot_ram(ram_data, ROW_COUNTS, title_suffix="Complete Mode")
print("\nComplete mode benchmark tamamlandı.")
