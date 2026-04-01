# AAS Pricing Model — 8-Variable Cost Function with Monte Carlo Simulation

A Python implementation of the multivariable cost function I built for [All Around Services](https://allaroundservice.com), a home services company I founded in January 2025. The model takes eight real-world business inputs and outputs an optimized price for any service job. It has been back-tested against all 44 jobs completed to date, generating $14,595 in revenue at a 93.7% job-level margin.

## The Problem

Most home service companies price jobs using gut feel, competitor matching, or simple hourly rates. These approaches ignore the actual variables that determine whether a job is profitable: how far you're driving, how tired your crew gets over multi-hour jobs, whether your equipment is degrading, what season it is, and what the local market will bear. I wanted a pricing method that accounts for all of these factors mathematically.

## The Model

The cost function takes eight inputs and produces an optimized price:

**C(f, d, h, φ, e, m, r, κ) → Price**

| Variable | Symbol | Description | Unit |
|----------|--------|-------------|------|
| Fuel Cost | f | Current fuel price × route distance efficiency | $/gallon |
| Route Distance | d | Round-trip distance to job site | miles |
| Labor Hours | h | Estimated crew-hours for the job | hours |
| Crew Fatigue Factor | φ | Declining efficiency over extended jobs (modeled as exponential decay) | dimensionless (0-1) |
| Equipment Depreciation | e | Per-job equipment wear based on usage intensity | $/job |
| Materials Cost | m | Consumables and supplies required | $ |
| Disposal Fees | r | Waste removal and dump fees if applicable | $ |
| Seasonal Demand Coefficient | κ | Market demand multiplier based on time of year | dimensionless |

### The Fatigue Factor (φ)

The crew fatigue factor models the observation that crew productivity declines over long jobs. A crew that's efficient at hour 1 is measurably slower at hour 6. This follows an exponential decay pattern:

```
φ(h) = e^(-λh)
```

Where λ is the decay constant calibrated from actual AAS job data. This is the same mathematical framework used to model energy dissipation in physics — which is where I first encountered the concept in my AP Physics class.

### The Seasonal Demand Coefficient (κ)

Demand for different services varies by season. Pressure washing peaks in spring. Moving peaks in summer. The seasonal coefficient adjusts pricing to reflect market conditions:

- κ > 1.0: High demand season (price premium justified by market)
- κ = 1.0: Normal demand
- κ < 1.0: Low demand season (price discount to maintain volume)

κ values are calibrated from AAS's actual monthly revenue distribution across 14 months of operations.

### Optimization Logic

The model uses partial derivative analysis to find the price point that maximizes margin:

```
∂(Revenue - Cost) / ∂(Price) = 0
```

Subject to the constraint that the price must remain within the competitive range for the service category and geographic area. This is fundamentally a constrained optimization problem — the same class of problems studied in multivariable calculus.

## Monte Carlo Simulation

To stress-test the model's robustness, I run a Monte Carlo simulation with 10,000 randomized scenarios. Each scenario draws input values from probability distributions calibrated to real AAS operating data:

- Fuel cost: Normal distribution based on 14-month gas price history
- Route distance: Log-normal distribution based on actual job distances
- Labor hours: Distribution based on historical job durations by service type
- Seasonal demand: Varies by month using actual revenue patterns

The simulation produces:
- **Expected margin distribution** — probability of achieving target margins under varying conditions
- **Break-even analysis** — minimum conditions required for profitability
- **Sensitivity analysis** — which variables have the largest impact on margin
- **Worst-case scenarios** — performance under adversarial conditions (high fuel + long distance + low demand)

## Results

Back-tested against all 44 AAS jobs:
- **Revenue generated:** $14,595
- **Job-level margin:** 93.7%
- **Net margin (after all overhead):** 82.1%
- **Model accuracy:** Predicted margins within ±3% of actual results on 41/44 jobs

## Project Structure

```
aas-pricing-model/
│
├── README.md                  # This file
├── pricing_model.py           # Core 8-variable cost function
├── monte_carlo.py             # Monte Carlo simulation engine
├── visualization.py           # Charts and analysis output
├── config.py                  # Model parameters and calibration data
├── data/
│   └── job_history.csv        # Anonymized job data for back-testing
└── output/
    ├── margin_distribution.png
    ├── sensitivity_analysis.png
    └── simulation_results.csv
```

## How to Run

```bash
# Clone the repository
git clone https://github.com/cameroncc333/aas-pricing-model.git
cd aas-pricing-model

# Install dependencies
pip install numpy pandas matplotlib scipy

# Run the pricing model for a sample job
python pricing_model.py

# Run the Monte Carlo simulation (10,000 scenarios)
python monte_carlo.py

# Generate visualization charts
python visualization.py
```

## Connection to Academics

This project applies concepts from three AP courses I'm taking at Mill Creek High School:

- **AP Calculus AB** — Partial derivatives, optimization, rates of change
- **AP Physics 1 & 2** — Exponential decay modeling (fatigue factor), energy dissipation frameworks
- **AP Computer Science** — Python implementation, data structures, algorithmic thinking

## About the Business

All Around Services was founded in January 2025 and operates across 15+ cities in the Atlanta metro area. Services include moving, pressure washing, auto and boat detailing, landscaping, and specialty labor. The company also runs AAS Cares, a pro-bono initiative that has contributed $1,250 in donated labor value to elderly and underserved community members.

- **Website:** [allaroundservice.com](https://allaroundservice.com)
- **Facebook:** [All Around Services](https://www.facebook.com/profile.php?id=61588386760982)

Full business documentation, financial model, and verified job history available in the password-protected Founder Vault at [allaroundservice.com](https://allaroundservice.com).

## Author

**Cameron Camarotti**
- Founder, All Around Services
- Junior at Mill Creek High School (Class of 2027)
- 4.1 GPA | 12 AP Courses
- Varsity Football — All-Region Honorable Mention
https://www.linkedin.com/in/cameron-camarotti-6997152b0/
- [All Around Services](https://allaroundservice.com)
