from Bot.Robot import Robot

# Selenium Imports
from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from userconfig import UserConfig
import json
import peewee
from models import Job

from helpers import Const
import re
from typing import Optional
import time


class AngelBot(Robot):
    def __init__(self, user_config: UserConfig, dry_run=False, reload_tags_blurbs=True):
        super().__init__(user_config, dry_run=dry_run, reload_tags_blurbs=reload_tags_blurbs)

    def login(self):
        self.driver.get(AngelConstants.URL.LOGIN)
        element_email = self.driver.find_element(By.ID, AngelConstants.Id.LOGIN_EMAIL)
        element_email.send_keys(self.user_config.EMAIL)
        self.driver.find_element(By.ID, AngelConstants.Id.LOGIN_PASSWORD).send_keys(self.user_config.PASSWORD)
        element_email.submit()

    def gather(self, query_parameters):
        def extract_job_key(url: str) -> Optional[str]:
            last_part_of_url = url.rsplit('/', 1)[-1]
            match = re.match(AngelConstants.Regex.JOB_KEY_FROM_URL, last_part_of_url)
            if match:
                return match.group(1)
            return None

        assert self._is_authenticated()

        string_parameters = AngelBot._encode_parameters(query_parameters)
        self.driver.get(AngelConstants.URL.JOBS + string_parameters)

        # Check if any jobs have loaded
        WebDriverWait(self.driver, AngelConstants.PauseTime.JOBS_LOADED).until(
            EC.presence_of_element_located((By.XPATH, AngelConstants.XPath.JOB_LISTING_LINK))
        )
        self._scroll_infinitely()
        elements_list = self.driver.find_elements(By.XPATH, AngelConstants.XPath.JOB_LISTING_LINK)
        for element in elements_list:
            job_link = element.get_attribute('href')
            job_title = element.get_attribute('innerText')
            job_key = extract_job_key(job_link)
            if job_key is None:
                pass
            else:
                try:
                    Job.create(
                        key=job_key,
                        website=AngelConstants.WEBSITE_NAME,
                        link=job_link,
                        title=job_title
                    )
                except peewee.IntegrityError as e:
                    print(e)

    def apply(self):
        jobs = Job\
            .select()\
            .where((Job.applied == False) & (Job.good_fit == True) & (Job.website == AngelConstants.WEBSITE_NAME))

        for count, job in enumerate(jobs):
            if count > RobotConstants.MAX_COUNT_APPLIED_JOBS:
                print('Max job apply limit reached')
                break

            self._apply_to_single_job(job)

    def _is_authenticated(self) -> bool:
        try:
            self.driver.find_element(By.XPATH, AngelConstants.XPath.LOGGED_IN)
            return True
        except common.exceptions.NoSuchElementException as e:
            return False

    @staticmethod
    def _encode_parameters(dict_parameters: dict) -> str:
        """
        Function to encode the query parameters how Angel.co likes them
        :param dict_parameters:
        :return:
        """
        dict_copy = dict_parameters.copy()
        string_parameters = json.dumps(dict_copy)
        return string_parameters.\
            replace(',','%2C').\
            replace(':','%3A').\
            replace('[','%5B').\
            replace(']','%5D')

    def _scroll_infinitely(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(AngelConstants.PauseTime.SCROLL)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


class AngelConstants(Const):
    WEBSITE_NAME = 'Angel'

    class URL(Const):
        BASE = r'https://angel.co/'
        LOGIN = r'https://angel.co/login'
        JOBS = r'https://angel.co/jobs#find/f!'

    class Id(Const):
        LOGIN_EMAIL = 'user_email'
        LOGIN_PASSWORD = 'user_password'

    class XPath(Const):
        LOGGED_IN = r"//div[string(@data-user_id)]"
        JOB_LISTING_LINK = r"//div[@class='listing-row']//div[@class='title']/a"

    class Regex(Const):
        JOB_KEY_FROM_URL = re.compile('(\d+)-')

    class PauseTime(Const):
        SCROLL = 1
        JOBS_LOADED = 7

