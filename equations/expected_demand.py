from parameters import ALPHA, EMPLOYMENT_DEMAND_ELASTICITY, SECTOR_SENSITIVITY


def expected_demand(previous_expectation, sector, previous_gdp_gap):
    # Desired employment follows expected demand (elasticity 1.0). Firms smooth
    # their expectations using ALPHA = 0.4, the course-model adjustment parameter.
    # Example: expectation 1.0, Trade sensitivity 1.10, and GDP 1% below central:
    # observed demand = 0.989; updated expectation = 0.6 * 1.0 + 0.4 * 0.989 = 0.9956.
    observed_demand = 1 + EMPLOYMENT_DEMAND_ELASTICITY * SECTOR_SENSITIVITY[sector] * previous_gdp_gap
    return (1 - ALPHA) * previous_expectation + ALPHA * observed_demand
