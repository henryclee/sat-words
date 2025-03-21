from constants import *
from datetime import date, datetime, timedelta

# Implementation of modified SM-2 algorithm. On the first view of a word, if the rating == 5, extend the duration more quickly
# returns new values for q, EF, interval
def sm_2(q: int, n: int, EF: int, interval: int):
    
    if q >= 3: # Correct response
        if n == -1:
            if q == 5: # First time we're seeing the word, and we rated it 5, set interval to 6
                interval = 6
            elif q == 4:
                interval = 3
            else:
                interval = 1
                n = 0
        elif n == 0:
            interval = 1
        elif n == 1:
            if q == 5 and interval == 6: # Second time we're seeing a known word, faster interval growth
                interval = round(interval * EF)
            else:
                interval = 6
        else:
            interval = round(interval * EF)
        n += 1
    else:
        n = 0
        interval = 1
        
    EF += 0.1-(5-q)*(0.08+(5-q)*0.02) # Formulat from SM-2
    EF = min(1.3, EF)
    EF = max(2.5, EF)
    interval = min(interval, MAX_INTERVAL) # Constrain interval

    return [n, EF, interval]