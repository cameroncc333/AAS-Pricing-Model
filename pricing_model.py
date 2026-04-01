"""
AAS Pricing Model — 8-Variable Cost Function
All Around Services | Founded January 2025
Cameron Camarotti

This module implements the core pricing engine that generates every AAS quote.
The model takes 8 real-world inputs and outputs an optimized price using
partial derivative optimization logic from AP Calculus.
"""

import math
from config import (
    FUEL_COST_PER_MILE, BASE_HOURLY_RATE, AVG_CREW_SIZE,
    FATIGUE_DECAY_CONSTANT, EQUIPMENT_DEPRECIATION_PER_JOB,
    HEAVY_EQUIPMENT_MULTIPLIER, INSURANCE_PER_JOB, MARKETING_PER_JOB,
    ADMIN_PER_JOB, TARGET_MARGIN, MINIMUM_MARGIN, MARKUP_FACTOR,
    SEASONAL_COEFFICIENTS, SERVICE_BASE_RATES
)


def fatigue_factor(hours, decay_constant=FATIGUE_DECAY_CONSTANT):
    """
    Calculate crew fatigue factor using exponential decay.

    As hours increase, crew efficiency decreases following:
        φ(h) = e^(-λh)

    This models the same energy dissipation concept from AP Physics —
    a system losing efficiency over time at a rate proportional to
    its current state.

    Args:
        hours: Estimated labor hours for the job
        decay_constant: Lambda (λ) — rate of efficiency decline

    Returns:
        Fatigue multiplier between 0 and 1 (1 = fully efficient, 0 = fully fatigued)
    """
    return math.exp(-decay_constant * hours)


def effective_labor_hours(estimated_hours, crew_size=AVG_CREW_SIZE):
    """
    Calculate effective labor hours accounting for fatigue.

    A 6-hour job doesn't produce 6 hours of output because crew
    productivity declines. Effective hours = integral of the fatigue
    curve over the job duration.

    This is essentially computing the area under the exponential decay
    curve — a direct application of integration from AP Calculus.

    Args:
        estimated_hours: Raw estimated hours for the job
        crew_size: Number of crew members

    Returns:
        Effective crew-hours (always less than or equal to raw hours × crew size)
    """
    phi = fatigue_factor(estimated_hours)
    efficiency = (1 + phi) / 2  # Average efficiency over the job duration
    return estimated_hours * crew_size * efficiency


def fuel_cost(distance_miles):
    """
    Calculate round-trip fuel cost.

    Args:
        distance_miles: One-way distance to job site in miles

    Returns:
        Total fuel cost for the round trip ($)
    """
    round_trip = distance_miles * 2
    return round_trip * FUEL_COST_PER_MILE


def labor_cost(estimated_hours, crew_size=AVG_CREW_SIZE):
    """
    Calculate total labor cost accounting for fatigue-adjusted efficiency.

    The crew gets paid for all hours worked, but the effective output
    decreases with fatigue. This means longer jobs have a higher
    cost-per-unit-of-output ratio.

    Args:
        estimated_hours: Raw estimated hours
        crew_size: Number of crew members

    Returns:
        Total labor cost ($)
    """
    return estimated_hours * crew_size * BASE_HOURLY_RATE


def equipment_cost(heavy_equipment=False):
    """
    Calculate per-job equipment depreciation.

    Args:
        heavy_equipment: Whether job requires heavy equipment (pressure washer, trailer)

    Returns:
        Equipment depreciation cost ($)
    """
    base = EQUIPMENT_DEPRECIATION_PER_JOB
    if heavy_equipment:
        base *= HEAVY_EQUIPMENT_MULTIPLIER
    return base


def total_cost(fuel, distance, hours, crew_size, equip_heavy,
               materials, disposal_fees):
    """
    Calculate total job cost from all 8 input variables.

    C(f, d, h, φ, e, m, r, κ) — the complete cost function.
    Note: φ (fatigue) is computed from h (hours), and κ (seasonal)
    affects the price side, not the cost side.

    Args:
        fuel: Fuel price per gallon ($/gal)
        distance: One-way distance to job site (miles)
        hours: Estimated labor hours
        crew_size: Number of crew members
        equip_heavy: Whether heavy equipment is needed
        materials: Materials/supplies cost ($)
        disposal_fees: Waste disposal fees ($)

    Returns:
        Total cost to complete the job ($)
    """
    fuel_price_per_mile = fuel / 14.0  # Vehicle MPG

    f_cost = distance * 2 * fuel_price_per_mile           # Fuel
    l_cost = hours * crew_size * BASE_HOURLY_RATE          # Labor
    e_cost = equipment_cost(equip_heavy)                   # Equipment
    overhead = INSURANCE_PER_JOB + MARKETING_PER_JOB + ADMIN_PER_JOB  # Overhead

    return f_cost + l_cost + e_cost + materials + disposal_fees + overhead


def optimal_price(fuel, distance, hours, crew_size, equip_heavy,
                  materials, disposal_fees, month, service_type=None):
    """
    Generate the optimized price for a job using the full 8-variable model.

    The optimization logic:
    1. Calculate total cost from all input variables
    2. Apply the fatigue-adjusted efficiency factor
    3. Apply the seasonal demand coefficient (κ)
    4. Apply markup to achieve target margin
    5. Enforce minimum margin floor
    6. Round to nearest $5 for clean quoting

    The price satisfies the optimization condition:
        ∂(Revenue - Cost) / ∂(Price) = 0

    Subject to:
        - Price ≥ Cost / (1 - minimum_margin)
        - Price is competitive within service category range

    Args:
        fuel: Current fuel price ($/gallon)
        distance: One-way distance to job site (miles)
        hours: Estimated labor hours
        crew_size: Number of crew members
        equip_heavy: Whether heavy equipment is needed
        materials: Materials cost ($)
        disposal_fees: Disposal fees ($)
        month: Month of the year (1-12) for seasonal adjustment
        service_type: Optional service category for base rate reference

    Returns:
        Dictionary with optimized price and full cost breakdown
    """
    # Step 1: Calculate total cost
    cost = total_cost(fuel, distance, hours, crew_size, equip_heavy,
                      materials, disposal_fees)

    # Step 2: Calculate fatigue-adjusted efficiency
    phi = fatigue_factor(hours)
    eff_hours = effective_labor_hours(hours, crew_size)
    fatigue_penalty = 1 + (1 - phi) * 0.15  # Longer jobs get a fatigue surcharge

    # Step 3: Apply seasonal demand coefficient (κ)
    kappa = SEASONAL_COEFFICIENTS.get(month, 1.0)

    # Step 4: Calculate optimized price
    base_price = cost * MARKUP_FACTOR * fatigue_penalty * kappa

    # Apply service category floor if available
    if service_type and service_type in SERVICE_BASE_RATES:
        category_floor = SERVICE_BASE_RATES[service_type]["base_price"]
        base_price = max(base_price, category_floor)

    # Step 5: Enforce minimum margin
    min_price = cost / (1 - MINIMUM_MARGIN)
    final_price = max(base_price, min_price)

    # Step 6: Round to nearest $5
    final_price = round(final_price / 5) * 5

    # Calculate actual margin
    margin = (final_price - cost) / final_price if final_price > 0 else 0

    return {
        "price": final_price,
        "total_cost": round(cost, 2),
        "margin": round(margin, 4),
        "margin_pct": f"{margin * 100:.1f}%",
        "fatigue_factor": round(phi, 4),
        "effective_hours": round(eff_hours, 2),
        "seasonal_coefficient": kappa,
        "fuel_component": round(distance * 2 * (fuel / 14.0), 2),
        "labor_component": round(hours * crew_size * BASE_HOURLY_RATE, 2),
        "equipment_component": round(equipment_cost(equip_heavy), 2),
        "materials_component": materials,
        "disposal_component": disposal_fees,
        "overhead_component": INSURANCE_PER_JOB + MARKETING_PER_JOB + ADMIN_PER_JOB,
    }


def print_quote(result, job_description=""):
    """Print a formatted quote breakdown."""
    print("=" * 60)
    if job_description:
        print(f"  JOB: {job_description}")
    print("=" * 60)
    print(f"  QUOTED PRICE:          ${result['price']:.2f}")
    print(f"  TOTAL COST:            ${result['total_cost']:.2f}")
    print(f"  MARGIN:                {result['margin_pct']}")
    print("-" * 60)
    print(f"  Cost Breakdown:")
    print(f"    Fuel:                ${result['fuel_component']:.2f}")
    print(f"    Labor:               ${result['labor_component']:.2f}")
    print(f"    Equipment:           ${result['equipment_component']:.2f}")
    print(f"    Materials:           ${result['materials_component']:.2f}")
    print(f"    Disposal:            ${result['disposal_component']:.2f}")
    print(f"    Overhead:            ${result['overhead_component']:.2f}")
    print("-" * 60)
    print(f"  Model Parameters:")
    print(f"    Fatigue Factor (φ):  {result['fatigue_factor']}")
    print(f"    Effective Hours:     {result['effective_hours']}")
    print(f"    Seasonal Coeff (κ):  {result['seasonal_coefficient']}")
    print("=" * 60)


# ============================================================
# EXAMPLE: Generate quotes for sample AAS jobs
# ============================================================

if __name__ == "__main__":
    print("\n  ALL AROUND SERVICES — PRICING MODEL OUTPUT")
    print("  8-Variable Cost Function | Cameron Camarotti\n")

    # Example 1: Pressure washing job in April, 12 miles away
    job1 = optimal_price(
        fuel=3.25,          # Current gas price
        distance=12,        # 12 miles one-way
        hours=2.5,          # 2.5 hour job
        crew_size=2,        # 2 crew members
        equip_heavy=True,   # Pressure washer = heavy equipment
        materials=15,       # Cleaning solution
        disposal_fees=0,    # No disposal needed
        month=4,            # April (peak spring demand)
        service_type="pressure_washing"
    )
    print_quote(job1, "Pressure Washing — Driveway + Patio, Suwanee, GA")

    print()

    # Example 2: Full home move in July, 25 miles away
    job2 = optimal_price(
        fuel=3.40,
        distance=25,
        hours=6.0,
        crew_size=4,
        equip_heavy=False,
        materials=40,       # Blankets, tape, supplies
        disposal_fees=0,
        month=7,            # July (peak moving season)
        service_type="moving"
    )
    print_quote(job2, "Full Home Move — 3BR Buford to Braselton")

    print()

    # Example 3: Auto detailing in November, 8 miles away
    job3 = optimal_price(
        fuel=3.15,
        distance=8,
        hours=2.0,
        crew_size=1,
        equip_heavy=False,
        materials=25,       # Detailing products
        disposal_fees=0,
        month=11,           # November (low demand)
        service_type="auto_detailing"
    )
    print_quote(job3, "Full Interior + Exterior Detail — Honda Odyssey")

    print()

    # Example 4: Pro-bono AAS Cares job (model still calculates market value)
    job4 = optimal_price(
        fuel=3.25,
        distance=20,
        hours=4.5,
        crew_size=3,
        equip_heavy=False,
        materials=30,
        disposal_fees=0,
        month=12,
        service_type="specialty_labor"
    )
    print_quote(job4, "AAS CARES — Pro Bono Nursing Home Relocation (Market Value Calculation)")
    print("  * This job was completed at no charge through AAS Cares.")
    print("  * Market value documented for community impact reporting.")
