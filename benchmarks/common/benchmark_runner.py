"""Benchmark runner — DataXID, Pandas/YData, Zarque profiler'ları.

n_runs desteği ile istatistiksel ölçüm (ortalama ± stddev).
"""

import time
import gc
import os
import numpy as np
import psutil
import polars as pl
from dataxid_profiling import ProfileReport as DataxidProfile, ProfileConfig
from ydata_profiling import ProfileReport as PandasProfile
from zarque_profiling import ProfileReport as ZarqueProfile


def get_memory_mb():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def run_benchmark(profile_func, df, n_runs=1):
    """Bir profiler fonksiyonunu n_runs kez çalıştırır, ortalama ve stddev döndürür.

    profile_func: (df) -> None çağrısı. İçinde kendi süre+RPM ölçümünü yapmaz,
                  sadece profiler'ı çalıştırır. Süre burada ölçülür.
    df: Polars veya Pandas DataFrame.

    Returns: (time_avg, time_std, mem_avg, mem_std)
    """
    times = []
    mems = []

    for run in range(n_runs):
        if n_runs > 1:
            print(f"    Run {run + 1}/{n_runs}...", end=" ")
        gc.collect()
        mem_before = get_memory_mb()
        t0 = time.perf_counter()

        try:
            profile_func(df)
        except Exception as e:
            print(f"\n    [!] Hata: {e}")
            if run == 0:
                return 0, 0, 0, 0
            continue

        elapsed = time.perf_counter() - t0
        mem_delta = max(0, get_memory_mb() - mem_before)
        times.append(elapsed)
        mems.append(mem_delta)

        if n_runs > 1:
            print(f"{elapsed:.1f}s / {mem_delta:.1f}MB")

    if not times:
        return 0, 0, 0, 0

    time_avg = float(np.mean(times))
    time_std = float(np.std(times, ddof=1)) if len(times) > 1 else 0.0
    mem_avg = float(np.mean(mems))
    mem_std = float(np.std(mems, ddof=1)) if len(mems) > 1 else 0.0

    return time_avg, time_std, mem_avg, mem_std


def _to_polars(df_or_dict):
    if isinstance(df_or_dict, dict):
        return pl.DataFrame(df_or_dict)
    if isinstance(df_or_dict, pl.DataFrame):
        return df_or_dict
    return pl.from_pandas(df_or_dict)


def profile_dataxid(df_or_dict, mode="complete", n_runs=1):
    """DataXID profiler wrapper. Polars veya Pandas df kabul eder."""
    df = _to_polars(df_or_dict)
    config = ProfileConfig(title="DataXID", mode=mode)

    def _run(_df):
        report = DataxidProfile(_df, config=config)
        report.to_dict()
        del report

    return run_benchmark(_run, df, n_runs=n_runs)


def profile_dataxid_ts_ab(df_or_dict, mode="complete", n_runs=1):
    """DataXID A/B: (ts_active=True, ts_active=False) → (on, off) iki ölçüm döndürür.

    OFF önce koşulur; böylece OFF ölçümü statsmodels yüklenmeden alınır.
    ON ilk run'da import + ADF maliyetini yakalar.
    """
    df = _to_polars(df_or_dict)

    def make_run(ts_active):
        config = ProfileConfig(title="DataXID", mode=mode, ts_active=ts_active)

        def _run(_df):
            report = DataxidProfile(_df, config=config)
            report.to_dict()
            del report

        return _run

    off = run_benchmark(make_run(False), df, n_runs=n_runs)
    on = run_benchmark(make_run(True), df, n_runs=n_runs)
    return on, off


def profile_pandas(df, mode="complete", n_runs=1):
    """Pandas/YData profiler wrapper. pandas DataFrame bekler."""
    minimal = mode != "complete"

    def _run(_df):
        report = PandasProfile(_df, title="Pandas", minimal=minimal)
        report.get_description()
        del report

    return run_benchmark(_run, df, n_runs=n_runs)


def profile_zarque(df_or_dict, mode="complete", n_runs=1):
    """Zarque profiler wrapper. Polars veya Pandas df kabul eder."""
    df = _to_polars(df_or_dict)
    minimal = mode != "complete"

    def _run(_df):
        report = ZarqueProfile(_df, minimal=minimal, title="Zarque")
        report.get_description()
        del report

    return run_benchmark(_run, df, n_runs=n_runs)
