"""3 Araçlı Complete Mode Benchmark — DataXID vs Zarque vs Pandas

Aynı sentetik veriyle 3 profiler'ı tek script'te karşılaştırır.
n_runs=3 ile istatistiksel ölçüm (ortalama ± stddev) + error bar'lı grafik.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import gc
import polars as pl
from benchmarks.common import generate_synthetic_data, profile_dataxid, profile_pandas, profile_zarque
from benchmarks.common import plot_3way, ensure_output_dir

ROW_COUNTS = [100_000, 500_000, 1_000_000, 2_000_000]
N_RUNS = 3

print("=" * 60)
print("  DataXID vs Zarque vs Pandas — COMPLETE Mode")
print("  (3 araçlı karşılaştırma, n=5 istatistiksel)")
print("=" * 60)

# Her araç için ayrı listeler
dx_times, dx_time_errs, dx_mems, dx_mem_errs = [], [], [], []
zq_times, zq_time_errs, zq_mems, zq_mem_errs = [], [], [], []
pd_times, pd_time_errs, pd_mems, pd_mem_errs = [], [], [], []

for rows in ROW_COUNTS:
    data_dict = generate_synthetic_data(rows, backend="polars")
    df_pl = pl.DataFrame(data_dict)
    df_pd = generate_synthetic_data(rows, backend="pandas")

    print(f"\n{'=' * 55}")
    print(f"  {rows:,} satır ({df_pl.width} kolon, {df_pl.estimated_size('mb'):.1f} MB)")
    print(f"{'=' * 55}")

    # DataXID
    print(f"--> DataXID COMPLETE ({N_RUNS} run)...")
    t_avg, t_std, m_avg, m_std = profile_dataxid(df_pl, mode="complete", n_runs=N_RUNS)
    dx_times.append(t_avg); dx_time_errs.append(t_std)
    dx_mems.append(m_avg); dx_mem_errs.append(m_std)
    print(f"    {t_avg:.1f}s ± {t_std:.1f} | {m_avg:.1f}MB ± {m_std:.1f}")

    # Zarque
    print(f"--> Zarque COMPLETE ({N_RUNS} run)...")
    t_avg, t_std, m_avg, m_std = profile_zarque(df_pl, mode="complete", n_runs=N_RUNS)
    zq_times.append(t_avg); zq_time_errs.append(t_std)
    zq_mems.append(m_avg); zq_mem_errs.append(m_std)
    if t_avg > 0:
        print(f"    {t_avg:.1f}s ± {t_std:.1f} | {m_avg:.1f}MB ± {m_std:.1f}")
    else:
        print(f"    CRASHED")

    # Pandas
    print(f"--> Pandas COMPLETE ({N_RUNS} run)...")
    t_avg, t_std, m_avg, m_std = profile_pandas(df_pd, mode="complete", n_runs=N_RUNS)
    pd_times.append(t_avg); pd_time_errs.append(t_std)
    pd_mems.append(m_avg); pd_mem_errs.append(m_std)
    if t_avg > 0:
        print(f"    {t_avg:.1f}s ± {t_std:.1f} | {m_avg:.1f}MB ± {m_std:.1f}")
    else:
        print(f"    CRASHED (OOM?)")

    del df_pl, df_pd, data_dict; gc.collect()

# Özet tablosu
print("\n" + "=" * 85)
header = f"{'Satır':>12}  {'DX Süre':>12}  {'ZQ Süre':>12}  {'PD Süre':>12}  {'DX RAM':>10}  {'ZQ RAM':>10}  {'PD RAM':>10}"
print(header)
print("-" * 85)
for i, rows in enumerate(ROW_COUNTS):
    print(f"{rows:>12,}  "
          f"{dx_times[i]:>8.1f}s±{dx_time_errs[i]:.1f}  "
          f"{zq_times[i]:>8.1f}s±{zq_time_errs[i]:.1f}  "
          f"{pd_times[i]:>8.1f}s±{pd_time_errs[i]:.1f}  "
          f"{dx_mems[i]:>8.1f}M  "
          f"{zq_mems[i]:>8.1f}M  "
          f"{pd_mems[i]:>8.1f}M")
print("=" * 85)

# Karşılaştırma oranları
print("\n--- DataXID'ye göre oranlar ---")
print(f"{'Satır':>12}  {'vs Zarque':>15}  {'vs Pandas':>15}")
print("-" * 48)
for i, rows in enumerate(ROW_COUNTS):
    zq_speed = f"{zq_times[i]/dx_times[i]:.1f}x" if zq_times[i] > 0 and dx_times[i] > 0 else "-"
    pd_speed = f"{pd_times[i]/dx_times[i]:.1f}x" if pd_times[i] > 0 and dx_times[i] > 0 else "-"
    print(f"{rows:>12,}  {zq_speed:>15}  {pd_speed:>15}")

# Çıktı dizini
charts_dir = ensure_output_dir("charts/three_way")

# Grafikler (3-way)
speed_data = {
    "DataXID": (dx_times, dx_time_errs),
    "Zarque": (zq_times, zq_time_errs),
    "Pandas": (pd_times, pd_time_errs),
}
ram_data = {
    "DataXID": (dx_mems, dx_mem_errs),
    "Zarque": (zq_mems, zq_mem_errs),
    "Pandas": (pd_mems, pd_mem_errs),
}

plot_3way(speed_data, ROW_COUNTS, f"{charts_dir}/three_way_speed.png", chart_type="speed", title_suffix="Complete Mode")
plot_3way(ram_data, ROW_COUNTS, f"{charts_dir}/three_way_ram.png", chart_type="ram", title_suffix="Complete Mode")

print("\n3 araçlı complete mode benchmark tamamlandı.")
