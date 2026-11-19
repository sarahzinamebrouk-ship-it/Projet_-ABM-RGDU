from parameters import ELASTICITY_AT_MIN_WAGE, CONTRIBUTION_RATE
from equations.legacy_relief import legacy_relief
from equations.contribution_relief_choice import policy_relief_rate
from equations.employment_elasticity import employment_elasticity


# BLOCK 2 — Step 3: calculate the desired change in employment.
def desired_employment_change(policy, wage_in_min_wages, employee_count, elasticity_at_min_wage=ELASTICITY_AT_MIN_WAGE, contribution_cut=0.0):
    # Compare employer labor cost under the selected scheme with the previous scheme.
    # The denominator is the labor cost still payable under the previous scheme.
    avant = legacy_relief(wage_in_min_wages, employee_count)
    apres = policy_relief_rate(policy, wage_in_min_wages, employee_count)
    # A general contribution cut removes a share of the contributions still payable (0.10 = 10%).
    apres = apres + contribution_cut * (CONTRIBUTION_RATE - apres)
    cost_change = -(apres - avant) / (1 + CONTRIBUTION_RATE - avant)
    return employment_elasticity(wage_in_min_wages, elasticity_at_min_wage) * cost_change
