"""
AAS Pricing Model — Configuration & Parameters
Calibrated from 14 months of All Around Services operating data (Jan 2025 - Present)
44 jobs | $14,595 revenue | 93.7% job-level margin
"""

# ============================================================
# COST FUNCTION PARAMETERS
# ============================================================

# Fuel parameters
AVG_FUEL_PRICE_PER_GALLON = 3.25      # Average gas price in Atlanta metro ($/gal)
VEHICLE_MPG = 14.0                      # Truck fuel efficiency (miles per gallon)
FUEL_COST_PER_MILE = AVG_FUEL_PRICE_PER_GALLON / VEHICLE_MPG

# Labor parameters
BASE_HOURLY_RATE = 25.00               # Base crew labor rate ($/hour/person)
AVG_CREW_SIZE = 2.5                     # Average crew members per job
FATIGUE_DECAY_CONSTANT = 0.08          # Lambda (λ) — exponential decay rate for crew efficiency
                                        # Calibrated from observed productivity drop on 6+ hour jobs

# Equipment depreciation
EQUIPMENT_DEPRECIATION_PER_JOB = 8.50  # Average equipment wear cost per job ($)
HEAVY_EQUIPMENT_MULTIPLIER = 2.0        # Multiplier for jobs requiring heavy equipment (pressure washer, trailer)

# Overhead allocation
INSURANCE_PER_JOB = 5.00               # Liability insurance allocation per job
MARKETING_PER_JOB = 3.00               # Marketing cost allocation per job
ADMIN_PER_JOB = 2.00                   # Administrative overhead per job

# Margin targets
TARGET_MARGIN = 0.85                    # Target job-level margin (85%)
MINIMUM_MARGIN = 0.60                   # Floor — never price below 60% margin
MARKUP_FACTOR = 1.45                    # Base markup over total cost

# ============================================================
# SEASONAL DEMAND COEFFICIENTS (κ)
# Calibrated from AAS monthly revenue distribution
# ============================================================

SEASONAL_COEFFICIENTS = {
    1: 0.75,    # January — low demand, post-holiday
    2: 0.80,    # February — still slow
    3: 1.05,    # March — spring pickup begins
    4: 1.20,    # April — strong spring demand (pressure washing peak starts)
    5: 1.30,    # May — peak spring (pressure washing, landscaping)
    6: 1.25,    # June — summer (moving season begins)
    7: 1.20,    # July — strong summer
    8: 1.15,    # August — late summer
    9: 1.00,    # September — back to school slowdown
    10: 0.90,   # October — fall decline
    11: 0.80,   # November — pre-holiday slow
    12: 0.85,   # December — holiday bump from gift jobs and year-end cleanups
}

# ============================================================
# SERVICE CATEGORY BASE RATES
# ============================================================

SERVICE_BASE_RATES = {
    "pressure_washing": {"base_price": 150, "avg_hours": 2.5, "materials_cost": 15},
    "moving": {"base_price": 200, "avg_hours": 4.0, "materials_cost": 25},
    "auto_detailing": {"base_price": 120, "avg_hours": 2.0, "materials_cost": 20},
    "boat_detailing": {"base_price": 180, "avg_hours": 3.0, "materials_cost": 30},
    "landscaping": {"base_price": 175, "avg_hours": 3.5, "materials_cost": 20},
    "junk_removal": {"base_price": 160, "avg_hours": 2.5, "materials_cost": 10},
    "specialty_labor": {"base_price": 140, "avg_hours": 3.0, "materials_cost": 15},
}

# ============================================================
# MONTE CARLO SIMULATION PARAMETERS
# ============================================================

MC_NUM_SIMULATIONS = 10000              # Number of randomized scenarios
MC_FUEL_PRICE_STD = 0.40               # Standard deviation of fuel price fluctuation
MC_DISTANCE_MEAN = 18.0                # Mean route distance (miles one-way)
MC_DISTANCE_STD = 12.0                 # Std dev of route distance
MC_HOURS_STD_FACTOR = 0.25             # Labor hours vary ±25% from estimate
MC_DEMAND_NOISE_STD = 0.10             # Seasonal coefficient noise

# ============================================================
# HISTORICAL PERFORMANCE (for back-testing validation)
# ============================================================

ACTUAL_TOTAL_REVENUE = 14595.00
ACTUAL_TOTAL_JOBS = 44
ACTUAL_PAID_JOBS = 41
ACTUAL_PRO_BONO_JOBS = 2
ACTUAL_DISCOUNTED_JOBS = 1
ACTUAL_NET_MARGIN = 0.821              # 82.1%
ACTUAL_JOB_MARGIN = 0.937              # 93.7%
ACTUAL_CITIES_SERVED = 15
ACTUAL_CREW_SIZE = 6
