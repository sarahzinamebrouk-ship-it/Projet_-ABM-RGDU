from parameters import (
    NET_WAGE_BY_SECTOR,
    OVERALL_NET_WAGE,
    NATIONAL_WAGES_IN_MIN_WAGES,
)
def wage_in_min_wage_units(sector, level):
  
    factor = NET_WAGE_BY_SECTOR[sector] / OVERALL_NET_WAGE
  
    return max(1.0, NATIONAL_WAGES_IN_MIN_WAGES[level] * factor)