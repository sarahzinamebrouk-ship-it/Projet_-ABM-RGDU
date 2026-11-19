from parameters import ELASTICITY_AT_MIN_WAGE, MU


# BLOCK 2 — Step 2: employment elasticity. Source: Bozio and Wasmer (2024).
# The wage-specific elasticity declines
# linearly from its minimum-wage value to zero at two minimum wages; add MU.
def employment_elasticity(wage_in_min_wages, elasticity_at_min_wage=ELASTICITY_AT_MIN_WAGE):
    """Employment response to a labor-cost change by wage level."""
    if wage_in_min_wages <= 1:
        individual_elasticity = elasticity_at_min_wage
    elif wage_in_min_wages >= 2:
        individual_elasticity = 0.0
    else:
        individual_elasticity = elasticity_at_min_wage * (2 - wage_in_min_wages)
    return individual_elasticity + MU
