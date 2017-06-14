from datetime import datetime as dt, time

class WorkAvailSheet:

    TIME_OFF = ['OFF', 'HOLIDAY', 'P.Day', 'Vac.', 'Union Bus.', 'STD', 'SICK']

    class Shift1:
        DEFAULT_TIME = '23:30-8:30'
        DEFAULT_TIME_START = time(hour=23, minute=30)
        DEFAULT_TIME_END = time(hour=8, minute=30)

    class Shift2:
        DEFAULT_TIME = '7:30-16:30'
        DEFAULT_TIME_START = time(hour=7, minute=30)
        DEFAULT_TIME_END = time(hour=16, minute=30)

    class Shift3:
        DEFAULT_TIME = '15:00-24:00'
        DEFAULT_TIME_START = time(hour=15, minute=0)
        DEFAULT_TIME_END = time(hour=0, minute=0)
