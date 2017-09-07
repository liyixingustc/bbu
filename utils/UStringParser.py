import pandas as pd
from datetime import datetime, timedelta
import re

class UStringParser:

    @classmethod
    def task_description_parser(cls, string):
        due_days = cls.task_description_pm_due_days_parser(string)

        result = {'due_days': due_days}
        return result

    @classmethod
    def task_description_pm_due_days_parser(cls, string):
        regex = re.compile(r'((?P<due_days>\d{1,4})? DAY PM.*)')
        parts = regex.match(string)
        if parts:
            parts = parts.groupdict()
            due_days = timedelta(days=float(parts['due_days']))
            return due_days
        else:
            return None

    @classmethod
    def equipment_parser(cls, string):
        pass

    @classmethod
    def equipment_code_parser(cls, string):
        pass

    @classmethod
    def equipment_line_parser(cls, string):
        pass
#
# data = pd.read_excel('PMs.xlsx')
# for index, row in data.iterrows():
#     UStringParser.task_description_parser(row['Description'])
