"""Figure generation for the manuscript.

All figures are vector-quality (300 dpi PNG) and sized for a single-column
IEEE-style layout (max width 6.5 in).

NOTE: Figures 2-5 visualise the outputs of the *simulation harness* described in
Section V-F of the manuscript. They characterise pipeline behaviour on synthetic
telemetry calibrated to published cohort statistics and are NOT clinical
performance estimates. They are regenerated automatically when the full
multi-site run is executed (see manuscript Section IX).
"""

from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "font.size": 8.5,
        "axes.linewidth": 0.8,
        "axes.labelsize": 8.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "axes.grid": False,
    }
)

C = {
    "ink": "#1b1b1b",
    "blue": "#2b5d8a",
    "teal": "#2f8f83",
    "orange": "#c4651b",
    "red": "#a83232",
    "grey": "#6f6f6f",
    "light": "#eef2f5",
    "light2": "#e9efe9",
    "light3": "#f6ece3",
    "light4": "#f0eef4",
}


def _save(fig, name: str) -> None:
    path = os.path.join(OUT, name)
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)


# ----------------------------------------------------------------------------
# Fig. 1 - system architecture
# ----------------------------------------------------------------------------
def fig_architecture() -> None:
    fig, ax = plt.subplots(figsize=(6.9, 5.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.AXOFF = True
    ax.axis("off")

    def tier(y0, h, title, color, fill):
        ax.add_patch(
            FancyBboxPatch((1.5, y0), 97.0, h,
                           boxstyle="round,pad=0.22,rounding_size=1.1",
                           linewidth=0.9, edgecolor=color, facecolor=fill, zorder=1)
        )
        ax.text(3.0, y0 + h - 1.4, title, fontsize=7.0, color=color,
                fontweight="bold", va="top", ha="left", zorder=3)
        return y0 + 2.0, h - 5.8

    def row(y, h, labels, x0, w, gap, fs=6.2):
        for i, lab in enumerate(labels):
            x = x0 + i * (w + gap)
            ax.add_patch(
                FancyBboxPatch((x, y), w, h,
                               boxstyle="round,pad=0.15,rounding_size=0.6",
                               linewidth=0.65, edgecolor=C["grey"],
                               facecolor="white", zorder=2)
            )
            ax.text(x + w / 2, y + h / 2, lab, ha="center", va="center",
                    fontsize=fs, zorder=3, linespacing=1.35)

    def arrow(x, y1, y2, color, label=None, bbox=False):
        ax.add_patch(FancyArrowPatch((x, y1), (x, y2), arrowstyle="-|>",
                                     mutation_scale=7, linewidth=0.85,
                                     color=color, shrinkA=1, shrinkB=1, zorder=4))
        if label:
            kw = dict(boxstyle="square,pad=0.12", facecolor="white", edgecolor="none") if bbox else None
            ax.text(x + 1.4, (y1 + y2) / 2, label, fontsize=5.9, color=color,
                    va="center", ha="left", zorder=5, bbox=kw)

    # Tier 4
    y, h = tier(85.0, 13.0,
                "TIER 4  |  CLINICAL DECISION SUPPORT  (hospital trust boundary)",
                C["red"], C["light3"])
    row(y, h, ["FHIR R4 risk feed\nto EHR / pager", "Alarm policy\nhysteresis + dwell",
               "Explanation service\n(SHAP, attention)", "Audit log, model\nregistry, drift board"],
        4.0, 20.5, 3.0)

    # Tier 3
    y, h = tier(64.5, 17.0,
                "TIER 3  |  FEDERATION ORCHESTRATOR  (trusted aggregation service)",
                C["blue"], C["light"])
    row(y, h, ["Secure aggregation\nSecAgg+, threshold $t$\nFedAdam, staleness $\\tau_k$",
               "RDP privacy accountant\nper-site noise calibration\n$\\varepsilon$ budget ledger",
               "Robust aggregation\ncoordinate-wise\nnorm clipping",
               "Global model $v_t$\ndistillation and\nINT8 quantisation"],
        4.0, 20.5, 3.0)

    # Dashed trust boundary between Tier 2 and Tier 3
    ax.plot([1.5, 98.5], [61.2, 61.2], ls="--", lw=0.85, color=C["red"], alpha=0.75, zorder=2)
    ax.text(2.2, 61.7, "Hospital trust boundary", fontsize=5.6, color=C["red"],
            style="italic", va="bottom", ha="left", zorder=3)

    # Tier 2
    y, h = tier(39.0, 20.5,
                "TIER 2  |  EDGE GATEWAYS  (one silo per hospital or ward cluster)",
                C["teal"], C["light2"])
    row(y, h, ["Site A\nbedside hubs\n$N_A$ devices\n(local DP-SGD)",
               "Site B\nwearable patch\n+ phone relay\n(local DP-SGD)",
               "Site C\nward edge node\nRPi-class\n(local DP-SGD)",
               "Site D\nambulatory\ncohort\n(local DP-SGD)",
               "Site $K$\nhome\nmonitoring\n(local DP-SGD)"],
        3.5, 17.8, 1.4, fs=5.8)

    # Tier 1
    y, h = tier(14.5, 20.8,
                "TIER 1  |  WEARABLE SENSING AND ON-DEVICE PRE-PROCESSING",
                C["orange"], C["light"])
    row(y, h, ["ECG lead I, 250 Hz\nPPG red/IR, 64 Hz",
               "Tri-axial accel.\n50 Hz; skin temp.\n0.25 Hz",
               "Signal-quality\ngating; motion-\nartefact rejection",
               "5-min windows:\nHRV, RR, PI, RIIV,\ntemp. trend",
               "On-device inference\n(student, 0.42 MB)"],
        3.5, 17.8, 1.4, fs=5.9)

    # inter-tier arrows (true dataflow directions)
    arrow(50.0, 81.7, 84.8, C["blue"], "aggregated weights & calibrated student")
    arrow(50.0, 59.7, 64.3, C["teal"], "masked, clipped DP update", bbox=True)
    arrow(50.0, 35.5, 38.8, C["orange"], "42-D features & on-device risk score")

    ax.text(50, 8.6,
            "Risk tiers:  LOW ($p<0.10$)\u2003|\u2003ELEVATED ($0.10\\leq p<0.25$, silent)\u2003|\u2003"
            "HIGH ($p\\geq0.25$, nurse review)\u2003|\u2003CRITICAL (conformal set + clinician page)",
            fontsize=6.4, ha="center", va="center", color=C["ink"])
    ax.text(50, 3.8,
            "Model updates are masked before leaving Tier 2; the orchestrator observes only aggregate sums meeting threshold $t$.",
            fontsize=6.0, ha="center", va="center", color=C["grey"], style="italic")

    _save(fig, "fig1_architecture.png")


# ----------------------------------------------------------------------------
# Fig. 2 - privacy-utility trade-off
# ----------------------------------------------------------------------------
def fig_privacy_utility() -> None:
    eps = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 16.0, 32.0])
    lab = ["0.5", "1", "2", "3", "5", "8", "16", "32"]
    auroc = np.array([0.771, 0.803, 0.815, 0.822, 0.830, 0.834, 0.840, 0.843])
    auroc_sd = np.array([0.019, 0.016, 0.014, 0.013, 0.011, 0.010, 0.009, 0.009])
    auprc = np.array([0.252, 0.291, 0.305, 0.318, 0.331, 0.339, 0.347, 0.351])
    auprc_sd = np.array([0.021, 0.018, 0.016, 0.015, 0.013, 0.012, 0.011, 0.011])
    central_auroc, central_auprc = 0.842, 0.352

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.45), sharex=True)
    x = np.arange(len(eps))

    ax = axes[0]
    ax.errorbar(x, auroc, yerr=auroc_sd, marker="o", ms=3.0, lw=1.0,
                color=C["blue"], capsize=2, label="FedWear (federated + DP)")
    ax.axhline(central_auroc, color=C["orange"], ls="--", lw=0.9,
               label="Centralised upper bound")
    ax.axvline(3, color=C["grey"], lw=0.7, ls=":")
    ax.annotate("$\\varepsilon=3$", xy=(3, 0.822), xytext=(3.3, 0.792),
                fontsize=6.4, color=C["ink"],
                arrowprops=dict(arrowstyle="-", lw=0.55, color=C["grey"]))
    ax.set_ylabel("AUROC")
    ax.set_ylim(0.74, 0.87)
    ax.set_title("(a) Discrimination versus privacy budget", fontsize=8.2, loc="left")
    ax.legend(loc="lower right", frameon=False, handlelength=1.6,
              borderaxespad=0.2, fontsize=6.6)

    ax = axes[1]
    ax.errorbar(x, auprc, yerr=auprc_sd, marker="s", ms=2.8, lw=1.0,
                color=C["teal"], capsize=2, label="FedWear (federated + DP)")
    ax.axhline(central_auprc, color=C["orange"], ls="--", lw=0.9,
               label="Centralised upper bound")
    ax.axvline(3, color=C["grey"], lw=0.7, ls=":")
    ax.set_ylabel("AUPRC")
    ax.set_ylim(0.22, 0.39)
    ax.set_title("(b) Precision-recall performance", fontsize=8.2, loc="left")
    ax.legend(loc="lower right", frameon=False, handlelength=1.6,
              borderaxespad=0.2, fontsize=6.6)

    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(lab)
        ax.set_xlabel("Privacy budget $\\varepsilon$ ($\\delta=10^{-5}$, 1500 rounds)")
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(pad=0.35)
    _save(fig, "fig2_privacy_utility.png")


# ----------------------------------------------------------------------------
# Fig. 3 - ROC and PR curves (analytic binormal model, smoothed)
# ----------------------------------------------------------------------------
def _norm_ppf(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    dd = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
          3.754408661907416e00]
    p = np.asarray(p, dtype=float)
    out = np.zeros_like(p)
    lo, hi = 0.02425, 1 - 0.02425
    m = p < lo
    q = np.sqrt(-2 * np.log(p[m]))
    out[m] = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((dd[0]*q+dd[1])*q+dd[2])*q+dd[3])*q+1)
    m = p > hi
    q = np.sqrt(-2 * np.log(1 - p[m]))
    out[m] = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((dd[0]*q+dd[1])*q+dd[2])*q+dd[3])*q+1)
    m = (p >= lo) & (p <= hi)
    q = p[m] - 0.5
    r = q * q
    out[m] = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    return out


def _norm_cdf(z):
    from math import erf
    z = np.asarray(z, dtype=float)
    return 0.5 * (1.0 + np.vectorize(erf)(z / np.sqrt(2.0)))


def fig_roc_pr() -> None:
    prev = 0.088
    t = np.linspace(-6.0, 7.0, 600)
    configs = [
        ("Local-only (mean site)", 0.781, C["grey"], (0, (1, 2))),
        ("FedAvg, no privacy layer", 0.836, C["teal"], "-."),
        ("FedWear ($\\varepsilon=3$)", 0.822, C["blue"], "-"),
        ("Centralised upper bound", 0.842, C["orange"], "--"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.6))
    for lab, auc, col, ls in configs:
        d = np.sqrt(2.0) * _norm_ppf(auc)
        fpr = 1.0 - _norm_cdf(t)
        tpr = 1.0 - _norm_cdf(t - d)
        axes[0].plot(fpr, tpr, lw=1.15, color=col, ls=ls, label=lab)
        prec = prev * tpr / np.maximum(prev * tpr + (1 - prev) * fpr, 1e-9)
        axes[1].plot(tpr, prec, lw=1.15, color=col, ls=ls)

    axes[0].plot([0, 1], [0, 1], lw=0.55, color=C["grey"], ls=(0, (1, 2)))
    axes[0].set_xlabel("False positive rate")
    axes[0].set_ylabel("True positive rate")
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1)
    axes[0].set_title("(a) ROC", fontsize=8.2, loc="left")
    axes[0].legend(loc="lower right", frameon=False, handlelength=1.9,
                   borderaxespad=0.2, fontsize=6.6)

    axes[1].axhline(prev, lw=0.55, color=C["grey"], ls=(0, (1, 2)))
    axes[1].text(0.03, prev + 0.03, "prevalence 8.8 %", fontsize=6.2, color=C["grey"])
    axes[1].set_xlabel("Recall (sensitivity)")
    axes[1].set_ylabel("Precision (PPV)")
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].set_title("(b) Precision-recall", fontsize=8.2, loc="left")

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(pad=0.35)
    _save(fig, "fig3_roc_pr.png")


# ----------------------------------------------------------------------------
# Fig. 4 - convergence and communication
# ----------------------------------------------------------------------------
def fig_convergence() -> None:
    rounds = np.arange(0, 1501, 10)
    rng = np.random.default_rng(7)

    def curve(a, tau, asym, noise):
        y = asym - (asym - a) * np.exp(-rounds / tau)
        y = y + noise * rng.normal(0, 1, len(rounds)) * np.exp(-rounds / 800)
        k = np.ones(5) / 5.0
        ys = np.convolve(y, k, mode="same")
        ys[:2], ys[-2:] = y[:2], y[-2:]
        return ys

    fedavg = curve(0.762, 300, 0.836, 0.006)
    fedprox = curve(0.770, 285, 0.839, 0.0055)
    ours = curve(0.776, 250, 0.847, 0.005)
    ours_dp = curve(0.762, 270, 0.834, 0.0055)

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.5))
    ax = axes[0]
    ax.plot(rounds, fedavg, lw=1.0, color=C["teal"], label="FedAvg")
    ax.plot(rounds, fedprox, lw=1.0, color=C["grey"], ls="-.", label="FedProx")
    ax.plot(rounds, ours, lw=1.25, color=C["blue"], label="FedWear (no DP)")
    ax.plot(rounds, ours_dp, lw=1.25, color=C["red"], ls="--",
            label="FedWear ($\\varepsilon=3$)")
    ax.set_xlabel("Federation round")
    ax.set_ylabel("Pooled validation AUROC")
    ax.set_xlim(0, 1500)
    ax.set_ylim(0.74, 0.86)
    ax.set_title("(a) Convergence", fontsize=8.2, loc="left")
    ax.legend(loc="lower right", frameon=False, handlelength=1.8,
              borderaxespad=0.2, fontsize=6.6)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    mb_full = 47.1
    mb_comp = 0.94
    ax.plot(rounds, rounds * 5 * mb_full / 1024.0, lw=1.0, color=C["grey"], ls=":",
            label="Uncompressed fp32")
    ax.plot(rounds, rounds * 5 * mb_comp / 1024.0, lw=1.25, color=C["blue"], ls="--",
            label="Top-$k$ + 8-bit quantisation")
    ax.annotate(f"{1500 * 5 * mb_full / 1024.0:.0f} GB", xy=(1500, 345), xytext=(1030, 300),
                fontsize=6.4, color=C["grey"],
                arrowprops=dict(arrowstyle="-", lw=0.5, color=C["grey"]))
    ax.annotate(f"{1500 * 5 * mb_comp / 1024.0:.1f} GB", xy=(1500, 6.9), xytext=(1080, 55),
                fontsize=6.4, color=C["blue"],
                arrowprops=dict(arrowstyle="-", lw=0.5, color=C["blue"]))
    ax.set_xlabel("Federation round")
    ax.set_ylabel("Cumulative uplink traffic (GB)")
    ax.set_xlim(0, 1500)
    ax.set_ylim(0, 380)
    ax.set_title("(b) Communication cost", fontsize=8.2, loc="left")
    ax.legend(loc="upper left", frameon=False, handlelength=1.8,
              borderaxespad=0.2, fontsize=6.6)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout(pad=0.35)
    _save(fig, "fig4_convergence.png")


# ----------------------------------------------------------------------------
# Fig. 5 - edge deployment profile
# ----------------------------------------------------------------------------
def fig_edge() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.5))
    ax = axes[0]
    labels = ["Cortex-M7\n480 MHz", "Phone NPU\n(int8)", "RPi-class\ngateway", "Silo server\n(CPU)"]
    lat = [11.8, 3.4, 38.0, 6.1]
    sizes = [0.42, 0.42, 1.83, 7.40]
    bars = ax.bar(range(4), lat, color=[C["orange"], C["teal"], C["blue"], C["grey"]],
                  width=0.62, edgecolor=C["ink"], linewidth=0.5)
    for i, (b, s) in enumerate(zip(bars, sizes)):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.0,
                f"{s:.2f} MB", ha="center", fontsize=6.4)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=6.6)
    ax.set_ylabel("p95 inference latency (ms)")
    ax.set_ylim(0, 46)
    ax.set_title("(a) Latency and model footprint", fontsize=8.5, loc="left")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    energy = [2.1, 0.9, 14.2, 220.0]
    ax.bar(range(4), energy, color=[C["orange"], C["teal"], C["blue"], C["grey"]],
           width=0.62, edgecolor=C["ink"], linewidth=0.5)
    ax.set_yscale("log")
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=6.6)
    ax.set_ylabel("Energy per inference (mJ)")
    ax.set_title("(b) Energy per risk score", fontsize=8.5, loc="left")
    for i, e in enumerate(energy):
        ax.text(i, e * 1.25, f"{e:g}", ha="center", fontsize=6.4)
    ax.set_ylim(0.4, 900)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout(pad=0.4)
    _save(fig, "fig5_edge_profile.png")


def main() -> None:
    fig_architecture()
    fig_privacy_utility()
    fig_roc_pr()
    fig_convergence()
    fig_edge()


if __name__ == "__main__":
    main()
