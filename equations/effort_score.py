from parameters import EFFORT_PENALTY


# Learning outcome: compare the firm's share of vacancies filled with the
# market fill rate, then subtract the resource cost of intensive effort.
def effort_score(hires, vacancies, market_fill_rate, effort, penalty=EFFORT_PENALTY):
    """Compare the firm's vacancy fill rate with the market, less effort cost."""
    # A firm filling the same share as the market scores 0 before the effort
    # penalty. Example: 2 / 4 / 0.4 - 1 - 0.10 = 0.15 for intensive effort.
    # If no vacancies can be filled, intensive effort receives only its penalty.
    if vacancies <= 0 or market_fill_rate <= 0:
        return -penalty * effort
    return hires / vacancies / market_fill_rate - 1 - penalty * effort
