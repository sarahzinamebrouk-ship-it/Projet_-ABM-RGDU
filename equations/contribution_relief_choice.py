from equations.legacy_relief import legacy_relief
from equations.rgdu_relief_rate import rgdu_relief_rate


def policy_relief_rate(policy, wage_in_min_wages, employee_count):
    """Model component description."""
    if policy == "rgdu":
        return rgdu_relief_rate(wage_in_min_wages, employee_count)
    if policy == "legacy":
        return legacy_relief(wage_in_min_wages, employee_count)
    if policy == "none":
        return 0.0
    raise ValueError("Policy must be 'none', 'legacy', or 'rgdu'.")
