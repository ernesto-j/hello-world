#!/usr/bin/env python3
"""Monte Carlo valuation model for ScreenFixed (Brisbane CBD screen-repair business).

Reads all inputs from params.yaml so the model can be re-run with real figures.
Outputs:
  outputs/results.json        - percentiles, probabilities, tornado data
  outputs/revenue_dist.png    - revenue distribution
  outputs/valuation_dist.png  - valuation distribution
  outputs/sde_dist.png        - SDE distribution
  outputs/tornado.png         - one-at-a-time sensitivity (p10 -> p90 swing per input)

Usage: python3 simulate.py [--params params.yaml] [--outdir outputs]
"""
import argparse
import json
import os

import numpy as np
import yaml
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --- palette (dataviz reference instance, light mode) ---
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"   # categorical slot 1 / diverging cool pole
RED = "#e34948"    # diverging warm pole
ORANGE = "#eb6834"


# ---------------------------------------------------------------- distributions
def sample(spec, rng, n):
    d = spec["dist"]
    if d == "triangular":
        return rng.triangular(spec["low"], spec["mode"], spec["high"], n)
    if d == "uniform":
        return rng.uniform(spec["low"], spec["high"], n)
    if d == "fixed":
        return np.full(n, float(spec["value"]))
    raise ValueError(f"unknown dist {d}")


def quantile(spec, q):
    """Analytic quantile for OAT tornado."""
    d = spec["dist"]
    if d == "fixed":
        return float(spec["value"])
    if d == "uniform":
        return spec["low"] + q * (spec["high"] - spec["low"])
    if d == "triangular":
        a, c, b = spec["low"], spec["mode"], spec["high"]
        fc = (c - a) / (b - a)
        if q < fc:
            return a + np.sqrt(q * (b - a) * (c - a))
        return b - np.sqrt((1 - q) * (b - a) * (b - c))
    raise ValueError(f"unknown dist {d}")


# ---------------------------------------------------------------- model
def evaluate(pt, cats):
    """Deterministic model: point dict -> dict of outcomes. Works on scalars or arrays."""
    jobs = pt["repairs_per_day"] * pt["trading_days"]
    ticket = sum(pt[f"share_{c}"] * pt[f"price_{c}"] for c in cats)
    revenue = jobs * ticket
    parts = jobs * sum(pt[f"share_{c}"] * pt[f"price_{c}"] * pt[f"parts_pct_{c}"] for c in cats)
    occupancy = pt["rent_annual"] + pt["outgoings_annual"]
    other = revenue * pt["other_opex_pct"]
    sde = revenue - parts - pt["non_owner_wages_annual"] - occupancy - other
    valuation = sde * pt["sde_multiple"]
    return {"jobs": jobs, "ticket": ticket, "revenue": revenue, "parts": parts,
            "occupancy": occupancy, "sde": sde, "valuation": valuation}


def run_mc(P, rng):
    n = int(P["simulation"]["runs"])
    cats = list(P["ticket_mix"]["categories"].keys())
    mix = P["ticket_mix"]
    conc = float(mix["concentration"])
    total = sum(mix["categories"][c]["share"] for c in cats)
    alphas = np.array([mix["categories"][c]["share"] / total * conc for c in cats])
    shares = rng.dirichlet(alphas, size=n)  # (n, k)

    pt = {
        "repairs_per_day": sample(P["throughput"]["repairs_per_day"], rng, n),
        "trading_days": sample(P["throughput"]["trading_days_per_year"], rng, n),
        "non_owner_wages_annual": sample(P["costs"]["non_owner_wages_annual"], rng, n),
        "rent_annual": sample(P["costs"]["rent_annual"], rng, n),
        "outgoings_annual": sample(P["costs"]["outgoings_annual"], rng, n),
        "other_opex_pct": sample(P["costs"]["other_opex_pct_revenue"], rng, n),
        "sde_multiple": sample(P["valuation"]["sde_multiple"], rng, n),
    }
    for i, c in enumerate(cats):
        pt[f"share_{c}"] = shares[:, i]
        pt[f"price_{c}"] = sample(mix["categories"][c]["price"], rng, n)
        pt[f"parts_pct_{c}"] = sample(mix["categories"][c]["parts_cost_pct"], rng, n)
    return pt, evaluate(pt, cats), cats


def median_point(P, cats):
    mix = P["ticket_mix"]
    pt = {
        "repairs_per_day": quantile(P["throughput"]["repairs_per_day"], 0.5),
        "trading_days": quantile(P["throughput"]["trading_days_per_year"], 0.5),
        "non_owner_wages_annual": quantile(P["costs"]["non_owner_wages_annual"], 0.5),
        "rent_annual": quantile(P["costs"]["rent_annual"], 0.5),
        "outgoings_annual": quantile(P["costs"]["outgoings_annual"], 0.5),
        "other_opex_pct": quantile(P["costs"]["other_opex_pct_revenue"], 0.5),
        "sde_multiple": quantile(P["valuation"]["sde_multiple"], 0.5),
    }
    total = sum(mix["categories"][c]["share"] for c in cats)
    for c in cats:
        pt[f"share_{c}"] = mix["categories"][c]["share"] / total
        pt[f"price_{c}"] = quantile(mix["categories"][c]["price"], 0.5)
        pt[f"parts_pct_{c}"] = quantile(mix["categories"][c]["parts_cost_pct"], 0.5)
    return pt


def share_quantile(P, cats, cat, q):
    """Marginal Beta quantile of one Dirichlet share."""
    from math import lgamma  # noqa: F401  (scipy-free beta quantile via numpy random not analytic)
    # Use a large sample from the marginal Beta to get the quantile without scipy.
    mix = P["ticket_mix"]
    conc = float(mix["concentration"])
    total = sum(mix["categories"][c]["share"] for c in cats)
    a = mix["categories"][cat]["share"] / total * conc
    b = conc - a
    rng = np.random.default_rng(12345)
    return float(np.quantile(rng.beta(a, b, 200_000), q))


def tornado(P, cats):
    """OAT: swing each input from its p10 to p90 holding others at median."""
    base_pt = median_point(P, cats)
    base_val = evaluate(base_pt, cats)["valuation"]
    rows = []

    def swing(label, key, spec):
        lo_pt, hi_pt = dict(base_pt), dict(base_pt)
        lo_pt[key] = quantile(spec, 0.10)
        hi_pt[key] = quantile(spec, 0.90)
        rows.append({"input": label,
                     "low": evaluate(lo_pt, cats)["valuation"],
                     "high": evaluate(hi_pt, cats)["valuation"]})

    swing("Repairs per day", "repairs_per_day", P["throughput"]["repairs_per_day"])
    swing("Trading days / yr", "trading_days", P["throughput"]["trading_days_per_year"])
    swing("Non-owner wages", "non_owner_wages_annual", P["costs"]["non_owner_wages_annual"])
    swing("Rent (annual)", "rent_annual", P["costs"]["rent_annual"])
    swing("Other opex % rev", "other_opex_pct", P["costs"]["other_opex_pct_revenue"])
    swing("SDE multiple", "sde_multiple", P["valuation"]["sde_multiple"])

    mix = P["ticket_mix"]["categories"]
    for c in cats:
        label = c.replace("_", " ")
        swing(f"Price: {label}", f"price_{c}", mix[c]["price"])
        swing(f"Parts %: {label}", f"parts_pct_{c}", mix[c]["parts_cost_pct"])

    # mix tilt: premium share p10/p90, other shares rescaled proportionally
    tilt_cat = P["ticket_mix"].get("tornado_tilt_category")
    if tilt_cat in cats:
        for q, tag in ((0.10, "low"), (0.90, "high")):
            pt = dict(median_point(P, cats))
            s = share_quantile(P, cats, tilt_cat, q)
            others = [c for c in cats if c != tilt_cat]
            rest = sum(pt[f"share_{c}"] for c in others)
            for c in others:
                pt[f"share_{c}"] *= (1 - s) / rest
            pt[f"share_{tilt_cat}"] = s
            v = evaluate(pt, cats)["valuation"]
            if tag == "low":
                tilt_low = v
            else:
                tilt_high = v
        rows.append({"input": f"Mix share: {tilt_cat.replace('_', ' ')}",
                     "low": tilt_low, "high": tilt_high})

    for r in rows:
        r["span"] = abs(r["high"] - r["low"])
    rows.sort(key=lambda r: -r["span"])
    return base_val, rows


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean(); ry -= ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx**2).sum() * (ry**2).sum()))


# ---------------------------------------------------------------- charts
def style_ax(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.75)
    ax.set_axisbelow(True)


def kfmt(x, _):
    return f"${x / 1e6:.1f}M" if abs(x) >= 1e6 else f"${x / 1e3:.0f}K"


def hist_chart(data, title, subtitle, path, band=None, band_label=None):
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    style_ax(ax)
    ax.hist(data, bins=60, color=BLUE, edgecolor=SURFACE, linewidth=0.5)
    p10, p50, p90 = np.percentile(data, [10, 50, 90])
    for v, lab in ((p10, "p10"), (p50, "p50"), (p90, "p90")):
        ax.axvline(v, color=INK_2, linewidth=1, linestyle=(0, (4, 3)))
        ax.text(v, ax.get_ylim()[1] * 0.97, f" {lab} {kfmt(v, None)}",
                color=INK_2, fontsize=8.5, va="top")
    if band:
        ax.axvspan(band[0], band[1], color=ORANGE, alpha=0.12, zorder=0)
        ax.text(band[0], ax.get_ylim()[1] * 0.06, f" {band_label}",
                color=ORANGE, fontsize=8.5)
    ax.xaxis.set_major_formatter(FuncFormatter(kfmt))
    ax.set_yticks([])
    ax.set_title(title, color=INK, fontsize=12, loc="left", fontweight="bold", pad=26)
    ax.text(0, 1.03, subtitle, transform=ax.transAxes, color=INK_2, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def tornado_chart(base_val, rows, path, top=10):
    rows = rows[:top][::-1]
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.grid(True, color=GRID, linewidth=0.75)
    ax.set_axisbelow(True)
    ys = np.arange(len(rows))
    for y, r in zip(ys, rows):
        lo, hi = sorted((r["low"], r["high"]))
        ax.barh(y, lo - base_val, left=base_val, height=0.55, color=BLUE,
                edgecolor=SURFACE, linewidth=0.5)
        ax.barh(y, hi - base_val, left=base_val, height=0.55, color=RED,
                edgecolor=SURFACE, linewidth=0.5)
    ax.axvline(base_val, color=INK_2, linewidth=1)
    ax.set_yticks(ys, [r["input"] for r in rows], color=INK, fontsize=9)
    ax.xaxis.set_major_formatter(FuncFormatter(kfmt))
    ax.set_title("What moves the valuation", color=INK, fontsize=12, loc="left",
                 fontweight="bold", pad=26)
    ax.text(0, 1.02, f"Input swung p10 → p90, others at median (base ≈ {kfmt(base_val, None)}). "
                     f"Blue = p10, red = p90.",
            transform=ax.transAxes, color=INK_2, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", default=os.path.join(os.path.dirname(__file__), "params.yaml"))
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(__file__), "outputs"))
    args = ap.parse_args()

    with open(args.params) as f:
        P = yaml.safe_load(f)
    os.makedirs(args.outdir, exist_ok=True)
    rng = np.random.default_rng(int(P["simulation"]["seed"]))

    pt, out, cats = run_mc(P, rng)

    def pct(a):
        return {f"p{q}": round(float(np.percentile(a, q))) for q in (5, 10, 25, 50, 75, 90, 95)}

    ob = P["owner_check"]
    in_band = np.mean((out["revenue"] >= ob["stated_revenue_low"]) &
                      (out["revenue"] <= ob["stated_revenue_high"]))
    band_mask = (out["revenue"] >= ob["stated_revenue_low"]) & (out["revenue"] <= ob["stated_revenue_high"])

    base_val, rows = tornado(P, cats)

    corr_inputs = {
        "repairs_per_day": pt["repairs_per_day"],
        "trading_days": pt["trading_days"],
        "wages": pt["non_owner_wages_annual"],
        "rent": pt["rent_annual"],
        "other_opex_pct": pt["other_opex_pct"],
        "sde_multiple": pt["sde_multiple"],
        "avg_ticket": out["ticket"],
    }
    correlations = {k: round(spearman(v, out["valuation"]), 3) for k, v in corr_inputs.items()}

    results = {
        "runs": int(P["simulation"]["runs"]),
        "revenue": pct(out["revenue"]),
        "avg_ticket": pct(out["ticket"]),
        "jobs_per_year": pct(out["jobs"]),
        "sde": pct(out["sde"]),
        "sde_margin_pct": {k: round(v, 1) for k, v in
                           {f"p{q}": float(np.percentile(out["sde"] / out["revenue"], q)) * 100
                            for q in (10, 50, 90)}.items()},
        "valuation": pct(out["valuation"]),
        "prob_sde_negative": round(float(np.mean(out["sde"] < 0)), 4),
        "prob_revenue_in_owner_band": round(float(in_band), 4),
        "valuation_given_owner_band": pct(out["valuation"][band_mask]) if band_mask.any() else None,
        "prob_valuation_in_original_range": round(float(np.mean(
            (out["valuation"] >= 700_000) & (out["valuation"] <= 1_050_000))), 4),
        "tornado_base_valuation": round(base_val),
        "tornado": [{"input": r["input"], "low": round(r["low"]),
                     "high": round(r["high"]), "span": round(r["span"])} for r in rows],
        "spearman_vs_valuation": correlations,
    }

    with open(os.path.join(args.outdir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    hist_chart(out["revenue"], "Annual revenue distribution",
               f"{results['runs']:,} Monte Carlo runs · orange band = owner's stated $1.1–1.2M",
               os.path.join(args.outdir, "revenue_dist.png"),
               band=(ob["stated_revenue_low"], ob["stated_revenue_high"]),
               band_label="owner's claim")
    hist_chart(out["sde"], "SDE distribution (seller's discretionary earnings)",
               "Revenue − parts − non-owner wages − occupancy − other opex",
               os.path.join(args.outdir, "sde_dist.png"))
    hist_chart(out["valuation"], "Valuation distribution (SDE × multiple)",
               "Orange band = your original back-of-envelope range $700K–$1.05M",
               os.path.join(args.outdir, "valuation_dist.png"),
               band=(700_000, 1_050_000), band_label="original range")
    tornado_chart(base_val, rows, os.path.join(args.outdir, "tornado.png"))

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
