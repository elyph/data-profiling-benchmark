"""Benchmark Runner — DataXID vs Zarque COMPLETE mode (süre + RAM)"""

import time
import gc
import os
import psutil
import polars as pl
from dataxid_profiling import ProfileReport as DataxidProfile, ProfileConfig
from zarque_profiling import ProfileReport as ZarqueProfile


def get_memory_mb():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def run_benchmarks(data_dict, rows):
    df = pl.DataFrame(data_dict)
    n_cols = len(df.columns)
    print(f"    > {n_cols} kolon, {df.estimated_size('mb'):.1f} MB tahmini boyut")

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

    # --- Zarque (complete / minimal=False) ---
    print(f"--> Zarque COMPLETE ({rows:,} satır)...")
    mem_before = get_memory_mb()
    t0 = time.perf_counter()
    try:
        zq_report = ZarqueProfile(df, minimal=False, title=f"Zarque {rows}")
        zq_report.get_description()
        zq_time = time.perf_counter() - t0
        zq_mem = max(0, get_memory_mb() - mem_before)
        print(f"    Süre: {zq_time:.1f} sn | RAM: {zq_mem:.1f} MB")
        del zq_report
    except Exception as e:
        print(f"    [!] Hata: {e}")
        zq_time = 0
        zq_mem = 0

    gc.collect()

    if zq_time > 0:
        if dx_time < zq_time:
            print(f"    >> DataXID {zq_time/dx_time:.1f}x daha hızlı | {zq_mem/dx_mem:.1f}x daha az RAM")
        else:
            print(f"    >> Zarque {dx_time/zq_time:.1f}x daha hızlı | {dx_mem/zq_mem:.1f}x daha az RAM")

    return dx_time, zq_time, dx_mem, zq_mem
