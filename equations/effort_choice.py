from parameters import EXPLORATION


def choose_effort(scores, draw, exploration=EXPLORATION):
  
    if draw < exploration:
        return int(draw < exploration / 2)
  
    return int(scores[1] > scores[0])
