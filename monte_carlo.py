"""
AAS Pricing Model — Monte Carlo Simulation
All Around Services | Cameron Camarotti

Stress-tests the pricing model by running 10,000 randomized scenarios
with input variables drawn from probability distributions calibrated
to actual AAS operating data.

This answers the question: "How robust is my pricing model under
varying real-world conditions?"
"""

import numpy as np
import os
from config import (
    MC_NUM_SIMULATIONS, MC_FUEL_PRICE_STD, MC_DISTANCE_MEAN,
    MC_DISTANCE_STD, MC_HOURS_STD_FACTOR, MC_DEMAND_NOISE_STD,
    SEASONAL_COEFFICIENTS, ACTUAL_JOB_MARGIN, ACTUAL_NET_MARGIN,
    SERVICE_BASE_RATES
)
from pricing_model import optimal_price


def run_simulation(num_simulations=MC_NUM_SIMULATIONS, seed=42):
    """
    Run Monte Carlo simulation with randomized inputs.

    Each scenario generates random but realistic values for:
    - Fuel price (normal distribution around current average)
    - Route distance (log-normal — most jobs are local, some are far)
    - Labor hours (varies by service type ± 25%)
    - Season/month (uniform across 12 months)
    - Service type (weighted by AAS historical service mix)

    Args:
        num_simulations: Number of scenarios to run (default 10,000)
        seed: Random seed for reproducibility

    Returns:
        Dictionary containing simulation results and statistics
    """
    np.random.seed(seed)

    # Service type weights based on approximate AAS historical mix
    service_types = list(SERVICE_BASE_RATES.keys())
    service_weights = [0.25, 0.25, 0.15, 0.05, 0.15, 0.10, 0.05]

    # Storage for results
    prices = []
    costs = []
    margins = []
    fatigue_factors = []
    seasonal_coefficients = []

    for i in range(num_simulations):
        # Randomize inputs from calibrated distributions
        fuel = max(2.50, np.random.normal(3.25, MC_FUEL_PRICE_STD))
        distance = max(3.0, np.random.lognormal(
            np.log(MC_DISTANCE_MEAN), 0.5))
        month = np.random.randint(1, 13)
        service = np.random.choice(service_types, p=service_weights)

        base_hours = SERVICE_BASE_RATES[service]["avg_hours"]
        hours = max(1.0, np.random.normal(
            base_hours, base_hours * MC_HOURS_STD_FACTOR))

        materials = max(0, np.random.normal(
            SERVICE_BASE_RATES[service]["materials_cost"], 5))

        crew_size = np.random.choice([1, 2, 3, 4], p=[0.15, 0.40, 0.30, 0.15])
        heavy_equip = service in ["pressure_washing", "landscaping"]
        disposal = max(0, np.random.normal(10, 8)) if service in [
            "junk_removal", "landscaping"] else 0

        # Run the pricing model
        result = optimal_price(
            fuel=fuel,
            distance=distance,
            hours=hours,
            crew_size=crew_size,
            equip_heavy=heavy_equip,
            materials=materials,
            disposal_fees=disposal,
            month=month,
            service_type=service
        )

        prices.append(result["price"])
        costs.append(result["total_cost"])
        margins.append(result["margin"])
        fatigue_factors.append(result["fatigue_factor"])
        seasonal_coefficients.append(result["seasonal_coefficient"])

    # Convert to numpy arrays for analysis
    prices = np.array(prices)
    costs = np.array(costs)
    margins = np.array(margins)
    fatigue_factors = np.array(fatigue_factors)

    # Calculate statistics
    results = {
        "num_simulations": num_simulations,
        "prices": prices,
        "costs": costs,
        "margins": margins,
        "fatigue_factors": fatigue_factors,
        "stats": {
            "mean_price": np.mean(prices),
            "median_price": np.median(prices),
            "std_price": np.std(prices),
            "mean_margin": np.mean(margins),
            "median_margin": np.median(margins),
            "min_margin": np.min(margins),
            "max_margin": np.max(margins),
            "pct_above_target": np.mean(margins >= 0.85) * 100,
            "pct_above_minimum": np.mean(margins >= 0.60) * 100,
            "percentile_5_margin": np.percentile(margins, 5),
            "percentile_95_margin": np.percentile(margins, 95),
            "mean_cost": np.mean(costs),
            "mean_fatigue": np.mean(fatigue_factors),
            "total_simulated_revenue": np.sum(prices),
        }
    }

    return results


def sensitivity_analysis(base_params=None):
    """
    Determine which input variable has the largest impact on margin.

    Method: Hold all variables at baseline, vary one at a time by ±20%,
    measure the change in output price and margin.

    Returns:
        Dictionary of variable sensitivities ranked by impact
    """
    if base_params is None:
        base_params = {
            "fuel": 3.25, "distance": 18, "hours": 3.0,
            "crew_size": 2, "equip_heavy": False,
            "materials": 20, "disposal_fees": 0,
            "month": 6, "service_type": "pressure_washing"
        }

    base_result = optimal_price(**base_params)
    base_price = base_result["price"]
    base_margin = base_result["margin"]

    sensitivities = {}
    test_variables = {
        "fuel": ("fuel", 3.25),
        "distance": ("distance", 18),
        "hours": ("hours", 3.0),
        "materials": ("materials", 20),
        "disposal_fees": ("disposal_fees", 0),
    }

    for var_name, (param_key, base_value) in test_variables.items():
        if base_value == 0:
            test_value = 10  # Can't do ±20% of zero
        else:
            test_value = base_value * 1.20  # +20%

        test_params = base_params.copy()
        test_params[param_key] = test_value
        test_result = optimal_price(**test_params)

        price_change = (test_result["price"] - base_price) / base_price * 100
        margin_change = test_result["margin"] - base_margin

        sensitivities[var_name] = {
            "base_value": base_value,
            "test_value": round(test_value, 2),
            "base_price": base_price,
            "test_price": test_result["price"],
            "price_change_pct": round(price_change, 2),
            "margin_change": round(margin_change, 4),
        }

    # Sort by absolute margin impact
    ranked = dict(sorted(
        sensitivities.items(),
        key=lambda x: abs(x[1]["margin_change"]),
        reverse=True
    ))

    return ranked


def print_simulation_report(results):
    """Print formatted simulation results."""
    s = results["stats"]

    print("=" * 65)
    print("  MONTE CARLO SIMULATION — AAS PRICING MODEL")
    print(f"  {results['num_simulations']:,} Randomized Scenarios")
    print("=" * 65)

    print(f"\n  PRICING DISTRIBUTION")
    print(f"    Mean Price:              ${s['mean_price']:.2f}")
    print(f"    Median Price:            ${s['median_price']:.2f}")
    print(f"    Std Deviation:           ${s['std_price']:.2f}")

    print(f"\n  MARGIN ANALYSIS")
    print(f"    Mean Margin:             {s['mean_margin'] * 100:.1f}%")
    print(f"    Median Margin:           {s['median_margin'] * 100:.1f}%")
    print(f"    Best Case (max):         {s['max_margin'] * 100:.1f}%")
    print(f"    Worst Case (min):        {s['min_margin'] * 100:.1f}%")
    print(f"    5th Percentile:          {s['percentile_5_margin'] * 100:.1f}%")
    print(f"    95th Percentile:         {s['percentile_95_margin'] * 100:.1f}%")

    print(f"\n  ROBUSTNESS METRICS")
    print(f"    % Scenarios Above 85% Margin:   {s['pct_above_target']:.1f}%")
    print(f"    % Scenarios Above 60% Margin:   {s['pct_above_minimum']:.1f}%")

    print(f"\n  COMPARISON TO ACTUAL RESULTS")
    print(f"    Actual Job-Level Margin:         {ACTUAL_JOB_MARGIN * 100:.1f}%")
    print(f"    Simulated Mean Margin:           {s['mean_margin'] * 100:.1f}%")
    print(f"    Actual Net Margin:               {ACTUAL_NET_MARGIN * 100:.1f}%")

    print(f"\n  COST ANALYSIS")
    print(f"    Mean Cost Per Job:       ${s['mean_cost']:.2f}")
    print(f"    Mean Fatigue Factor:     {s['mean_fatigue']:.3f}")

    print("=" * 65)


def print_sensitivity_report(sensitivities):
    """Print formatted sensitivity analysis."""
    print("\n" + "=" * 65)
    print("  SENSITIVITY ANALYSIS — Which Variables Matter Most?")
    print("  Method: +20% change in each variable, all others held constant")
    print("=" * 65)

    for rank, (var, data) in enumerate(sensitivities.items(), 1):
        print(f"\n  #{rank} — {var.upper()}")
        print(f"    Base: {data['base_value']} → Test: {data['test_value']}")
        print(f"    Price: ${data['base_price']:.0f} → ${data['test_price']:.0f} "
              f"({data['price_change_pct']:+.1f}%)")
        print(f"    Margin Impact: {data['margin_change']:+.4f}")

    print("\n" + "=" * 65)
    most_sensitive = list(sensitivities.keys())[0]
    print(f"  MOST SENSITIVE VARIABLE: {most_sensitive.upper()}")
    print(f"  This variable has the largest impact on job margins.")
    print("=" * 65)


if __name__ == "__main__":
    print("\n  ALL AROUND SERVICES — MONTE CARLO ANALYSIS")
    print("  Cameron Camarotti | github.com/YOUR_USERNAME\n")

    # Run simulation
    print("  Running 10,000 simulated job scenarios...")
    results = run_simulation()
    print_simulation_report(results)

    # Run sensitivity analysis
    sensitivities = sensitivity_analysis()
    print_sensitivity_report(sensitivities)

    # Save summary
    os.makedirs("output", exist_ok=True)
    print(f"\n  Simulation complete. Results available in /output/")
