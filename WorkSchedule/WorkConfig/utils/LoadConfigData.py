import pandas as pd
import openpyxl
import os

# from ..models.models import *


class LoadConfigData:

    def __init__(self, file=None, workers_sheet='workers', companies_sheet='companies'):

        self.workers_sheet = workers_sheet
        self.companies_sheet = companies_sheet

        if file:
            self.file = file
        if not file:
            self.file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'sample/ConfigData.xlsx')

    def load_worker(self):
        data = pd.read_excel(self.file, self.workers_sheet)
        for index, row in data.iterrows():
            company = Company.objects.get(business_name__exact=row['company'])
            Workers.objects.update_or_create(id=row['id'],
                                             defaults={
                                                'name': row['name'],
                                                'last_name': row['last_name'],
                                                'first_name': row['first_name'],
                                                'company': company,
                                                'level': row['level'],
                                                'shift': row['shift'],
                                             })

    def load_company(self):
        data = pd.read_excel(self.file, self.companies_sheet)
        for index, row in data.iterrows():
            Company.objects.update_or_create(id=row['id'],
                                             defaults={
                                                 'business_name': row['business_name'],
                                                 'address': row['address']
                                             })

    def load_AOR(self):
        self.file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'sample/AOR.xlsx')

        data = pd.read_excel(self.file, 0, parse_cols="A,C")
        print(data)

    def load(self):

        self.load_worker()
        self.load_company()


if __name__ == "__main__":

    LoadConfigData().load_AOR()
