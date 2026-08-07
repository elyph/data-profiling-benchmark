"""DataXID vs Zarque — Benchmark Ana Döngü"""

import gc
from data_generator import generate_dummy_data
from benchmark_runner import run_benchmarks
from visualizer import draw_comparison_chart

ROW_COUNTS = [1_000_000, 10_000_000, 25_000_000, 50_000_000, 75_000_000, 100_000_000]
dataxid_times, zarque_times = [], []

print("=" * 50)
print("  DataXID vs Zarque — Benchmark")
print("=" * 50)

for rows in ROW_COUNTS:
    data_dict = generate_dummy_data(rows)
    dx_time, zq_time = run_benchmarks(data_dict, rows)
    dataxid_times.append(dx_time)
    zarque_times.append(zq_time)
    del data_dict
    gc.collect()

# Özet
print("\n" + "=" * 55)
print(f"{'Satır':>12}  {'DataXID':>10}  {'Zarque':>10}  {'Fark':>10}")
print("-" * 55)
for rows, dx, zq in zip(ROW_COUNTS, dataxid_times, zarque_times):
    if zq > 0:
        if dx < zq:
            diff = f"DX {zq/dx:.1f}x"
        else:
            diff = f"ZQ {dx/zq:.1f}x"
    else:
        diff = "CRASHED"
    print(f"{rows:>12,}  {dx:>8.1f}s  {zq:>8.1f}s  {diff:>10}")
print("=" * 55)

draw_comparison_chart(ROW_COUNTS, dataxid_times, zarque_times)
print("\nBenchmark tamamlandı.")
