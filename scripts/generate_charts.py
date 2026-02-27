"""
Generate business insight charts for the herrac.gov.az auction dataset.
Output: charts/ directory (7 PNG files)

Usage:
    pip install pandas matplotlib
    python scripts/generate_charts.py
"""

import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

# ── Styling ─────────────────────────────────────────────────────────────────
CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)

PALETTE  = ["#1B4F72", "#2E86C1", "#5DADE2", "#AED6F1", "#D6EAF8"]
ACCENT   = "#E74C3C"
POSITIVE = "#1E8449"
NEUTRAL  = "#2C3E50"
GRID_CLR = "#ECEFF1"
FIG_BG   = "#FAFAFA"

plt.rcParams.update({
    "figure.facecolor":  FIG_BG,
    "axes.facecolor":    "white",
    "axes.grid":         True,
    "grid.color":        GRID_CLR,
    "grid.linewidth":    0.8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    14,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
})

# AZN formatter — avoids the unrenderable manat glyph
def azn(x, _=None):
    return f"AZN {x:,.0f}"

def azn_k(x, _=None):
    return f"AZN {x:.0f}K"

def azn_m(x, _=None):
    return f"AZN {x:.1f}M"

# ── Data loading & prep ──────────────────────────────────────────────────────
df = pd.read_csv("data/data.csv", encoding="utf-8-sig")
df["startAt"]    = pd.to_datetime(df["startAt"])
df["validUntil"] = pd.to_datetime(df["validUntil"])
TODAY = pd.Timestamp("2026-02-27")
df["days_remaining"] = (df["validUntil"] - TODAY).dt.days

CAT_MAP = {
    "Menzil":              "Apartment",
    "Ferdi yasayis evi":   "Private House",
    "Qeyri-yasayis sahesi":"Commercial Property",
    "Avtomobiller":        "Vehicle",
    "Diger":               "Other",
    "Mənzil":              "Apartment",
    "Fərdi yaşayış evi":   "Private House",
    "Qeyri-yaşayış sahəsi":"Commercial Property",
    "Avtomobillər":        "Vehicle",
    "Digər":               "Other",
}
df["category"] = df["categoryName"].map(CAT_MAP).fillna(df["categoryName"])

# ── Helpers ──────────────────────────────────────────────────────────────────
def save(fig: plt.Figure, name: str) -> None:
    path = CHARTS_DIR / name
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 1 — Auction Portfolio: Count & Total Value by Category
# ═══════════════════════════════════════════════════════════════════════════
def chart_portfolio():
    cat_counts = df.groupby("category").size().sort_values(ascending=True)
    cat_values = (df.groupby("category")["initialPrice"].sum() / 1_000_000
                  ).reindex(cat_counts.index)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Auction Portfolio Overview", fontsize=16, fontweight="bold", y=1.01)

    bars1 = ax1.barh(cat_counts.index, cat_counts.values,
                     color=PALETTE[:len(cat_counts)], edgecolor="none", height=0.55)
    ax1.set_xlabel("Number of Auctions")
    ax1.set_title("Auctions by Property Type")
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 0.1, bar.get_y() + bar.get_height() / 2,
                 str(int(w)), va="center", ha="left",
                 fontsize=10, fontweight="bold", color=NEUTRAL)

    colors_v = [ACCENT if c == "Commercial Property" else PALETTE[1]
                for c in cat_values.index]
    bars2 = ax2.barh(cat_values.index, cat_values.values,
                     color=colors_v, edgecolor="none", height=0.55)
    ax2.set_xlabel("Total Listed Value (AZN millions)")
    ax2.set_title("Total Asset Value by Type")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(azn_m))
    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 0.05, bar.get_y() + bar.get_height() / 2,
                 f"AZN {w:.1f}M", va="center", ha="left",
                 fontsize=9, fontweight="bold", color=NEUTRAL)

    ax1.set_xlim(0, cat_counts.max() * 1.3)
    ax2.set_xlim(0, cat_values.max() * 1.3)
    fig.tight_layout()
    save(fig, "01_portfolio_overview.png")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 2 — Price Band Distribution
# ═══════════════════════════════════════════════════════════════════════════
def chart_price_bands():
    bins   = [0, 20_000, 50_000, 100_000, 200_000, 500_000, float("inf")]
    labels = ["Under\nAZN 20K", "AZN 20K\n-50K", "AZN 50K\n-100K",
              "AZN 100K\n-200K", "AZN 200K\n-500K", "Above\nAZN 500K"]
    df["price_band"] = pd.cut(df["initialPrice"], bins=bins, labels=labels)
    counts = df["price_band"].value_counts().reindex(labels)

    fig, ax = plt.subplots(figsize=(11, 5))
    colors = [PALETTE[0], PALETTE[1], PALETTE[2],
              PALETTE[3], "#F0B27A", ACCENT]
    bars = ax.bar(labels, counts.values, color=colors, edgecolor="none", width=0.6)
    ax.set_title("How Are Auctions Distributed Across Price Ranges?")
    ax.set_xlabel("Listed Price Range")
    ax.set_ylabel("Number of Auctions")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2,
                str(int(h)), ha="center", va="bottom",
                fontsize=12, fontweight="bold", color=NEUTRAL)
    ax.set_ylim(0, counts.max() * 1.2)
    fig.tight_layout()
    save(fig, "02_price_band_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 3 — Auction Status: ONGOING vs NOT STARTED by Category
# ═══════════════════════════════════════════════════════════════════════════
def chart_status():
    pivot = (df.groupby(["category", "status"])
               .size()
               .unstack(fill_value=0)
               .reindex(columns=["ONGOING", "NOT_STARTED"]))
    pivot = pivot.sort_values("ONGOING", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    pivot.plot(kind="barh", stacked=True, ax=ax,
               color=[POSITIVE, PALETTE[2]], edgecolor="none", width=0.55)
    ax.set_title("Active vs. Scheduled Auctions by Property Type")
    ax.set_xlabel("Number of Auctions")
    ax.legend(["Live Now (ONGOING)", "Scheduled (NOT STARTED)"],
              loc="lower right", frameon=True)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    totals = pivot.sum(axis=1)
    for i, (_, total) in enumerate(totals.items()):
        ax.text(total + 0.15, i, str(int(total)),
                va="center", ha="left", fontsize=10,
                fontweight="bold", color=NEUTRAL)
    ax.set_xlim(0, totals.max() * 1.2)
    fig.tight_layout()
    save(fig, "03_auction_status_by_category.png")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 4 — Buyer Engagement: Attendants per Category
# ═══════════════════════════════════════════════════════════════════════════
def chart_engagement():
    eng = df.groupby("category").agg(
        total_lots=("id", "count"),
        total_attendants=("attendantsCount", "sum"),
        lots_with_bids=("attendantsCount", lambda x: (x > 0).sum()),
    ).sort_values("total_attendants", ascending=False)
    eng["engagement_rate"] = (eng["lots_with_bids"] / eng["total_lots"] * 100).round(1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Buyer Engagement Across Property Types", fontsize=16,
                 fontweight="bold", y=1.01)

    colors_l = [ACCENT if v == eng["total_attendants"].max() else PALETTE[1]
                for v in eng["total_attendants"]]
    bars1 = ax1.bar(eng.index, eng["total_attendants"],
                    color=colors_l, edgecolor="none", width=0.55)
    ax1.set_title("Total Registered Bidders")
    ax1.set_ylabel("Number of Bidders")
    ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    for bar in bars1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                 str(int(h)), ha="center", va="bottom",
                 fontsize=11, fontweight="bold", color=NEUTRAL)
    ax1.set_ylim(0, eng["total_attendants"].max() * 1.3)
    ax1.tick_params(axis="x", rotation=15)

    colors_r = [POSITIVE if v > 20 else ACCENT for v in eng["engagement_rate"]]
    bars2 = ax2.bar(eng.index, eng["engagement_rate"],
                    color=colors_r, edgecolor="none", width=0.55)
    ax2.set_title("% of Lots With at Least One Bidder")
    ax2.set_ylabel("Engagement Rate (%)")
    ax2.set_ylim(0, 100)
    ax2.axhline(50, color=PALETTE[2], linestyle="--", linewidth=1,
                label="50% benchmark")
    ax2.legend(fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h + 1,
                 f"{h:.0f}%", ha="center", va="bottom",
                 fontsize=11, fontweight="bold", color=NEUTRAL)
    ax2.tick_params(axis="x", rotation=15)

    fig.tight_layout()
    save(fig, "04_buyer_engagement.png")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 5 — Round 2 Auctions: Unsold Inventory
# ═══════════════════════════════════════════════════════════════════════════
def chart_rounds():
    r_cnt = df.groupby(["category", "roundNumber"]).size().unstack(fill_value=0)
    r_cnt.columns = [f"Round {int(c)}" for c in r_cnt.columns]
    r_cnt = r_cnt.sort_values("Round 1", ascending=True)

    r_price = df.groupby("roundNumber")["initialPrice"].mean() / 1000

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Round 1 vs. Round 2 Auctions — Unsold Inventory Signal",
                 fontsize=15, fontweight="bold", y=1.01)

    r_cnt.plot(kind="barh", stacked=True, ax=ax1,
               color=[PALETTE[1], ACCENT], edgecolor="none", width=0.55)
    ax1.set_title("Count: First Attempt vs. Re-Listed")
    ax1.set_xlabel("Number of Lots")
    ax1.legend(["Round 1 (first listing)", "Round 2 (re-listed after no sale)"],
               loc="lower right", frameon=True, fontsize=9)
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    totals = r_cnt.sum(axis=1)
    for i, t in enumerate(totals):
        ax1.text(t + 0.1, i, str(int(t)), va="center", ha="left",
                 fontsize=10, fontweight="bold", color=NEUTRAL)
    ax1.set_xlim(0, totals.max() * 1.2)

    bars = ax2.bar(r_price.index.map({1: "Round 1", 2: "Round 2"}),
                   r_price.values,
                   color=[PALETTE[1], ACCENT], edgecolor="none", width=0.45)
    ax2.set_title("Average Listed Price per Round (AZN thousands)")
    ax2.set_ylabel("Average Price (AZN K)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(azn_k))
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h + 5,
                 f"AZN {h:.0f}K", ha="center", va="bottom",
                 fontsize=11, fontweight="bold", color=NEUTRAL)
    ax2.set_ylim(0, r_price.max() * 1.3)

    fig.tight_layout()
    save(fig, "05_round_analysis.png")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 6 — Closing Urgency: Lots by Urgency Tier & Category (aggregated)
# ═══════════════════════════════════════════════════════════════════════════
def chart_urgency():
    # Bucket every lot into an urgency tier
    def urgency_tier(d):
        if d < 0:
            return "Overdue"
        elif d <= 3:
            return "Critical\n(1-3 days)"
        elif d <= 7:
            return "Urgent\n(4-7 days)"
        else:
            return "Approaching\n(8-14 days)"

    tiers_order = ["Overdue", "Critical\n(1-3 days)",
                   "Urgent\n(4-7 days)", "Approaching\n(8-14 days)"]
    tier_colors = [ACCENT, "#E67E22", PALETTE[1], PALETTE[3]]

    df["urgency"] = df["days_remaining"].apply(urgency_tier)

    # ── Left panel: total lots per tier (stacked by category)
    cats_order = ["Private House", "Apartment", "Commercial Property",
                  "Vehicle", "Other"]
    cat_colors = PALETTE[:5]

    pivot = (df.groupby(["urgency", "category"])
               .size()
               .unstack(fill_value=0)
               .reindex(index=tiers_order)
               .reindex(columns=cats_order, fill_value=0))

    # ── Right panel: avg days remaining per tier × category heat-like bars
    tier_totals = pivot.sum(axis=1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Auction Closing Urgency — Portfolio at Risk",
                 fontsize=16, fontweight="bold", y=1.01)

    # Left: stacked bar — count by category per urgency tier
    bottom = [0] * len(tiers_order)
    for cat, color in zip(cats_order, cat_colors):
        vals = pivot[cat].values if cat in pivot.columns else [0] * len(tiers_order)
        ax1.bar(tiers_order, vals, bottom=bottom, label=cat,
                color=color, edgecolor="none", width=0.55)
        bottom = [b + v for b, v in zip(bottom, vals)]

    # Annotate totals above each bar
    for i, total in enumerate(tier_totals):
        ax1.text(i, total + 0.3, str(int(total)),
                 ha="center", va="bottom", fontsize=12,
                 fontweight="bold", color=NEUTRAL)

    ax1.set_title("Lots Closing by Urgency Tier")
    ax1.set_ylabel("Number of Lots")
    ax1.set_ylim(0, tier_totals.max() * 1.25)
    ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax1.legend(title="Property Type", fontsize=9, title_fontsize=9,
               loc="upper right", frameon=True)

    # Right: horizontal bars — urgency tiers coloured by severity
    tier_totals_sorted = tier_totals.sort_values(ascending=True)
    colors_r = [tier_colors[tiers_order.index(t)] for t in tier_totals_sorted.index]
    bars = ax2.barh(tier_totals_sorted.index, tier_totals_sorted.values,
                    color=colors_r, edgecolor="none", height=0.5)
    ax2.set_title("Total Lots at Risk by Severity")
    ax2.set_xlabel("Number of Lots")
    ax2.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    for bar in bars:
        w = bar.get_width()
        ax2.text(w + 0.15, bar.get_y() + bar.get_height() / 2,
                 str(int(w)), va="center", ha="left",
                 fontsize=11, fontweight="bold", color=NEUTRAL)
    ax2.set_xlim(0, tier_totals_sorted.max() * 1.3)

    fig.tight_layout()
    save(fig, "06_closing_urgency.png")


# ═══════════════════════════════════════════════════════════════════════════
# Chart 7 — Apartment Price per m² Comparison
# ═══════════════════════════════════════════════════════════════════════════
def chart_price_per_m2():
    apt = df[df["category"] == "Apartment"].dropna(
        subset=["lotData.Sahəsi(m2)", "initialPrice"]).copy()
    apt["price_per_m2"] = apt["initialPrice"] / apt["lotData.Sahəsi(m2)"]
    apt = apt.sort_values("price_per_m2", ascending=True).reset_index(drop=True)

    # Build readable short label: district + size only
    apt["short_name"] = apt["lotName"].str.extract(
        r"(?:Mənzil|Menzil)\s*-\s*(.{0,40})"
    )[0].str.strip().fillna("Apartment") + "..."

    avg_pm2 = apt["price_per_m2"].mean()

    fig, ax = plt.subplots(figsize=(11, max(5, len(apt) * 0.48)))
    colors = [ACCENT if v > avg_pm2 * 1.5 else
              (POSITIVE if v < avg_pm2 * 0.8 else PALETTE[1])
              for v in apt["price_per_m2"]]
    ax.barh(apt["short_name"], apt["price_per_m2"],
            color=colors, edgecolor="none", height=0.6)
    ax.axvline(avg_pm2, color=NEUTRAL, linestyle="--", linewidth=1.5,
               label=f"Portfolio avg: AZN {avg_pm2:,.0f}/m2")
    ax.set_title("Apartment Price per m2 — Individual Lot Comparison\n"
                 "(Red = significantly above avg, Green = below avg)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Listed Price per m2 (AZN)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(azn))
    ax.legend(fontsize=9)
    for patch in ax.patches:
        w = patch.get_width()
        ax.text(w + 20, patch.get_y() + patch.get_height() / 2,
                f"AZN {w:,.0f}", va="center", ha="left",
                fontsize=8, color=NEUTRAL)
    ax.set_xlim(0, apt["price_per_m2"].max() * 1.3)
    fig.tight_layout()
    save(fig, "07_apartment_price_per_m2.png")


# ── Run all ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating charts ...\n")
    chart_portfolio()
    chart_price_bands()
    chart_status()
    chart_engagement()
    chart_rounds()
    chart_urgency()
    chart_price_per_m2()
    print(f"\nDone. All charts saved to: {CHARTS_DIR.resolve()}")
