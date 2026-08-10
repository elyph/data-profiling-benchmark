"""DataXID vs Zarque — Complete Mode Benchmark (süre + RAM)"""

import time, gc, os, numpy as np, polars as pl, psutil
from dataxid_profiling import ProfileReport as DX, ProfileConfig
from zarque_profiling import ProfileReport as ZQ
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import platform

ROW_COUNTS = [100_000, 500_000, 1_000_000]
dx_times, zq_times, dx_mems, zq_mems = [], [], [], []

print("=" * 55)
print("  DataXID vs Zarque — COMPLETE Mode Benchmark")
print("=" * 55)


def gen(n_rows, seed=42):
    rng = np.random.default_rng(seed)
    d = {}
    for i in range(5):
        d[f"num_col_{i}"] = rng.standard_normal(n_rows).astype(np.float32)
    for i in range(3):
        d[f"cat_col_{i}"] = rng.choice(["A","B","C","D"], n_rows).tolist()
    for i in range(2):
        d[f"bool_col_{i}"] = rng.choice([True,False], n_rows).tolist()
    return pl.DataFrame(d)


def mem():
    return psutil.Process(os.getpid()).memory_info().rss / (1024*1024)


for rows in ROW_COUNTS:
    df = gen(rows)
    print(f"\n[+] {rows:,} satır, {df.estimated_size('mb'):.1f} MB")

    # DataXID
    print(f"  DX...", end=" ")
    mb = mem(); t0 = time.perf_counter()
    dx = DX(df, config=ProfileConfig(title=f"DX {rows}", mode="complete"))
    dx.to_dict()
    t_dx = time.perf_counter() - t0
    m_dx = max(0, mem() - mb)
    print(f"{t_dx:.1f}s / {m_dx:.0f}MB")

    # Zarque
    print(f"  ZQ...", end=" ")
    mb = mem(); t0 = time.perf_counter()
    try:
        zq = ZQ(df, minimal=False, title=f"ZQ {rows}")
        zq.get_description()
        t_zq = time.perf_counter() - t0
        m_zq = max(0, mem() - mb)
        print(f"{t_zq:.1f}s / {m_zq:.0f}MB")
    except Exception as e:
        print(f"CRASH: {str(e)[:80]}")
        t_zq = 0; m_zq = 0

    dx_times.append(t_dx); zq_times.append(t_zq)
    dx_mems.append(m_dx); zq_mems.append(m_zq)
    del df, dx; gc.collect()

# Özet
print("\n" + "=" * 60)
print(f"{'Satır':>10} {'DX Süre':>8} {'ZQ Süre':>8} {'DX RAM':>8} {'ZQ RAM':>8}")
print("-" * 60)
for r, dt, zt, dm, zm in zip(ROW_COUNTS, dx_times, zq_times, dx_mems, zq_mems):
    print(f"{r:>10,} {dt:>7.1f}s {zt:>7.1f}s {dm:>7.0f}M {zm:>7.0f}M")

# ----- Grafik -----
def lbl(n):
    if n < 1_000_000: return f"{n//1000}K"
    return f"{n//1_000_000}M"

labels = [lbl(r) for r in ROW_COUNTS]
x = np.arange(len(labels)); w = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Speed
r1 = ax1.bar(x - w/2, dx_times, w, label="DataXID (Polars-native)", color="#4472C4")
r2 = ax1.bar(x + w/2, zq_times, w, label="Zarque (Polars-adapted)", color="#ED7D31")
ax1.set_ylabel("Süre (saniye)", fontweight="bold")
ax1.set_xlabel("Satır Sayısı", fontweight="bold")
ax1.set_title("DataXID vs Zarque — Complete Mode Hız", fontweight="bold", fontsize=12)
ax1.set_xticks(x); ax1.set_xticklabels(labels)
ax1.legend(loc="upper left", frameon=False); ax1.grid(axis="y", alpha=0.3)
ax1.bar_label(r1, padding=3, fmt="%.1f")
for rect in r2:
    h = rect.get_height()
    lbl_txt = "CRASHED" if h == 0 else f"{h:.1f}"
    c = "red" if h == 0 else "black"
    ax1.annotate(lbl_txt, xy=(rect.get_x()+rect.get_width()/2, h),
                  xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                  color=c, fontweight="bold" if h==0 else "normal")

# RAM
r3 = ax2.bar(x - w/2, dx_mems, w, label="DataXID", color="#70AD47")
r4 = ax2.bar(x + w/2, zq_mems, w, label="Zarque", color="#FFC000")
ax2.set_ylabel("RAM (MB)", fontweight="bold")
ax2.set_xlabel("Satır Sayısı", fontweight="bold")
ax2.set_title("DataXID vs Zarque — Complete Mode RAM", fontweight="bold", fontsize=12)
ax2.set_xticks(x); ax2.set_xticklabels(labels)
ax2.legend(loc="upper left", frameon=False); ax2.grid(axis="y", alpha=0.3)
ax2.bar_label(r3, padding=3, fmt="%.0f")
for rect in r4:
    h = rect.get_height()
    c = "red" if h == 0 else "black"
    ax2.annotate("CRASHED" if h==0 else f"{h:.0f}",
                  xy=(rect.get_x()+rect.get_width()/2, h),
                  xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                  color=c, fontweight="bold" if h==0 else "normal")

cpu = platform.processor() or "Unknown"; ram_gb = round(psutil.virtual_memory().total/(1024**3))
plt.figtext(0.5, 0.01, f"{cpu} | {ram_gb} GB RAM | Complete Mode", ha="center", fontsize=9)
plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("dx_vs_zq_complete.png", dpi=300)
plt.close()
print("\ndx_vs_zq_complete.png kaydedildi.")
