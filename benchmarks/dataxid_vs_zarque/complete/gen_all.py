"""HTML Rapor Karşılaştırması — DataXID vs Zarque vs Pandas (Telco, Complete)
Kullanım: python gen_all.py
"""

import os, polars as pl, pandas as pd

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "benchmark_outputs", "html_compare"))
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

DS = os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "telco_churn.csv")
df_pl = pl.read_csv(DS, null_values=["", " "])
df_pd = pd.read_csv(DS)
print(f"Telco Churn: {df_pl.height} satır, {df_pl.width} kolon")

# ---- DataXID ----
from dataxid_profiling import ProfileReport as DX, ProfileConfig
print("\n[1/3] DataXID COMPLETE HTML...")
dx = DX(df_pl, config=ProfileConfig(title="DataXID — Telco Churn (Complete)", mode="complete"))
dx.to_html(os.path.join(OUTPUT_DIR, "dataxid_complete.html"))
print("  OK")

# ---- Zarque ----
from zarque_profiling import ProfileReport as ZQ
print("[2/3] Zarque COMPLETE HTML...")
zq = ZQ(df_pd, minimal=False, title="Zarque — Telco Churn (Complete)")
with open(os.path.join(OUTPUT_DIR, "zarque_complete.html"), "w", encoding="utf-8") as f:
    f.write(zq.to_html())
print("  OK")

# ---- Pandas ----
from ydata_profiling import ProfileReport as PD
print("[3/3] Pandas COMPLETE HTML...")
pd_rep = PD(df_pd, title="Pandas — Telco Churn (Complete)", minimal=False)
with open(os.path.join(OUTPUT_DIR, "pandas_complete.html"), "w", encoding="utf-8") as f:
    f.write(pd_rep.to_html())
print("  OK")

print(f"\nHepsi hazır: {OUTPUT_DIR}")
for f in os.listdir(OUTPUT_DIR):
    print(f"  {f}")
