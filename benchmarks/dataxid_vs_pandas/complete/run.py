"""DataXID vs Pandas — Complete Mode Benchmark Ana Döngü (süre + RAM)"""

import gc
from data_generator import generate_dummy_data
from benchmark_runner import run_benchmarks
from visualizer import draw_charts

# Complete mode ağır → Pandas OOM yapmadan ölçek küçük tutuldu
ROW_COUNTS = [100_000, 500_000, 1_000_000, 2_000_000]
dataxid_times, pandas_times = [], []
dataxid_mems, pandas_mems = [], []

print("=" * 55)
print("  DataXID vs Pandas — COMPLETE Mode Benchmark")
print("  (Korelasyon + Etkileşim + Karakter Analizi dahil)")
print("=" * 55)

for rows in ROW_COUNTS:
    df = generate_dummy_data(rows)
    dx_time, pd_time, dx_mem, pd_mem = run_benchmarks(df, rows)
    dataxid_times.append(dx_time)
    pandas_times.append(pd_time)
    dataxid_mems.append(dx_mem)
    pandas_mems.append(pd_mem)
    del df
    gc.collect()

# Özet
print("\n" + "=" * 75)
print(f"{'Satır':>12}  {'DX Süre':>10}  {'PD Süre':>10}  {'DX RAM':>10}  {'PD RAM':>10}  {'Fark':>10}")
print("-" * 75)
for rows, dx, pd_t, dxm, pdm in zip(ROW_COUNTS, dataxid_times, pandas_times, dataxid_mems, pandas_mems):
    if pd_t > 0:
        speedup = f"{pd_t/dx:.1f}x" if dx < pd_t else f"-{dx/pd_t:.1f}x"
        memup = f"{pdm/dxm:.1f}x" if dxm < pdm else f"-{dxm/pdm:.1f}x"
        diff = f"S:{speedup} M:{memup}"
    else:
        diff = "CRASHED"
    print(f"{rows:>12,}  {dx:>8.1f}s  {pd_t:>8.1f}s  {dxm:>8.1f}M  {pdm:>8.1f}M  {diff:>10}")
print("=" * 75)

draw_charts(ROW_COUNTS, dataxid_times, pandas_times, dataxid_mems, pandas_mems)
print("\nComplete mode benchmark tamamlandı.")
