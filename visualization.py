"""
AAS Pricing Model — Visualization
All Around Services | Cameron Camarotti

Generates publication-quality charts showing Monte Carlo simulation
results, sensitivity analysis, and model behavior.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
from monte_carlo import run_simulation, sensitivity_analysis
from config import ACTUAL_JOB_MARGIN, ACTUAL_NET_MARGIN, SEASONAL_COEFFICIENTS


def set_style():
    """Set consistent chart styling."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "#f8f9fa",
        "axes.edgecolor": "#cccccc",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
    })


def plot_margin_distribution(margins, save_path="output/margin_distribution.png"):
    """Plot the distribution of margins across all simulated scenarios."""
    set_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(margins * 100, bins=50, color="#2E75B6", edgecolor="white",
            alpha=0.85, label="Simulated Margins")

    # Add reference lines
    ax.axvline(x=ACTUAL_JOB_MARGIN * 100, color="#E74C3C", linewidth=2,
               linestyle="--", label=f"Actual Job Margin ({ACTUAL_JOB_MARGIN*100:.1f}%)")
    ax.axvline(x=np.mean(margins) * 100, color="#27AE60", linewidth=2,
               linestyle="--", label=f"Simulated Mean ({np.mean(margins)*100:.1f}%)")
    ax.axvline(x=np.percentile(margins, 5) * 100, color="#F39C12", linewidth=1.5,
               linestyle=":", label=f"5th Percentile ({np.percentile(margins, 5)*100:.1f}%)")

    ax.set_xlabel("Job Margin (%)")
    ax.set_ylabel("Number of Scenarios")
    ax.set_title("AAS Pricing Model — Margin Distribution (10,000 Scenarios)")
    ax.legend(loc="upper left", fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_price_vs_cost(prices, costs, save_path="output/price_vs_cost.png"):
    """Scatter plot of quoted price vs total cost for all scenarios."""
    set_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(costs, prices, alpha=0.15, s=8, color="#2E75B6", label="Simulated Jobs")

    # Add break-even line
    max_val = max(np.max(costs), np.max(prices))
    ax.plot([0, max_val], [0, max_val], color="#E74C3C", linewidth=1.5,
            linestyle="--", label="Break-Even (Price = Cost)")

    ax.set_xlabel("Total Cost ($)")
    ax.set_ylabel("Quoted Price ($)")
    ax.set_title("AAS Pricing Model — Price vs Cost (10,000 Scenarios)")
    ax.legend(loc="upper left")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_sensitivity(sensitivities, save_path="output/sensitivity_analysis.png"):
    """Bar chart showing which variables impact margin the most."""
    set_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    variables = list(sensitivities.keys())
    impacts = [abs(sensitivities[v]["margin_change"]) * 100 for v in variables]
    colors = ["#E74C3C" if i == 0 else "#2E75B6" for i in range(len(variables))]

    bars = ax.barh(variables, impacts, color=colors, edgecolor="white", height=0.6)

    # Add value labels
    for bar, impact in zip(bars, impacts):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"{impact:.2f}%", va="center", fontsize=10)

    ax.set_xlabel("Absolute Margin Impact (percentage points)")
    ax.set_title("AAS Pricing Model — Variable Sensitivity Analysis")
    ax.invert_yaxis()

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_seasonal_pattern(save_path="output/seasonal_demand.png"):
    """Plot the seasonal demand coefficients across 12 months."""
    set_style()
    fig, ax = plt.subplots(figsize=(10, 5))

    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    kappas = [SEASONAL_COEFFICIENTS[m] for m in months]

    colors = ["#E74C3C" if k < 1.0 else "#27AE60" for k in kappas]
    ax.bar(month_names, kappas, color=colors, edgecolor="white", width=0.7)
    ax.axhline(y=1.0, color="#333333", linewidth=1, linestyle="--", alpha=0.5)

    for i, (name, k) in enumerate(zip(month_names, kappas)):
        ax.text(i, k + 0.02, f"{k:.2f}", ha="center", fontsize=9)

    ax.set_ylabel("Demand Coefficient (κ)")
    ax.set_title("AAS Seasonal Demand Coefficients — Calibrated from 14 Months of Data")
    ax.set_ylim(0.5, 1.5)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_fatigue_curve(save_path="output/fatigue_curve.png"):
    """Plot the crew fatigue decay curve."""
    set_style()
    fig, ax = plt.subplots(figsize=(10, 5))

    hours = np.linspace(0, 10, 100)
    from pricing_model import fatigue_factor
    fatigue = [fatigue_factor(h) for h in hours]

    ax.plot(hours, fatigue, color="#2E75B6", linewidth=2.5)
    ax.fill_between(hours, fatigue, alpha=0.15, color="#2E75B6")

    # Mark key points
    for h in [2, 4, 6, 8]:
        f = fatigue_factor(h)
        ax.plot(h, f, "o", color="#E74C3C", markersize=8)
        ax.annotate(f"  {h}hr: {f:.2f}", (h, f), fontsize=10)

    ax.set_xlabel("Job Duration (hours)")
    ax.set_ylabel("Crew Efficiency Factor (φ)")
    ax.set_title("AAS Fatigue Factor — Exponential Decay Model (φ = e^(-λh))")
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


if __name__ == "__main__":
    print("\n  GENERATING AAS PRICING MODEL VISUALIZATIONS\n")

    # Run simulation for data
    print("  Running Monte Carlo simulation...")
    results = run_simulation()

    # Generate all charts
    print("  Generating charts...\n")
    plot_margin_distribution(results["margins"])
    plot_price_vs_cost(results["prices"], results["costs"])

    sensitivities = sensitivity_analysis()
    plot_sensitivity(sensitivities)

    plot_seasonal_pattern()
    plot_fatigue_curve()

    print(f"\n  All visualizations saved to /output/")
    print("  Upload these images to your GitHub repo for the README.")
