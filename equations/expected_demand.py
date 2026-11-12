from parameters import ALPHA, EMPLOYMENT_DEMAND_ELASTICITY, SECTOR_SENSITIVITY


def expected_demand(previous_expectation, sector, previous_gdp_gap):
    observed_demand = 1 + EMPLOYMENT_DEMAND_ELASTICITY * SECTOR_SENSITIVITY[sector] * previous_gdp_gap
    return (1 - ALPHA) * previous_expectation + ALPHA * observed_demand
