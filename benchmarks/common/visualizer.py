"""Grafik çizici — speed, RAM, ve 3-way karşılaştırma.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import platform
import psutil

from .utils import ensure_output_dir

COLORS = {
    "DataXID": "#4472C4",
    "Pandas": "#ED7D31",
    "Zarque": "#70AD47",
}

_LABEL_SHORT = {
    "DataXID": "DataXID (Polars-native)",
    "Pandas": "Pandas (YData)",
    "Zarque": "Zarque (Polars-adapted)",
}


def _format_label(n):
    if n >= 1_000_000:
        return f"{n // 1_000_000}M"
    return f"{n // 1_000}K"


def _make_chart(results, row_labels, output_path, chart_type, title_suffix=""):
    """results: {"ToolName": (values, errors), ...}
    row_labels: [100_000, 500_000, ...] — x ekseni etiketleri
    """
    tool_names = list(results.keys())
    n_tools = len(tool_names)
    n_groups = len(next(iter(results.values()))[0])

    values = {name: results[name][0] for name in tool_names}
    errors = {name: results[name][1] for name in tool_names}

    labels = [_format_label(r) for r in row_labels]
    x = np.arange(n_groups)
    width = 0.8 / n_tools

    fig, ax = plt.subplots(figsize=(11, 6))

    for i, name in enumerate(tool_names):
        offset = (i - (n_tools - 1) / 2) * width
        color = COLORS.get(name, "#999999")
        label = _LABEL_SHORT.get(name, name)

        err = errors[name] if any(e > 0 for e in errors[name]) else None
        r = ax.bar(x + offset, values[name], width,
                   label=label, color=color,
                   yerr=err, capsize=4, error_kw={"elinewidth": 1.5})

        for rect in r:
            h = rect.get_height()
            if h == 0:
                ax.annotate("CRASHED\n(OOM)",
                            xy=(rect.get_x() + rect.get_width() / 2, h),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom",
                            color="red", fontweight="bold")
            else:
                ax.bar_label([rect], padding=3, fmt="%.1f")

    ylabel = "Süre (saniye)" if chart_type == "speed" else "Ekstra RAM (MB)"
    ax.set_ylabel(ylabel, fontweight="bold")
    ax.set_xlabel("Satır Sayısı", fontweight="bold")

    others = [t for t in tool_names if t != "DataXID"]
    if others:
        title_vs = f"DataXID vs {' vs '.join(others)}"
    else:
        title_vs = tool_names[0]
    title = f"{title_vs} — {title_suffix} ({'Hız' if chart_type == 'speed' else 'RAM'}, 10 Kolon)"
    ax.set_title(title, fontweight="bold", pad=20, fontsize=12)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="y", linestyle="-", alpha=0.3)

    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
    cpu = platform.processor() or "Unknown CPU"
    plt.figtext(0.12, 0.02, f"Environment: {cpu} | {ram_gb} GB RAM | {title_suffix}",
                ha="left", fontsize=9)
    plt.subplots_adjust(bottom=0.18)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"    {output_path} kaydedildi.")


def plot_speed(results, row_labels, output_path=None, title_suffix="Complete Mode"):
    if output_path is None:
        output_path = f"{ensure_output_dir('charts/complete')}/benchmark_speed.png"
    _make_chart(results, row_labels, output_path, "speed", title_suffix)


def plot_ram(results, row_labels, output_path=None, title_suffix="Complete Mode"):
    if output_path is None:
        output_path = f"{ensure_output_dir('charts/complete')}/benchmark_ram.png"
    _make_chart(results, row_labels, output_path, "ram", title_suffix)


def plot_3way(results, row_labels, output_path, chart_type="speed", title_suffix="Complete Mode"):
    _make_chart(results, row_labels, output_path, chart_type, f"3-Way {title_suffix}")


def plot_ab(on_vals, off_vals, on_errs, off_errs, row_labels, output_path, chart_type="speed"):
    """DataXID TS AÇIK vs KAPALI — 2 bar gruplu karşılaştırma."""
    labels = [_format_label(r) for r in row_labels]
    x = np.arange(len(row_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))

    on_err = on_errs if any(e > 0 for e in on_errs) else None
    off_err = off_errs if any(e > 0 for e in off_errs) else None

    r1 = ax.bar(x - width / 2, on_vals, width, label="TS Aktif (ts_active=True)",
                color=COLORS["DataXID"], yerr=on_err, capsize=4,
                error_kw={"elinewidth": 1.5})
    r2 = ax.bar(x + width / 2, off_vals, width, label="TS Kapalı (ts_active=False)",
                color="#A5A5A5", yerr=off_err, capsize=4,
                error_kw={"elinewidth": 1.5})

    ax.bar_label(r1, padding=3, fmt="%.2f")
    ax.bar_label(r2, padding=3, fmt="%.2f")

    ylabel = "Süre (saniye)" if chart_type == "speed" else "Ekstra RAM (MB)"
    ax.set_ylabel(ylabel, fontweight="bold")
    ax.set_xlabel("Satır Sayısı", fontweight="bold")
    ax.set_title("DataXID ADF / Statsmodels Etkisi (Sentetik TS Veri, 10 Kolon)",
                 fontweight="bold", pad=20, fontsize=12)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="y", linestyle="-", alpha=0.3)

    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
    cpu = platform.processor() or "Unknown CPU"
    plt.figtext(0.12, 0.02, f"Environment: {cpu} | {ram_gb} GB RAM | {ylabel}",
                ha="left", fontsize=9)
    plt.subplots_adjust(bottom=0.18)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"    {output_path} kaydedildi.")
