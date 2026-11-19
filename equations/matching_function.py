from parameters import UNEMPLOYED_EXPONENT


# BLOCK 4 — Step 6: calculate matches between unemployed workers and vacancies.
# Source: Petrongolo and Pissarides (2001): the unemployed-worker exponent is
# between 0.5 and 0.7. The baseline uses 0.5; 0.7 is tested for robustness.
def number_of_matches(m0, unemployed, vacancies, exponent=UNEMPLOYED_EXPONENT, efficiency=1.0):
    """Cobb-Douglas matching function, capped at the smaller market-side count."""
    # M = m0 x unemployed^exponent x vacancies^(1 - exponent) x efficiency.
    matches = round(m0 * unemployed**exponent * vacancies ** (1 - exponent) * efficiency)
    return min(matches, unemployed, vacancies)
