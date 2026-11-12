from parameters import EFFORT_PENALTY


def effort_score(hires, vacancies, market_fill_rate, effort, penalty=EFFORT_PENALTY):
    """Model component description."""
    if vacancies <= 0 or market_fill_rate <= 0:
        return -penalty * effort
    return hires / vacancies / market_fill_rate - 1 - penalty * effort
