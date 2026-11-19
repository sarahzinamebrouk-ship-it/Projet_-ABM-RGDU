from parameters import EXPLORATION


def choose_effort(scores, draw, exploration=EXPLORATION):
    # Exploration: randomly try one of the two effort levels in 10% of periods
    # under the baseline setting (the rate is varied in sensitivity analysis).
    if draw < exploration:
        return int(draw < exploration / 2)
  
    # Otherwise choose the effort with the higher score; ties select standard effort.
    return int(scores[1] > scores[0])
