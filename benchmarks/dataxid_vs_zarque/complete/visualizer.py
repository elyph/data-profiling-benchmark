"""Grafik — DataXID vs Zarque COMPLETE Mode Hız + RAM Karşılaştırması"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import platform
import psutil


def draw_charts(row_counts, dataxid_times, zarque_times, dataxid_mems, zarque_mems):
    _draw_speed(row_counts, dataxid_times, zarque_times)
    _draw_memory(row_counts, dataxid_mems, zarque_mems)


def _draw_speed(row_counts, dataxid_times, zarque_times):
    print("\n[+] Complete Mode hız grafiği çiziliyor...")
    labels = [f"{r//1_000_000}M" for r in row_counts]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))
    rects1 = ax.bar(x - width / 2, dataxid_times, width, label="DataXID (Polars-native)", color="#4472C4")
    rects2 = ax.bar(x + width / 2, zarque_times, width, label="Zarque (Polars-adapted)", color="#ED7D31")

    ax.set_ylabel("Süre (saniye)", fontweight="bold")
    ax.set_xlabel("Satır Sayısı", fontweight="bold")
    ax.set_title("DataXID vs Zarque — Complete Mode Hız (10 Kolon)", fontweight="bold", pad=20, fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="y", linestyle="-", alpha=0.3)

    ax.bar_label(rects1, padding=3, fmt="%.1f")
    for rect in rects2:
        h = rect.get_height()
        label = "CRASHED" if h == 0 else f"{h:.1f}"
        color = "red" if h == 0 else "black"
        ax.annotate(label, xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    color=color, fontweight="bold" if h == 0 else "normal")

    ram_gb = round(psutil.virtual_memory().total / (1024**3))
    cpu = platform.processor() or "Unknown CPU"
    plt.figtext(0.12, 0.02, f"Environment: {cpu} | {ram_gb} GB RAM | Complete Mode", ha="left", fontsize=9)
    plt.subplots_adjust(bottom=0.18)
    plt.savefig("benchmark_complete_speed.png", dpi=300)
    plt.close()
    print("    benchmark_complete_speed.png kaydedildi.")


def _draw_memory(row_counts, dataxid_mems, zarque_mems):
    print("[+] Complete Mode RAM grafiği çiziliyor...")
    labels = [f"{r//1_000_000}M" for r in row_counts]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))
    rects1 = ax.bar(x - width / 2, dataxid_mems, width, label="DataXID (Polars-native)", color="#70AD47")
    rects2 = ax.bar(x + width / 2, zarque_mems, width, label="Zarque (Polars-adapted)", color="#FFC000")

    ax.set_ylabel("Ekstra RAM (MB)", fontweight="bold")
    ax.set_xlabel("Satır Sayısı", fontweight="bold")
    ax.set_title("DataXID vs Zarque — Complete Mode RAM Karşılaştırması (10 Kolon)", fontweight="bold", pad=20, fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="y", linestyle="-", alpha=0.3)

    ax.bar_label(rects1, padding=3, fmt="%.1f")
    for rect in rects2:
        h = rect.get_height()
        label = "CRASHED" if h == 0 else f"{h:.1f}"
        color = "red" if h == 0 else "black"
        ax.annotate(label, xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    color=color, fontweight="bold" if h == 0 else "normal")

    plt.subplots_adjust(bottom=0.12)
    plt.savefig("benchmark_complete_ram.png", dpi=300)
    plt.close()
    print("    benchmark_complete_ram.png kaydedildi.")
