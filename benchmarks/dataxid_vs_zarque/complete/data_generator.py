"""Sentetik Veri Üretici — Complete Mode için daha küçük scale (1M→10M)"""

import numpy as np


def generate_dummy_data(n_rows, seed=42):
    print(f"\n[+] {n_rows:,} satırlık sentetik veri üretiliyor...")
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
