from parameters import UNEMPLOYED_EXPONENT


def number_of_matches(m0, unemployed, vacancies, exponent=UNEMPLOYED_EXPONENT, efficiency=1.0):
    """Model component description."""
    matches = round(m0 * unemployed**exponent * vacancies ** (1 - exponent) * efficiency)
    return min(matches, unemployed, vacancies)
