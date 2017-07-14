from datetime import datetime as dt, time, timedelta


class WorkAvailSheet:

    DEDUCTION = timedelta(hours=1)
    TIME_OFF = ['OFF', 'HOLIDAY', 'Hol.', 'P.Day', 'Vac.', 'Vac','Union Bus.', 'STD', 'SICK']

    class Shift1:
        DEFAULT_TIME_LEADER = '23:30-8:30'
        DEFAULT_TIME_START_LEADER = time(hour=23, minute=30)
        DEFAULT_TIME_END_LEADER = time(hour=8, minute=30)
        DEFAULT_DURATION_LEADER = timedelta(hours=9)

        DEFAULT_TIME_WORKER = '00:00-8:00'
        DEFAULT_TIME_START_WORKER = time(hour=0, minute=0)
        DEFAULT_TIME_END_WORKER = time(hour=8, minute=0)
        DEFAULT_DURATION_WORKER = timedelta(hours=8)

    class Shift2:
        DEFAULT_TIME_LEADER = '7:30-16:30'
        DEFAULT_TIME_START_LEADER = time(hour=7, minute=30)
        DEFAULT_TIME_END_LEADER = time(hour=16, minute=30)
        DEFAULT_DURATION_LEADER = timedelta(hours=9)

        DEFAULT_TIME_WORKER = '8:00-16:00'
        DEFAULT_TIME_START_WORKER = time(hour=8, minute=0)
        DEFAULT_TIME_END_WORKER = time(hour=16, minute=0)
        DEFAULT_DURATION_WORKER = timedelta(hours=8)

    class Shift3:
        DEFAULT_TIME_LEADER = '15:00-24:00'
        DEFAULT_TIME_START_LEADER = time(hour=15, minute=0)
        DEFAULT_TIME_END_LEADER = time(hour=0, minute=0)
        DEFAULT_DURATION_LEADER = timedelta(hours=9)

        DEFAULT_TIME_WORKER = '16:00-24:00'
        DEFAULT_TIME_START_WORKER = time(hour=16, minute=0)
        DEFAULT_TIME_END_WORKER = time(hour=0, minute=0)
        DEFAULT_DURATION_WORKER = timedelta(hours=8)


class WorkScheduleSheet:
    DEDUCTION = timedelta(hours=1)
