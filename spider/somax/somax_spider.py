from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as bs
import os
import shutil
import glob
import time

import numpy as np
import pandas as pd

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
    somax_task_filter_work_order_id = 'MainContent_grdResults_DXFREditorcol0_I'
    somax_task_first_row_work_order_a_id = 'MainContent_grdResults_cell0_0_ColClientLookUpId_0'
    somax_task_first_row_work_order_td_id = 'MainContent_grdResults_tccell0_0'

    download_path = os.path.join(BASE_DIR, MEDIA_ROOT, 'spider', 'somax')

    def __init__(self, account=None, password=None):

        self.driver = self.chromedriver()
        # self.login(account, password)
        # self.cookies = self.driver.get_cookies()

    def chromedriver(self):
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': self.download_path}
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(chrome_options=options)
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

        file_path = os.path.join(target_path, filename)
        TasksLoadProcessor.tasks_load_processor([file_path])

        return True

    def task_edit_spider(self, work_orders_dict=None):
        if not work_orders_dict:
            return True

        # filter out no change record
        worker_order_df = pd.DataFrame.from_records(work_orders_dict)
        worker_order_df = worker_order_df[worker_order_df['current_status'] != worker_order_df['current_status_somax']]
        if worker_order_df.empty:
            return True

        # wait and check again
        time.sleep(100)

        for index, row in worker_order_df.iterrows():
            work_order = row['work_order']
            tasks_obj = Tasks.objects.filter(work_order__exact=work_order)
            if tasks_obj.exists():
                current_status = tasks_obj[0].current_status
            else:
                continue

            worker_order_df.set_value(index, 'current_status', current_status)

        # filter out no change record
        worker_order_df = worker_order_df[worker_order_df['current_status'] != worker_order_df['current_status_somax']]
        if worker_order_df.empty:
            return True

        # edit somax
        self.driver.get(self.somax_task_url)
        current_url = self.driver.current_url
        if current_url == self.somax_login_url:
            self.login()

        self.get_and_ready(self.somax_task_url)

        for work_order_dict in work_orders_dict:

            work_order = work_order_dict['work_order']
            current_status = work_order_dict['current_status']

            element_text = self.driver.find_element_by_id(self.somax_task_first_row_work_order_a_id).text
            if element_text == work_order:
                element_click = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.ID, self.somax_task_first_row_work_order_a_id)))
            else:
                element_filter = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, self.somax_task_filter_work_order_id)))
                element_filter.clear()
                self.driver.find_element_by_id(self.somax_logo_id).click()

                WebDriverWait(self.driver, 60).until(
                    EC.text_to_be_present_in_element((By.ID, self.somax_task_filter_work_order_id), ''))
                element_filter.send_keys(work_order)
                self.driver.find_element_by_id(self.somax_logo_id).click()

                WebDriverWait(self.driver, 60).until(
                    EC.text_to_be_present_in_element((By.ID, self.somax_task_first_row_work_order_a_id), work_order))
                element_click = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.ID, self.somax_task_first_row_work_order_a_id)))

            element_click.click()

        self.driver.quit()

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

        # self.driver.get('https://somaxonline.somax.com/EquipmentSearch.aspx')
        # time.sleep(10)
        # self.driver.find_element_by_id('ctrlNavigation_btnSiteMap').click()
        # time.sleep(10)
        # self.driver.find_element_by_id('Equipment').click()
        # time.sleep(10)
        # self.driver.find_element_by_id('MainContent_uicSearchHeader_dxBtnExport').click()

        # soup = bs(self.driver.page_source, 'xml')
        # time.sleep(10)
        # # print(soup)

if __name__ == '__main__':
    SomaxSpider().task_edit_spider([{'work_order': '17037018',
                                     'current_status': 'Scheduled',
                                     'current_status_somax': 'Scheduled'}])
    # SomaxSpider().task_spider()
