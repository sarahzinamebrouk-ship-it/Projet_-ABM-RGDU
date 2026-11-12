T_MIN = 0.02
T_DELTA_UNDER_50 = 0.3781
T_DELTA_50_AND_OVER = 0.3821
LEGACY_T_UNDER_50 = 0.3193
LEGACY_T_50_AND_OVER = 0.3233

LEGACY_HEALTH_THRESHOLD_IN_MIN_WAGES = 2.396
LEGACY_FAMILY_ALLOWANCE_THRESHOLD_IN_MIN_WAGES = 3.354

CONTRIBUTION_RATE = 0.41
ELASTICITY_AT_MIN_WAGE = -0.4
MU = -0.2

SECTORS = [
    "Accommodation and food services",
    "Trade",
    "Industry",
    "Information and communication",
    "Transportation and warehousing",
    "Construction",
]

FIRM_PROFILES = [
    ("Small", "Near minimum wage"),
    ("Medium", "Intermediate"),
    ("Large", "High"),
    ("Small", "Intermediate"),
    ("Medium", "High"),
    ("Large", "Near minimum wage"),
]
WAGE_LEVELS = ["Near minimum wage", "Intermediate", "High"]

MODEL_SCALE = 0.01

EMPLOYEES_BY_SIZE = {"Small": 27, "Medium": 553, "Large": 13321}

NET_TO_GROSS_RATIO = 2733 / 3602
GROSS_MIN_WAGE_JANUARY_2024 = 11.65 * 151.67
GROSS_MIN_WAGE_2026 = 1867.02

NATIONAL_WAGES_IN_MIN_WAGES = {
    "Near minimum wage": 1.2,
    "Intermediate": 2190 / NET_TO_GROSS_RATIO / GROSS_MIN_WAGE_JANUARY_2024,
    "High": 4334 / NET_TO_GROSS_RATIO / GROSS_MIN_WAGE_JANUARY_2024,
}

NET_WAGE_BY_SECTOR = {
    "Accommodation and food services": 1980,
    "Trade": 2530,
    "Industry": 3010,
    "Information and communication": 3900,
    "Transportation and warehousing": 2590,
    "Construction": 2440,
}
OVERALL_NET_WAGE = 2730



SECTORS = [
    "Accommodation and food services",
    "Trade",
    "Industry",
    "Information and communication",
    "Transportation and warehousing",
    "Construction",
]

FIRM_PROFILES = [
    ("Small", "Near minimum wage"),
    ("Medium", "Intermediate"),
    ("Large", "High"),
    ("Small", "Intermediate"),
    ("Medium", "High"),
    ("Large", "Near minimum wage"),
]
WAGE_LEVELS = ["Near minimum wage", "Intermediate", "High"]

MODEL_SCALE = 0.01

EMPLOYEES_BY_SIZE = {"Small": 27, "Medium": 553, "Large": 13321}

NET_TO_GROSS_RATIO = 2733 / 3602
GROSS_MIN_WAGE_JANUARY_2024 = 11.65 * 151.67
GROSS_MIN_WAGE_2026 = 1867.02

NATIONAL_WAGES_IN_MIN_WAGES = {
    "Near minimum wage": 1.2,
    "Intermediate": 2190 / NET_TO_GROSS_RATIO / GROSS_MIN_WAGE_JANUARY_2024,
    "High": 4334 / NET_TO_GROSS_RATIO / GROSS_MIN_WAGE_JANUARY_2024,
}

NET_WAGE_BY_SECTOR = {
    "Accommodation and food services": 1980,
    "Trade": 2530,
    "Industry": 3010,
    "Information and communication": 3900,
    "Transportation and warehousing": 2590,
    "Construction": 2440,
}
OVERALL_NET_WAGE = 2730

AVERAGE_EMPLOYMENT_2025_THOUSANDS = {
    "Accommodation and food services": 1308.0,
    "Trade": 3373.1,
    "Industry": 420.4 + 648.2 + 8.8 + 421.1 + 359.6 + 1396.8,
    "Information and communication": 912.6,
    "Transportation and warehousing": 1457.9,
    "Construction": 1539.7,
}
TOTAL_BASE_EMPLOYMENT = sum(AVERAGE_EMPLOYMENT_2025_THOUSANDS.values()) * 1000
NATIONAL_WAGE_LEVEL_SHARES = {"Near minimum wage": 0.39, "Intermediate": 0.42, "High": 0.19}
WAGE_LEVEL_DISTRIBUTION = {sector: NATIONAL_WAGE_LEVEL_SHARES for sector in SECTORS}

TEST_WAGE_LEVEL_DISTRIBUTION = {
    "Accommodation and food services": {"Near minimum wage": 0.60, "Intermediate": 0.35, "High": 0.05},
    "Trade": {"Near minimum wage": 0.40, "Intermediate": 0.45, "High": 0.15},
    "Industry": {"Near minimum wage": 0.15, "Intermediate": 0.55, "High": 0.30},
    "Information and communication": {"Near minimum wage": 0.05, "Intermediate": 0.40, "High": 0.55},
    "Transportation and warehousing": {"Near minimum wage": 0.30, "Intermediate": 0.55, "High": 0.15},
    "Construction": {"Near minimum wage": 0.35, "Intermediate": 0.50, "High": 0.15},
}



QUALIFICATION_BY_WAGE_LEVEL = {"Near minimum wage": 0, "Intermediate": 1, "High": 2}
VACANCY_RATE = 0.023
PERMANENT_CONTRACT_ENDINGS_2025 = {
    "Accommodation and food services": 616776,
    "Trade": 797573,
    "Industry": 140758 + 38898 + 25306 + 173402 + 33937,
    "Information and communication": 150551,
    "Transportation and warehousing": 294332,
    "Construction": 334814,
}

UNEMPLOYMENT_RATE_BY_QUALIFICATION = {0: 0.147, 1: 0.091, 2: 0.053}

EMPLOYMENT_TO_UNEMPLOYMENT_RATE_PER_QUARTER = 0.018
AVERAGE_SEPARATION_RATE_PER_QUARTER =(
    sum(PERMANENT_CONTRACT_ENDINGS_2025.values()) / (sum(AVERAGE_EMPLOYMENT_2025_THOUSANDS.values()) * 1000) / 4)

SEPARATIONS_TO_UNEMPLOYMENT_SHARE = EMPLOYMENT_TO_UNEMPLOYMENT_RATE_PER_QUARTER / AVERAGE_SEPARATION_RATE_PER_QUARTER

UNEMPLOYMENT_TO_INACTIVITY_RATE = 0.227
INACTIVITY_TO_UNEMPLOYMENT_RATE = 0.058

UNEMPLOYED_EXPONENT = 0.5

HIRING_CHANCE_DECLINE_QUARTERS = 3
HIRING_CHANCE_DECLINE = 0.45
LONG_TERM_UNEMPLOYMENT_QUARTERS = 4
LONG_TERM_UNEMPLOYMENT_SHARE = 566 / 2451




EURO_AREA_GDP_GROWTH = {
    "central": [0.4, 0.3, 0.3, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3],
    "favorable": [0.4, 0.3, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3],
    "Unfavorable": [0.2, 0.2, 0.3, 0.3, 0.3, 0.4, 0.4, 0.4, 0.4],
    "severe": [-0.2, 0.0, 0.1, 0.2, 0.3, 0.4, 0.4, 0.4, 0.4],
}
ALPHA = 0.40

SECTOR_SENSITIVITY = {
    "Accommodation and food services": 1.20,
    "Trade": 1.10,
    "Industry": 0.90,
    "Information and communication": 1.00,
    "Transportation and warehousing": 0.95,
    "Construction": 1.15,
}
EMPLOYMENT_DEMAND_ELASTICITY = 1.0

EFFORT_ADVANTAGE = 0.5
EFFORT_PENALTY = 0.10
LEARNING_GAIN = 0.10
EXPLORATION = 0.10


NUMBER_OF_QUARTERS = 60
LAYOFF_RATE = 0.25


ASSUMPTIONS = [
    ["RGDU formula: minimum rate 0.02; size adjustment 0.3781 / 0.3821; zero from 3 minimum wages", "Source", "Decree no. 2025-887", "No"],
    ["Legacy relief: 0.3193 / 0.3233; health contribution relief to 2.396 minimum wages; family benefits to 3.354", "Source", "Tissot (2025); Legisocial and Previssima", "No"],
    ["Reference firm sizes: 27 / 553 / 13,321 employees, used for the 50-employee threshold", "Source", "Insee, firms by size category, 2023", "No"],
    ["Median and 90th-percentile net wages: 2,190 and 4,334 euros", "Source", "Insee survey no. 2079", "No"],
    ["Wages by sector are proportional to the sector's average wage", "Source and assumption", "Insee dataset 2381338", "No"],
    ["Near-minimum-wage profile set to 1.2 minimum wages", "Assumption (value)", "DGT guide (2024, pp. 14, 16); CGT document (2018) is a policy claim, not an observed value", "Yes (1.1 and 1.3)"],
    ["Wage level proxies qualification: below high school, high school, and post-secondary", "Assumption", "DGT guide (2024): job classification relates education and minimum pay; simplified by the project", "No"],
    ["Employee shares by wage level: 39 / 42 / 19 percent", "Source and calculation", "Insee survey no. 2132 (2025), figure 3", "Yes (alternative sector distributions)"],
    ["Economy scaled to one hundredth: one simulated employee represents 100 actual employees", "Calculation assumption", "Used to keep the model fast; results are multiplied by 100", "No"],
    ["Employees are represented as firm-level counts, not individual agents", "Acknowledged limitation", "Simplification; unemployed people are represented as agents", "No"],
    ["Unemployment rates by qualification: 14.7 / 9.1 / 5.3 percent", "Calibration source", "Insee Reference Series, \1 2026, unemployment inequalities (2025)", "No"],
    ["Vacancy rate of 2.3 percent; vacancies are allocated by separation rates", "Source and calibration assumption", "Dares Focus no. 33 (2024)", "No"],
    ["Sector separation rate based on annual permanent-contract endings divided by four", "Source and assumption", "Dares 2025 contract endings; Insee employment", "No"],
    ["About one third of separations lead to unemployment", "Calibration to observed data", "Insee Reference Series, \1 2025: 1.8 percent of employees move to unemployment per quarter", "Yes (20 and 50 percent)"],
    ["Unemployment-to-inactivity transition: 22.7 percent per quarter", "Source", "Insee Reference Series, \1 2025, labor market transitions (2024)", "Yes (0, 10 and 30 percent)"],
    ["Inactivity-to-unemployment transition: 5.8 percent per quarter", "Source", "Insee Reference Series, \1 2025, labor market transitions (2024)", "No"],
    ["Initial inactive population balances transitions; total employees, unemployed and inactive people is conserved", "Calculation assumption", "The inactive population is unavailable for the six sectors; this affects the source of new hires", "Yes (inactivity exit rate)"],
    ["Employer contributions set to 41 percent of gross wages", "Assumption (value)", "Inspired by Albertini et al. (2025); other references suggest 44 to 47 percent", "Yes (44 and 47 percent)"],
    ["Employment elasticity: -0.4 at minimum wage, zero at 2 minimum wages, plus mu = -0.2", "Source", "Bozio and Wasmer (2024), p. 194", "Yes (-0.2 and -0.6)"],
    ["Cobb-Douglas matching function with unemployed-worker exponent 0.5", "Source (range 0.5 to 0.7)", "Petrongolo and Pissarides (2001)", "Yes (0.7)"],
    ["Unemployed agents' hiring weight falls by 45 percent after three quarters", "Source", "Kroft, Lange and Notowidigdo (2013)", "No"],
    ["Long-term unemployment means four quarters or more", "Definition", "Insee (one year); used for validation, not calibration", "No"],
    ["Firms lay off 25 percent of excess employment each quarter", "Assumption; form supported by sources", "Hamermesh and Pfann (1996); Bentolila and Bertola (1990)", "Yes (0, 25 and 100 percent)"],
    ["Recruitment effort can fill vacancies faster but uses resources", "Qualitative assumption supported by sources", "Davis, Faberman and Haltiwanger (2013); Gavazza, Mongey and Violante (2018)", "No"],
    ["Effort increases total labor-market matches according to the average weight of open vacancies", "Assumption (form)", "Inspired by Davis et al. (2013); exact functional form is a project assumption", "Yes (effort advantage 0, 0.25 and 1)"],
    ["Effort advantage 0.5; effort penalty 0.10", "Assumptions (values)", "Not directly supported by a source; tested in sensitivity analysis", "Yes"],
    ["Firms learn through reinforcement and explore randomly in 10 percent of periods", "Form assumption supported by sources", "Brenner (2006); Roth and Erev (1995)", "Yes"],
    ["Learning gain 0.10; exploration rate 10 percent", "Assumptions (values)", "Not directly supported by a source", "Yes"],
    ["Baseline scenario disables learning; alternative scenario enables it", "Method choice", "Instructor instruction to compare baseline and alternative scenarios", "No"],
    ["Severe GDP scenario reproduces the observed 2026 shortfall of about 1.3 percent", "Source and assumption", "Insee, Rapid Information bulletin no. 263 (30 October 2026)", "No"],
    ["Central GDP scenario grows by 0.4 percent per quarter", "Assumption", "Project scenario", "No"],
    ["Sector demand sensitivity ranges from 0.9 to 1.2", "Assumption", "Project scenario", "No"],
    ["Expectations are smoothed using alpha = 0.4", "Source", "Instructor model parameter EXPECTATION_ADJUSTMENT", "No"],
    ["Thirty-six firm archetypes: six sectors by six profiles", "Assumption", "Project design choice", "No"],
    ["Results report simulation means and 95-percent confidence intervals using common random seeds", "Method", "Course guidance: account for simulation randomness; use the same seeds across scenarios", "No"],
]
