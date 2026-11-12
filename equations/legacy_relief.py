from parameters import (
    LEGACY_T_UNDER_50,
    LEGACY_T_50_AND_OVER,
    LEGACY_HEALTH_THRESHOLD_IN_MIN_WAGES,
    LEGACY_FAMILY_ALLOWANCE_THRESHOLD_IN_MIN_WAGES,
)


def legacy_relief(wage_in_min_wages, employee_count):
    """Total legacy-policy relief rate by wage and reference firm size."""
    rate = LEGACY_T_UNDER_50 if employee_count < 50 else LEGACY_T_50_AND_OVER
    relief_generale = (
        rate / 0.6 * (1.6 / wage_in_min_wages - 1)
        if 0 < wage_in_min_wages < 1.6
        else 0.0
    )
    maladie = 0.06 if wage_in_min_wages <= LEGACY_HEALTH_THRESHOLD_IN_MIN_WAGES else 0.0
    allocations_familiales = (
        0.018 if wage_in_min_wages <= LEGACY_FAMILY_ALLOWANCE_THRESHOLD_IN_MIN_WAGES else 0.0
    )
    return relief_generale + maladie + allocations_familiales
