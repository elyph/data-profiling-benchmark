"""Sentetik veri üretici — Polars ve Pandas backend desteği."""

import numpy as np


def generate_synthetic_data(n_rows, backend="polars", seed=42):
    """10 kolonlu sentetik veri: 5 sayısal (float32) + 3 kategorik + 2 boolean.

    backend="polars" → dict döndürür (pl.DataFrame(data_dict) ile kullanılır)
    backend="pandas"  → pd.DataFrame döndürür
    """
    print(f"\n[+] {n_rows:,} satırlık sentetik veri üretiliyor ({backend})...")

    if backend == "polars":
        return _generate_polars_dict(n_rows, seed)
    elif backend == "pandas":
        return _generate_pandas_df(n_rows, seed)
    else:
        raise ValueError(f"Bilinmeyen backend: {backend}. 'polars' veya 'pandas' kullanın.")


def _generate_polars_dict(n_rows, seed):
    rng = np.random.default_rng(seed)
    data = {}
    for i in range(5):
        data[f"num_col_{i}"] = rng.standard_normal(n_rows).astype(np.float32)
    cats = ["A", "B", "C", "D"]
    for i in range(3):
        data[f"cat_col_{i}"] = rng.choice(cats, n_rows).tolist()
    for i in range(2):
        data[f"bool_col_{i}"] = rng.choice([True, False], n_rows).tolist()
    return data


def generate_timeseries_data(n_rows, seed=42):
    """10 kolon: 5 numerik ZAMAN SERİSİ + 3 kategorik + 2 boolean (Polars dict).

    Numerik sütunlar lineer trend + küçük gürültü üretir. Lag-1 otokorelasyon
    ~1.0 olduğu için _detect_timeseries() eşiğini (0.7) garantili geçer ve ADF
    her sütunda tetiklenir. Böylece statsmodels maliyeti ölçülebilir.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_rows, dtype=np.float64)
    data = {}
    for i in range(5):
        noise = rng.standard_normal(n_rows) * 0.1
        data[f"ts_col_{i}"] = (t * (1 + i * 0.25) + noise).astype(np.float64)
    cats = ["A", "B", "C", "D"]
    for i in range(3):
        data[f"cat_col_{i}"] = rng.choice(cats, n_rows).tolist()
    for i in range(2):
        data[f"bool_col_{i}"] = rng.choice([True, False], n_rows).tolist()
    return data


def _generate_pandas_df(n_rows, seed):
    import pandas as pd

    np.random.seed(seed)
    data = {f"num_col_{i}": np.random.randn(n_rows).astype(np.float32) for i in range(5)}
    df = pd.DataFrame(data)
    for i in range(3):
        df[f"cat_col_{i}"] = pd.Series(
            np.random.choice(["A", "B", "C", "D"], n_rows), dtype="string[pyarrow]"
        )
    for i in range(2):
        df[f"bool_col_{i}"] = np.random.choice([True, False], n_rows)
    return df
