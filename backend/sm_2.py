from constants import *
from datetime import date, datetime, timedelta

# Implementation of modified SM-2 algorithm. If a 
def sm_2(q: int, n: int, EF: int, interval: int):
    
    if q >= 3:
        if n == 0:
            if q == 5:
                interval = 6
            else:
                interval = 1
        elif n == 1:
            if q == 5 and interval == 6:
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

    return [n, EF, interval]