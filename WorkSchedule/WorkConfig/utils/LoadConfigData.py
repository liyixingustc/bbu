import pandas as pd
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
        print(data)

    def load_company(self):
        data = pd.read_excel(self.file, self.companies_sheet)


    def load(self):

        self.load_worker()
        self.load_company()


if __name__=="__main__":

    LoadConfigData().load()

