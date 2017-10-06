from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display

from bs4 import BeautifulSoup as bs
import os
import sys
import shutil
import glob
import time

import numpy as np
import pandas as pd
from openpyxl import load_workbook

sys.path.append('../..')
import django
from bbu.settings import BASE_DIR, MEDIA_ROOT

os.environ['DJANGO_SETTINGS_MODULE'] = 'bbu.settings'
django.setup()

from WorkSchedule.WorkConfig.processor.EquipmentLoadProcessor import EquipmentLoadProcessor
from WorkSchedule.WorkConfig.processor.PMsLoadProcessor import PMsLoadProcessor
from WorkSchedule.WorkConfig.processor.TasksLoadProcessor import TasksLoadProcessor

from WorkSchedule.WorkConfig.models.models import *
from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *


class SomaxSpider:

    DISPLAY = False

    account = 'BBUGRNATU'
    password = 'ARTHUR'

    somax_dashboard_url = 'https://somaxonline.somax.com/DashboardMain.aspx'
    somax_login_url = 'https://somaxonline.somax.com/Login.aspx'
    somax_equipment_url = 'https://somaxonline.somax.com/EquipmentSearch.aspx'
    somax_equipment_edit_url = 'https://somaxonline.somax.com/EquipmentEdit.aspx'
    somax_task_url = 'https://somaxonline.somax.com/WorkOrderSearch.aspx'
    somax_task_edit_url = 'https://somaxonline.somax.com/WorkOrderEdit.aspx'
    somax_pm_url = 'https://somaxonline.somax.com/PreventiveMaintenanceSearch.aspx'
    somax_pm_edit_url = 'https://somaxonline.somax.com/PreventiveMaintenanceDetails.aspx'

    somax_logo_id = 'imgLogo'
    somax_page_title_id = 'ctlPageDetails_lblPageTitle'
    somax_task_filter_work_order_id = 'MainContent_grdResults_DXFREditorcol0_I'
    somax_task_first_row_work_order_a_id = 'MainContent_grdResults_cell0_0_ColClientLookUpId_0'
    somax_task_first_row_work_order_td_id = 'MainContent_grdResults_tccell0_0'
    somax_task_detail_actual_open_span_id = 'MainContent_cpcActuals_lblHeaderCollapsed'
    somax_task_detail_actual_tab_a_id = 'MainContent_cpcActuals_ctl00_ASPxPageControlActuals_T1'
    somax_task_detail_actual_table_id = 'MainContent_cpcActuals_ctl00_ASPxPageControlActuals_grdWorkOrderLabor_DXMainTable'


    download_path = os.path.join(BASE_DIR, MEDIA_ROOT, 'spider', 'somax')

    def __init__(self, account=None, password=None):

        if not self.DISPLAY:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
        self.driver = self.chromedriver()
        # self.login(account, password)
        # self.cookies = self.driver.get_cookies()

    def firefoxdriver(self):
        driver = webdriver.Firefox(executable_path='/usr/bin/geckodriver')

        return driver


    def chromedriver(self):
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.download_path}
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(chrome_options=options,executable_path='/usr/bin/chromedriver')
        return driver

    def phantomjsdriver(self):

        driver = webdriver.PhantomJS()

        return driver

    def login(self, account=None, password=None):
        if account and password:
            self.account = account
            self.password = password
        self.driver.get(self.somax_login_url)
        self.driver.find_element_by_id('txtUserName').clear()
        self.driver.find_element_by_id('txtUserName').send_keys(self.account)
        self.driver.find_element_by_id('txtPassword').clear()
        self.driver.find_element_by_id('txtPassword').send_keys(self.password)
        self.driver.find_element_by_id('btnLogin').click()

        while True:
            if self.driver.current_url != self.somax_login_url:
                break
            time.sleep(1)
        return True

    def equipment_spider(self):
        self.driver.get(self.somax_equipment_url)
        current_url = self.driver.current_url
        if current_url == self.somax_login_url:
            self.login()

        before = os.listdir(self.download_path)
        self.get_and_ready(self.somax_equipment_url)
        self.driver.find_element_by_id('MainContent_uicSearchHeader_dxBtnExport').click()
        after = os.listdir(self.download_path)
        self.driver.execute_script("window.stop();")
        filename = self.get_download_file_name(before, after, self.download_path)
        if not filename:
            return None
        else:
            target_path = os.path.join(self.download_path, 'equipment')
            r = glob.glob(os.path.join(target_path, '*'))
            for i in r:
                    os.remove(i)

            shutil.move(os.path.join(self.download_path, filename),
                        os.path.join(target_path, filename))

        self.driver.quit()
        if not self.DISPLAY:
            self.display.stop()

        file_path = os.path.join(target_path, filename)
        EquipmentLoadProcessor.equipment_load_processor([file_path])

        return True

    def pm_spider(self):
        self.driver.get(self.somax_pm_url)
        current_url = self.driver.current_url
        if current_url == self.somax_login_url:
            self.login()

        before = os.listdir(self.download_path)
        self.get_and_ready(self.somax_pm_url)
        self.driver.find_element_by_id('MainContent_uicSearchHeader_dxBtnExport').click()
        after = os.listdir(self.download_path)
        self.driver.execute_script("window.stop();")
        filename = self.get_download_file_name(before, after, self.download_path)
        if not filename:
            return None
        else:
            target_path = os.path.join(self.download_path, 'pm')
            r = glob.glob(os.path.join(target_path, '*'))
            for i in r:
                    os.remove(i)

            shutil.move(os.path.join(self.download_path, filename),
                        os.path.join(target_path, filename))

        self.driver.quit()
        if not self.DISPLAY:
            self.display.stop()

        file_path = os.path.join(target_path, filename)
        PMsLoadProcessor.pms_load_processor([file_path])

        return True

    def task_spider(self):
        self.driver.get(self.somax_task_url)
        current_url = self.driver.current_url
        if current_url == self.somax_login_url:
            self.login()

        before = os.listdir(self.download_path)
        self.get_and_ready(self.somax_task_url)
        self.driver.find_element_by_id('MainContent_uicSearchHeader_dxBtnExport').click()
        after = os.listdir(self.download_path)
        self.driver.execute_script("window.stop();")
        filename = self.get_download_file_name(before, after, self.download_path)
        if not filename:
            return None
        else:
            target_path = os.path.join(self.download_path, 'task')
            r = glob.glob(os.path.join(target_path, '*'))
            for i in r:
                    os.remove(i)

            shutil.move(os.path.join(self.download_path, filename),
                        os.path.join(target_path, filename))

        self.driver.quit()
        if not self.DISPLAY:
            self.display.stop()

        file_path = os.path.join(target_path, filename)
        TasksLoadProcessor.tasks_load_processor([file_path])

        return True

    def task_edit_spider(self, work_orders_dict=None):
        if not work_orders_dict:
            return True

        # filter out no change record
        worker_order_df = pd.DataFrame.from_records(work_orders_dict)
        # worker_order_df = worker_order_df[worker_order_df['current_status'] != worker_order_df['current_status_somax']]
        # if worker_order_df.empty:
        #     return True

        # wait and check again
        # time.sleep(100)

        for index, row in worker_order_df.iterrows():
            work_order = row['work_order']
            tasks_obj = Tasks.objects.filter(work_order__exact=work_order)
            if tasks_obj.exists():
                current_status = tasks_obj[0].current_status
            else:
                continue

            worker_order_df.set_value(index, 'current_status', current_status)

        # filter out no change record
        # worker_order_df = worker_order_df[worker_order_df['current_status'] != worker_order_df['current_status_somax']]
        # if worker_order_df.empty:
        #     return True

        # edit somax
        self.driver.get(self.somax_task_url)
        current_url = self.driver.current_url
        if current_url == self.somax_login_url:
            self.login()

        self.get_and_ready(self.somax_task_url)

        for work_order_dict in work_orders_dict:

            work_order = work_order_dict['work_order']
            current_status = work_order_dict['current_status']

            self.get_work_order_detail(work_order)

        self.driver.quit()
        if not self.DISPLAY:
            self.display.stop()

        return True

    def task_actual_hour_spider(self, start, end):

        # remove
        data = pd.read_excel('Work hour result.xlsx')
        data = data.loc[int(start): int(end)]
        data_unfilled = data[data['hours'].isnull()]
        # data_unfilled = data[data['hours']==-1]

        data['Scheduled'] = data['Scheduled'].apply(lambda x: x.date())
        data['Created'] = data['Created'].apply(lambda x: x.date())

        self.driver.get(self.somax_task_url)
        current_url = self.driver.current_url
        if current_url == self.somax_login_url:
            self.login()

        self.get_and_ready(self.somax_task_url)

        i = 0
        for index, row in data_unfilled.iterrows():
            try:
                work_order = str(row['Work Order'])
                self.get_work_order_detail(work_order)

                element_click_plus = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.ID, self.somax_task_detail_actual_open_span_id)))
                element_click_plus.click()

                element_click_tab = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.ID, self.somax_task_detail_actual_tab_a_id)))
                element_click_tab.click()

                element_table = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, self.somax_task_detail_actual_table_id)))

                table_html = element_table.get_attribute('outerHTML')
                soup = bs(table_html, 'lxml')

            # with open("output1.html", "w") as file:
            #     file.write(str(soup))
            # print(table_html)
            # print(pd.read_html(table_html))

                columns = ['username_somax', 'full_name', 'date', 'hours', 'value']
                table_data = pd.DataFrame(columns=columns)

                for script in soup.find_all('script'):
                    script.extract()
                tr_s = soup.find_all('tr', class_='dxgvDataRow_GridTheme')

                for tr in tr_s:
                    td_s = tr.find_all('td')[1:-1]
                    row = {'username_somax': td_s[0].get_text(),
                           'full_name': td_s[1].get_text(),
                           'date': td_s[2].get_text(),
                           'hours': float(td_s[3].get_text()),
                           'value': float(td_s[4].get_text())
                           }

                    table_data = table_data.append(pd.Series(row), ignore_index=True)

                total_actual = table_data['hours'].sum()

                # data.set_value(index, 'hours', total_actual)

            except Exception as e:
                print(e)
                total_actual = -1
                # data.set_value(index, 'hours', -1)

            self.to_excel(index + 2, total_actual)
            print(i)
            i = i + 1
            self.get_and_ready(self.somax_task_url)

        self.driver.quit()
        if not self.DISPLAY:
            self.display.stop()

        return True

    def get_work_order_detail(self, work_order):

        try:
            element_text = self.driver.find_element_by_id(self.somax_task_first_row_work_order_a_id).text
        except Exception as e:
            element_text = ''

        if element_text != work_order:
            element_filter = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, self.somax_task_filter_work_order_id)))
            self.driver.execute_script("arguments[0].setAttribute('value', {work_order})".format(work_order=work_order),
                                       element_filter)
            element_filter.send_keys(Keys.ENTER)

            WebDriverWait(self.driver, 60).until(
                EC.text_to_be_present_in_element((By.ID, self.somax_task_first_row_work_order_a_id), str(work_order)))

        element_click = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.ID, self.somax_task_first_row_work_order_a_id)))
        element_click.click()

        return True

    def get_and_ready(self, url):
        self.driver.get(url)
        while True:
            if self.driver.current_url == url:
                break
            time.sleep(1)
        return True

    @staticmethod
    def get_download_file_name(before, after, download_path):
        change = set(after) - set(before)

        if len(change) == 1:
            while True:
                if str(list(change)[0]).endswith('.csv'):
                    break
                after = os.listdir(download_path)
                change = set(after) - set(before)
                time.sleep(1)
            file_name = change.pop()
        else:
            return None

        return file_name

    def spider(self):
        # self.equipment_spider()
        # self.pm_spider()
        self.task_spider()

    @classmethod
    def to_excel(cls, row, value):
        wb = load_workbook('/home/arthurtu/projects/bbu/spider/somax/Work hour result.xlsx')
        ws = wb.get_active_sheet()
        ws.cell(row=row, column=16).value = value

        wb.save('/home/arthurtu/projects/bbu/spider/somax/Work hour result.xlsx')




if __name__ == '__main__':
    # SomaxSpider().task_edit_spider([{'work_order': '17037018',
    #                                  'current_status': 'Scheduled',
    #                                  'current_status_somax': 'Scheduled'}])
    SomaxSpider().equipment_spider()
    # SomaxSpider().task_spider()
    # start = input('start:')
    # end = input('end:')
    # SomaxSpider().task_actual_hour_spider(start, end)
