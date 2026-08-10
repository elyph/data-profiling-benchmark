"""Benchmark Runner — DataXID vs Pandas COMPLETE mode (süre + RAM)"""

import time
import gc
import os
import psutil
from dataxid_profiling import ProfileReport as DataxidProfile, ProfileConfig
from ydata_profiling import ProfileReport as PandasProfile


def get_memory_mb():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def run_benchmarks(df, rows):
    n_cols = len(df.columns)
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"    > {n_cols} kolon, ~{mem_mb:.1f} MB tahmini boyut")

    # --- DataXID (complete) ---
    print(f"--> DataXID COMPLETE ({rows:,} satır)...")
    dx_config = ProfileConfig(title=f"DataXID {rows}", mode="complete")
    mem_before = get_memory_mb()
    t0 = time.perf_counter()
    dx_report = DataxidProfile(df, config=dx_config)
    dx_report.to_dict()
    dx_time = time.perf_counter() - t0
    dx_mem = max(0, get_memory_mb() - mem_before)
    print(f"    Süre: {dx_time:.1f} sn | RAM: {dx_mem:.1f} MB")
    del dx_report
    gc.collect()

    # --- Pandas / YData (complete / default) ---
    print(f"--> Pandas COMPLETE ({rows:,} satır)...")
    mem_before = get_memory_mb()
    t0 = time.perf_counter()
    try:
        pd_report = PandasProfile(df, title=f"Pandas {rows}", minimal=False)
        pd_report.get_description()
        pd_time = time.perf_counter() - t0
        pd_mem = max(0, get_memory_mb() - mem_before)
        print(f"    Süre: {pd_time:.1f} sn | RAM: {pd_mem:.1f} MB")
        del pd_report
    except Exception as e:
        print(f"    [!] Hata (OOM?): {e}")
        pd_time = 0
        pd_mem = 0

    gc.collect()

    if pd_time > 0:
        if dx_time < pd_time:
            print(f"    >> DataXID {pd_time/dx_time:.1f}x daha hızlı | {pd_mem/dx_mem:.1f}x daha az RAM")
        else:
            print(f"    >> Pandas {dx_time/pd_time:.1f}x daha hızlı | {dx_mem/pd_mem:.1f}x daha az RAM")

    return dx_time, pd_time, dx_mem, pd_mem
