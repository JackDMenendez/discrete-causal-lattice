"""
plot_quantization_scan.py
Plots spontaneous quantization scan results for n=1 and/or n=2.

Reads output from exp_11_quantization_scan.py.

Default figure (when *_pdf.npy is present) — one panel per n-level:

  2D heatmap: x = k, y = r, colour = time-averaged P(r) normalised per
  k-column.  The bright spot marks where the electron spends its time.
  If the lattice selects the Bohr orbit, that spot falls exactly on the
  crosshair (k_Bohr, r_n).

  Overlaid as a twin-axis line: score_pdf (right axis, inverted so the
  minimum dips toward the bright spot).  score_com is shown as a dashed
  line for comparison.

  This is the paper figure.  It is dramatic because a single image shows:
    - the bright spot at (k_Bohr, r_n)
    - the score minimum coinciding with it
    - all other k values producing diffuse or misplaced distributions

Fallback (when pdf data is absent for a given n-level):
  Score-only panel for that n, with a note that PDF data is pending.

Classic figure (no PDF data at all, or --no-heatmap):
  Three-row layout: score comparison | component breakdown | P(r) overlays.

Usage:
  python plot_quantization_scan.py
  python plot_quantization_scan.py --n1
  python plot_quantization_scan.py --n2
  python plot_quantization_scan.py --out quantization_scan.pdf
  python plot_quantization_scan.py --no-heatmap   # classic three-row layout
  python plot_quantization_scan.py --n-curves 9   # for --no-heatmap mode
  python plot_quantization_scan.py --datadir path/to/npy/files
"""

import sys, os, argparse
import numpy as np

R1_APPROX    = 10.3
K_STEP_N1    = 0.0002
K_STEP_N2    = 0.001
N_PDF_CURVES = 7


# ── Data loading ──────────────────────────────────────────────────────────────

def load(n, datadir='.'):
    fname = os.path.join(datadir, f'quantization_scan_n{n}.npy')
    if not os.path.exists(fname):
        return None

    raw = np.load(fname)
    d = {
        'k':      raw[:, 0],
        'r_mean': raw[:, 1],
        'cv':     raw[:, 2],
        'r_bias': raw[:, 3],
    }
    if raw.shape[1] >= 8:
        d['score_com']       = raw[:, 4]
        d['inv_sharpness']   = raw[:, 5]
        d['peak_error']      = raw[:, 6]
        d['score_pdf']       = raw[:, 7]
    else:
        d['score_com']       = raw[:, 4]
        d['inv_sharpness']   = None
        d['peak_error']      = None
        d['score_pdf']       = None

    if raw.shape[1] >= 10:
        d['score_epoch_mean'] = raw[:, 8]
        d['score_epoch_std']  = raw[:, 9]
    else:
        d['score_epoch_mean'] = None
        d['score_epoch_std']  = None

    pdf_f   = os.path.join(datadir, f'quantization_scan_n{n}_pdf.npy')
    rbins_f = os.path.join(datadir, f'quantization_scan_n{n}_rbins.npy')
    d['pdf']   = np.load(pdf_f)   if os.path.exists(pdf_f)   else None
    d['rbins'] = np.load(rbins_f) if os.path.exists(rbins_f) else None

    return d


# ── Heatmap panel (main paper figure) ────────────────────────────────────────

def plot_heatmap(ax, data, n, k_step):
    """
    2D heatmap of P(r, k) with score overlaid on a twin axis.

    Each k-column of the PDF is normalised to its own maximum so the
    structure at every k value is visible regardless of total density.
    The bright spot at (k_Bohr, r_n) is the physical result.

    Falls back to a score-only plot when pdf data is absent.
    """
    import matplotlib.pyplot as plt
    r_n    = n**2 * R1_APPROX
    k_bohr = n / r_n
    k      = data['k']

    if data['pdf'] is None or data['rbins'] is None:
        # No PDF data — show score curve only
        score = data['score_pdf'] if data['score_pdf'] is not None else data['score_com']
        ax.plot(k, score, color='white', lw=2.0, label='score')
        ax.axvline(k_bohr, color='cyan', lw=1.5, ls='--',
                   label=f'Bohr $k_{n}$ = {k_bohr:.4f}')
        min_idx = int(np.argmin(score))
        ax.plot(k[min_idx], score[min_idx], 'o', color='cyan', ms=7, zorder=5)
        ax.annotate(f'min k={k[min_idx]:.4f}',
                    xy=(k[min_idx], score[min_idx]),
                    xytext=(k[min_idx] + 5*k_step, score[min_idx] + 0.01),
                    color='white', fontsize=8,
                    arrowprops=dict(arrowstyle='->', color='white', lw=0.8))
        ax.set_xlabel('k', fontsize=10)
        ax.set_ylabel('Score  (lower = better)', fontsize=10)
        ax.set_title(f'n={n}  score (PDF data pending — re-run exp_11 --n{n})',
                     fontsize=10)
        ax.legend(fontsize=8)
        return

    pdf    = data['pdf']    # (n_k, N_BINS)
    rbins  = data['rbins']  # (N_BINS,)

    # Normalise each k-column to [0, 1] so dim columns are not invisible
    col_max = pdf.max(axis=1, keepdims=True)
    col_max[col_max < 1e-12] = 1.0
    pdf_norm = pdf / col_max          # (n_k, N_BINS)

    # pcolormesh needs cell edges, not centres
    dk     = k[1] - k[0] if len(k) > 1 else k_step
    dr     = rbins[1] - rbins[0]
    k_edges = np.append(k - dk/2, k[-1] + dk/2)
    r_edges = np.append(rbins - dr/2, rbins[-1] + dr/2)

    mesh = ax.pcolormesh(k_edges, r_edges, pdf_norm.T,
                         cmap='hot', shading='flat',
                         vmin=0, vmax=1)

    # Bohr crosshair
    ax.axvline(k_bohr, color='cyan', lw=1.5, ls='--', alpha=0.9,
               label=f'Bohr $k_{n}$ = {k_bohr:.4f}')
    ax.axhline(r_n,    color='cyan', lw=1.5, ls='--', alpha=0.9,
               label=f'Bohr $r_{n}$ = {r_n:.1f}')
    ax.plot(k_bohr, r_n, '+', color='cyan', ms=14, mew=2, zorder=5)

    ax.set_xlabel('k  (angular momentum per unit radius)', fontsize=10)
    ax.set_ylabel('r  (lattice units)', fontsize=10)
    ax.set_title(f'n={n}  time-averaged $P(r,k)$\n'
                 f'Bright spot should land on crosshair at '
                 f'($k_{n}$={k_bohr:.4f}, $r_{n}$={r_n:.1f})',
                 fontsize=10)

    plt.colorbar(mesh, ax=ax, label='P(r) normalised per k-column')

    # Score overlay on twin axis (inverted: minimum dips toward bright spot)
    # Prefer epoch_mean (robust) over score_pdf when available.
    if data['score_epoch_mean'] is not None:
        score      = data['score_epoch_mean']
        score_label = 'score$_{\\rm epoch}$'
    elif data['score_pdf'] is not None:
        score      = data['score_pdf']
        score_label = 'score$_{\\rm pdf}$'
    else:
        score      = data['score_com']
        score_label = 'score$_{\\rm com}$'

    ax2 = ax.twinx()
    ax2.plot(k, score, color='white', lw=2.0, alpha=0.85,
             label=score_label, zorder=6)
    # Epoch std as shaded band
    if data['score_epoch_mean'] is not None and data['score_epoch_std'] is not None:
        ax2.fill_between(k,
                         score - data['score_epoch_std'],
                         score + data['score_epoch_std'],
                         color='white', alpha=0.15, zorder=5,
                         label='$\\pm$1 epoch std')
    elif data['score_pdf'] is not None:
        ax2.plot(k, data['score_com'], color='lightblue', lw=1.2,
                 ls='--', alpha=0.6, label='score$_{\\rm com}$', zorder=5)

    # Mark score minimum
    min_idx = int(np.argmin(score))
    ax2.plot(k[min_idx], score[min_idx], 'o', color='white', ms=7, zorder=7)
    ax2.annotate(f'min k={k[min_idx]:.4f}',
                 xy=(k[min_idx], score[min_idx]),
                 xytext=(k[min_idx] + 5*k_step, score[min_idx] + 0.01),
                 color='white', fontsize=8,
                 arrowprops=dict(arrowstyle='->', color='white', lw=0.8))

    ax2.set_ylabel('Score  (lower = better)', fontsize=10, color='white')
    ax2.tick_params(axis='y', colors='white')
    ax2.invert_yaxis()   # minimum dips toward the bright spot

    # Combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2,
               fontsize=8, loc='upper right',
               facecolor='#222222', labelcolor='white', framealpha=0.7)


# ── Classic three-row panels (fallback / --no-heatmap) ───────────────────────

def _bohr_vline(ax, k_bohr, k_step, n):
    ax.axvline(k_bohr, color='crimson', lw=1.5, ls='-',
               label=f'Bohr $k_{n}$ = {k_bohr:.4f}', zorder=4)
    ax.axvspan(k_bohr - k_step, k_bohr + k_step,
               alpha=0.10, color='crimson', zorder=3)


def _annotate_min(ax, k, score, k_step):
    idx = int(np.argmin(score))
    ax.plot(k[idx], score[idx], 'o', color='black', ms=6, zorder=6)
    ax.annotate(f'min k={k[idx]:.4f}',
                xy=(k[idx], score[idx]),
                xytext=(k[idx] + 5*k_step, score[idx] + 0.015),
                fontsize=8,
                arrowprops=dict(arrowstyle='->', color='black', lw=0.8))


def plot_scores(ax, data, n, k_step):
    r_n    = n**2 * R1_APPROX
    k_bohr = n / r_n
    k      = data['k']

    ax.plot(k, data['score_com'], color='steelblue', lw=2.0,
            label='score$_{\\rm com}$ = cv + r$_{\\rm bias}$')
    if data['score_epoch_mean'] is not None:
        ax.plot(k, data['score_epoch_mean'], color='black', lw=2.0,
                label='score$_{\\rm epoch}$ (robust mean)')
        if data['score_epoch_std'] is not None:
            ax.fill_between(k,
                            data['score_epoch_mean'] - data['score_epoch_std'],
                            data['score_epoch_mean'] + data['score_epoch_std'],
                            color='black', alpha=0.15, label='$\\pm$1 epoch std')
        _annotate_min(ax, k, data['score_epoch_mean'], k_step)
    elif data['score_pdf'] is not None:
        ax.plot(k, data['score_pdf'], color='black', lw=2.0,
                label='score$_{\\rm pdf}$ = peak$_{\\rm err}$ + inv$_{\\rm sharp}$')
        _annotate_min(ax, k, data['score_pdf'], k_step)
    else:
        _annotate_min(ax, k, data['score_com'], k_step)

    _bohr_vline(ax, k_bohr, k_step, n)
    ax.set_xlabel('k', fontsize=10)
    ax.set_ylabel('Score', fontsize=10)
    ax.set_title(f'n={n}  score comparison  |  Bohr $k_{n}$ = {k_bohr:.4f}',
                 fontsize=10)
    ax.legend(fontsize=8, loc='upper right')
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)


def plot_components(ax, data, n, k_step):
    r_n    = n**2 * R1_APPROX
    k_bohr = n / r_n
    k      = data['k']

    ax.plot(k, data['cv'],    color='steelblue', lw=1.2, ls='--',
            alpha=0.8, label='cv  (CoM steadiness)')
    ax.plot(k, data['r_bias'], color='steelblue', lw=1.2, ls=':',
            alpha=0.8, label='r$_{\\rm bias}$  (CoM drift)')
    if data['inv_sharpness'] is not None:
        ax.plot(k, data['inv_sharpness'], color='black', lw=1.2, ls='--',
                alpha=0.8, label='inv$_{\\rm sharp}$  (PDF width)')
        ax.plot(k, data['peak_error'],    color='black', lw=1.2, ls=':',
                alpha=0.8, label='peak$_{\\rm err}$  (PDF location)')

    _bohr_vline(ax, k_bohr, k_step, n)
    ax.set_xlabel('k', fontsize=10)
    ax.set_ylabel('Metric value', fontsize=10)
    ax.set_title(f'n={n}  metric components', fontsize=10)
    ax.legend(fontsize=8, loc='upper right')
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)


def plot_radial_pdf(ax, data, n, n_curves):
    import matplotlib.cm as cm

    r_n    = n**2 * R1_APPROX
    k_bohr = n / r_n
    k      = data['k']
    pdf    = data['pdf']
    rbins  = data['rbins']

    bohr_idx = int(np.argmin(np.abs(k - k_bohr)))
    n_k      = len(k)

    if n_curves >= n_k:
        indices = list(range(n_k))
    else:
        raw = list(np.linspace(0, n_k - 1, n_curves).astype(int))
        if bohr_idx not in raw:
            nearest = int(np.argmin(np.abs(np.array(raw) - bohr_idx)))
            raw[nearest] = bohr_idx
        indices = sorted(set(raw))

    bg_colors = cm.coolwarm(np.linspace(0.1, 0.9, len(indices)))

    for color, idx in zip(bg_colors, indices):
        ki      = k[idx]
        is_bohr = (idx == bohr_idx)
        ax.plot(rbins, pdf[idx],
                color  = 'crimson' if is_bohr else color,
                lw     = 2.5       if is_bohr else 0.9,
                alpha  = 1.0       if is_bohr else 0.5,
                zorder = 5         if is_bohr else 2,
                label  = f'k={ki:.4f}  ← Bohr' if is_bohr else f'k={ki:.4f}')

    ax.axvline(r_n, color='black', lw=1.2, ls='--',
               label=f'Bohr $r_{n}$ = {r_n:.1f}', zorder=4)
    ax.set_xlabel('r  (lattice units)', fontsize=10)
    ax.set_ylabel('P(r)', fontsize=10)
    ax.set_title(f'n={n}  radial PDF  |  sharp peak at $r_{n}$ only for $k = k_{n}$',
                 fontsize=10)
    ax.legend(fontsize=7, loc='upper right')
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n1',         action='store_true', help='n=1 only')
    ap.add_argument('--n2',         action='store_true', help='n=2 only')
    ap.add_argument('--no-heatmap', action='store_true',
                    help='Classic three-row layout instead of heatmap')
    ap.add_argument('--n-curves',   type=int, default=N_PDF_CURVES,
                    help=f'P(r) overlay count for classic layout (default {N_PDF_CURVES})')
    ap.add_argument('--out',        default=None,
                    help='Output file (pdf/png). Default: interactive.')
    ap.add_argument('--datadir',    default='.',
                    help='Directory containing .npy files (default: cwd)')
    args = ap.parse_args()

    try:
        import matplotlib
        if args.out:
            matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available -- pip install matplotlib")
        sys.exit(1)

    d1 = load(1, args.datadir) if not args.n2 else None
    d2 = load(2, args.datadir) if not args.n1 else None

    available = [(n, d) for n, d in [(1, d1), (2, d2)] if d is not None]
    if not available:
        print("No data files found.  Run exp_11_quantization_scan.py first.")
        sys.exit(1)

    use_heatmap = (not args.no_heatmap and
                   any(d['pdf'] is not None for _, d in available))

    k_steps = {1: K_STEP_N1, 2: K_STEP_N2}
    n_cols  = len(available)

    if use_heatmap:
        fig, axes = plt.subplots(1, n_cols,
                                 figsize=(8 * n_cols, 6),
                                 squeeze=False)
        fig.patch.set_facecolor('#111111')
        for ax_row in axes:
            for ax in ax_row:
                ax.set_facecolor('#111111')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
                for spine in ax.spines.values():
                    spine.set_edgecolor('white')

        for col, (n, data) in enumerate(available):
            plot_heatmap(axes[0][col], data, n, k_steps[n])

        fig.suptitle(
            'Spontaneous Quantisation — A=1 Bipartite Lattice Selects Bohr $k_n$\n'
            r'Bright spot at $(k_n,\,r_n)$ means the lattice spontaneously '
            r'selects the Bohr orbit',
            fontsize=12, color='white', y=1.01
        )
    else:
        has_pdf = any(d['pdf'] is not None for _, d in available)
        n_rows  = 3 if has_pdf else 2
        fig, axes = plt.subplots(n_rows, n_cols,
                                 figsize=(7 * n_cols, 4.5 * n_rows),
                                 squeeze=False)
        for col, (n, data) in enumerate(available):
            ks = k_steps[n]
            plot_scores(    axes[0][col], data, n, ks)
            plot_components(axes[1][col], data, n, ks)
            if has_pdf and data['pdf'] is not None:
                plot_radial_pdf(axes[2][col], data, n, args.n_curves)

        fig.suptitle(
            'Spontaneous Quantisation — A=1 Bipartite Lattice Selects Bohr $k_n$',
            fontsize=12, y=1.01
        )

    plt.tight_layout()

    if args.out:
        plt.savefig(args.out, bbox_inches='tight', dpi=150,
                    facecolor=fig.get_facecolor())
        print(f"Saved: {args.out}")
    else:
        plt.show()


if __name__ == '__main__':
    main()
