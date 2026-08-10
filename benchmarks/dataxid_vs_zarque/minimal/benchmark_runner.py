"""Benchmark Runner — DataXID ve Zarque süre ölçümü"""

import time
import gc
import polars as pl
from dataxid_profiling import ProfileReport as DataxidProfile, ProfileConfig
from zarque_profiling import ProfileReport as ZarqueProfile


def run_benchmarks(data_dict, rows):
    df = pl.DataFrame(data_dict)
    n_cols = len(df.columns)
    print(f"    > {n_cols} kolon, {df.estimated_size('mb'):.1f} MB tahmini boyut")

    # --- DataXID ---
    print(f"--> DataXID ({rows:,} satır)...")
    dx_config = ProfileConfig(title=f"DataXID {rows}", mode="overview")
    t0 = time.perf_counter()
    dx_report = DataxidProfile(df, config=dx_config)
    dx_report.to_dict()
    dx_time = time.perf_counter() - t0
    print(f"    Süre: {dx_time:.1f} sn")
    del dx_report
    gc.collect()

    # --- Zarque ---
    print(f"--> Zarque ({rows:,} satır)...")
    t0 = time.perf_counter()
    try:
        zq_report = ZarqueProfile(df, minimal=True, title=f"Zarque {rows}")
        zq_report.get_description()
        zq_time = time.perf_counter() - t0
        print(f"    Süre: {zq_time:.1f} sn")
        del zq_report
    except Exception as e:
        print(f"    [!] Hata: {e}")
        zq_time = 0

    gc.collect()

    if zq_time > 0:
        if dx_time < zq_time:
            print(f"    >> DataXID {zq_time/dx_time:.1f}x daha hızlı")
        else:
            print(f"    >> Zarque {dx_time/zq_time:.1f}x daha hızlı")

    return dx_time, zq_time
