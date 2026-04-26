"""
render_harmonic_hires_light.py
Re-render exp_09c_harmonic_hires's heatmap from cached .npy data using a
light-on-white theme.  The original exp_09c renderer hardcodes a black
background suitable for screen viewing; for print this is expensive and
hard to read, so this utility produces a printer-friendly variant from
the same underlying data.

Inputs : data/exp_harmonic_hires_powermap.npy   (150 x 257, log10 power)
Outputs: figures/exp_harmonic_hires.pdf
         figures/exp_harmonic_hires.png

The Arnold-tongue / Farey-structure markers, theoretical-frequency
overlays, and resonance lock-in stars are reproduced with adjusted colours
for white background (dark blues/reds rather than cyans/yellows so the
overlays remain visible against the inferno colormap).

Run:  python src/utilities/render_harmonic_hires_light.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
from scipy.fft import rfftfreq


HERE     = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA     = os.path.join(ROOT, "data", "exp_harmonic_hires_powermap.npy")
FIG_DIR  = os.path.join(ROOT, "figures")
OUT_PDF  = os.path.join(FIG_DIR, "exp_harmonic_hires.pdf")
OUT_PNG  = os.path.join(FIG_DIR, "exp_harmonic_hires.png")

N_TICKS = 512
N_OMEGA = 150

# Resonance lock-in points (omega, f_lock, label)
RESONANCES = [
    (np.pi / 4, 3 / 8,  "4:1"),
    (np.pi / 3, 1 / 3,  "3:1"),
    (np.pi / 2, 0.25,   "2:1"),
]


def _theory_freqs(omega: float) -> dict[str, float]:
    f_zitt = omega / (2 * np.pi)
    return {
        "f_zitt"  : f_zitt,
        "f_vacuum": 0.5,
        "f_beat"  : abs(0.5 - f_zitt),
        "f_2nd"   : 2 * f_zitt,
        "f_3rd"   : 3 * f_zitt,
    }


def main() -> int:
    if not os.path.exists(DATA):
        print(f"ERROR: missing {DATA}", file=sys.stderr)
        return 1

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError:
        print("matplotlib not available", file=sys.stderr)
        return 1

    power_log = np.load(DATA)
    if power_log.shape != (N_OMEGA, N_TICKS // 2 + 1):
        print(f"ERROR: unexpected shape {power_log.shape}", file=sys.stderr)
        return 1

    omega  = np.linspace(0.0, np.pi, N_OMEGA + 2)[1:-1]
    freqs  = rfftfreq(N_TICKS)

    fig, ax = plt.subplots(figsize=(14, 10))
    # White background, dark text -- printer-friendly.
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    im = ax.imshow(
        power_log,
        aspect="auto",
        origin="lower",
        extent=[freqs[0], freqs[-1], 0, N_OMEGA],
        cmap="inferno",
        interpolation="bilinear",
    )
    cbar = plt.colorbar(im, ax=ax, label="log₁₀(spectral power)")
    cbar.ax.tick_params(colors="black")
    cbar.ax.yaxis.label.set_color("black")

    # Y-axis: label every 10th omega row in units of pi
    tick_idx  = np.arange(0, N_OMEGA, 10)
    tick_vals = omega[tick_idx]
    ax.set_yticks(tick_idx + 0.5)
    ax.set_yticklabels(
        [f"{o / np.pi:.3f}π" for o in tick_vals],
        color="black",
        fontsize=7,
    )

    # Theoretical-frequency overlays.  On white background, swap from the
    # neon palette to darker, more readable colours.
    overlay_colors = {
        "f_zitt"  : "#0d3b66",   # navy
        "f_vacuum": "#16a34a",   # forest green
        "f_beat"  : "#b45309",   # amber
        "f_2nd"   : "#7c2d12",   # dark rust
    }
    for i, w in enumerate(omega):
        y  = i + 0.5
        tf = _theory_freqs(w)
        for name, f in [("f_zitt", tf["f_zitt"]),
                        ("f_vacuum", tf["f_vacuum"]),
                        ("f_beat", tf["f_beat"]),
                        ("f_2nd", tf["f_2nd"])]:
            if 0 < f < 0.5:
                ax.plot(f, y, ".", color=overlay_colors[name],
                        markersize=2, alpha=0.75, zorder=5)
        if 0 < tf["f_3rd"] < 0.5:
            ax.plot(tf["f_3rd"], y, "s", color="#5b21b6",   # purple
                    markersize=1.5, alpha=0.75, zorder=5)

    # Lock-in stars (dark fill, light edge for contrast on inferno)
    for omega_res, f_lock, lbl in RESONANCES:
        i_res = int(np.argmin(np.abs(omega - omega_res)))
        y_res = i_res + 0.5
        ax.plot(f_lock, y_res, "*",
                color="white",
                markeredgecolor="black",
                markeredgewidth=0.8,
                markersize=14,
                zorder=6, alpha=0.95)
        ax.annotate(
            lbl,
            xy=(f_lock, y_res),
            xytext=(f_lock + 0.01, y_res + 1.2),
            color="black", fontsize=9, alpha=0.95, zorder=7,
        )

    legend_elements = [
        Line2D([0], [0], marker=".", color="w",
               markerfacecolor="#0d3b66", markeredgecolor="#0d3b66",
               label="$f_\\mathrm{zitt}$", markersize=8),
        Line2D([0], [0], marker=".", color="w",
               markerfacecolor="#16a34a", markeredgecolor="#16a34a",
               label="$f_\\mathrm{vacuum}$ (0.5)", markersize=8),
        Line2D([0], [0], marker=".", color="w",
               markerfacecolor="#b45309", markeredgecolor="#b45309",
               label="$f_\\mathrm{beat}$", markersize=8),
        Line2D([0], [0], marker=".", color="w",
               markerfacecolor="#7c2d12", markeredgecolor="#7c2d12",
               label="$f_\\mathrm{2nd}$", markersize=8),
        Line2D([0], [0], marker="s", color="w",
               markerfacecolor="#5b21b6", markeredgecolor="#5b21b6",
               label="$f_\\mathrm{3rd}$", markersize=6),
        Line2D([0], [0], marker="*", color="w",
               markerfacecolor="white", markeredgecolor="black",
               label="resonance lock-in", markersize=12),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8,
              facecolor="white", edgecolor="black",
              labelcolor="black", framealpha=0.95)

    ax.set_xlabel("Frequency (cycles / tick)", fontsize=11, color="black")
    ax.set_ylabel("Instruction frequency $\\omega$", fontsize=11, color="black")
    ax.set_title(
        "Harmonic Fingerprint -- High Resolution Omega Scan  (N=150)\n"
        "Spectral power of $\\mathrm{rgb\\_cmy\\_imbalance}$  "
        "--  Arnold tongue / Farey structure",
        fontsize=11, color="black",
    )
    ax.tick_params(colors="black")
    for spine in ax.spines.values():
        spine.set_edgecolor("black")

    plt.tight_layout()
    os.makedirs(FIG_DIR, exist_ok=True)
    plt.savefig(OUT_PDF, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"Saved: {OUT_PDF}")
    print(f"Saved: {OUT_PNG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
