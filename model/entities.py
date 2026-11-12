
from parameters import (
    MODEL_SCALE,
    AVERAGE_EMPLOYMENT_2025_THOUSANDS,
    PERMANENT_CONTRACT_ENDINGS_2025,
    EMPLOYEES_BY_SIZE,
    QUALIFICATION_BY_WAGE_LEVEL,
    WAGE_LEVEL_DISTRIBUTION,
    NATIONAL_WAGES_IN_MIN_WAGES,
    OVERALL_NET_WAGE,
    NET_WAGE_BY_SECTOR,
)


class Firm:
    """A firm agent with size, wage, separations, and recruitment-effort scores."""

    def __init__(self, index, sector, size, level, near_min_wage_value=None, distribution=None):
        self.index = index
        self.sector = sector
        self.size = size
      
        self.reference_employee_count = EMPLOYEES_BY_SIZE[size]
      
      
        distribution = distribution or WAGE_LEVEL_DISTRIBUTION
        sector_employment = AVERAGE_EMPLOYMENT_2025_THOUSANDS[sector] * 1000
        self.employee_count = round(MODEL_SCALE * sector_employment * distribution[sector][level] / 2)
        self.qualification = QUALIFICATION_BY_WAGE_LEVEL[level]
        factor = NET_WAGE_BY_SECTOR[sector] / OVERALL_NET_WAGE
      
        wage_national = NATIONAL_WAGES_IN_MIN_WAGES[level]
        if level == "Near minimum wage" and near_min_wage_value is not None:
            wage_national = near_min_wage_value
        self.wage_in_min_wages = max(1.0, wage_national * factor)
        self.separation_rate = PERMANENT_CONTRACT_ENDINGS_2025[sector] / (AVERAGE_EMPLOYMENT_2025_THOUSANDS[sector] * 1000) / 4
        self.initial_vacancies = 0.0
