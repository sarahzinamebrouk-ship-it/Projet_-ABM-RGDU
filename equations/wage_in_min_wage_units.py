from parameters import (
    NET_WAGE_BY_SECTOR,
    OVERALL_NET_WAGE,
    NATIONAL_WAGES_IN_MIN_WAGES,
)
# BLOCK 3 — Step 5: calculate wages in minimum-wage units by sector.
def wage_in_min_wage_units(sector, level):
    # Assumption: national wage for this level x (sector wage / overall wage).
    factor = NET_WAGE_BY_SECTOR[sector] / OVERALL_NET_WAGE
    # No modeled employee earns below the minimum wage; floor the result at 1.
    return max(1.0, NATIONAL_WAGES_IN_MIN_WAGES[level] * factor)
