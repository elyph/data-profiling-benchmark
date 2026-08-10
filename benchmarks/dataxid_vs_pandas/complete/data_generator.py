"""Sentetik Veri Üretici — Pandas için (string[pyarrow] optimize)"""

import pandas as pd
import numpy as np


def generate_dummy_data(n_rows):
    print(f"\n[+] {n_rows:,} satırlık sentetik veri üretiliyor (Pandas)...")
    np.random.seed(42)

    data = {f"num_col_{i}": np.random.randn(n_rows).astype(np.float32) for i in range(5)}
    df = pd.DataFrame(data)

    for i in range(3):
        df[f"cat_col_{i}"] = pd.Series(
            np.random.choice(["A", "B", "C", "D"], n_rows), dtype="string[pyarrow]"
        )

    for i in range(2):
        df[f"bool_col_{i}"] = np.random.choice([True, False], n_rows)

    return df
