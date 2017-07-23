import time

from bs4 import BeautifulSoup
import peewee

from selenium import common
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from Bot.Robot import Robot, RobotConstants
from Bot.LinkedIn.constants import LinkedInConstant as LC
from Bot.LinkedIn.LinkedInParser import LinkedInParser
from userconfig import UserConfig
from Shared.models import Person
from Shared.selenium_helpers import scroll_infinitely, open_link_new_tab, scroll_gradually, adjust_zoom
from Shared.helpers import sleep_after_function


class LinkedInBot(Robot):
    def __init__(self, user_config: UserConfig):
        super().__init__(user_config=user_config, driver=RobotConstants.Driver.CHROME)

    def login(self):
        self.driver.get(LC.URL.LOGIN)
        element_login = self.driver.find_element(By.NAME, LC.Name.LOGIN_EMAIL)
        element_login.send_keys(self.user_config.EMAIL)

        self.driver.find_element(By.NAME, LC.Name.LOGIN_PASSWORD).send_keys(self.user_config.PASSWORD)

        element_login.submit()

        # Wait for login to finalize
        WebDriverWait(self.driver, LC.WaitTime.LOGIN).until(
            EC.presence_of_element_located((By.XPATH, LC.XPath.NEWS_FEED))
        )

    def search_people_by_query(self, query_string: str):
        full_url = LC.URL.HOST + \
                   LC.URL.SEARCH_PATH + \
                   '?' + query_string
        self.driver.get(full_url)
        WebDriverWait(self.driver, LC.WaitTime.SEARCH).until(
            EC.presence_of_element_located((By.XPATH, LC.XPath.SEARCH_RESULTS_LIST))
        )

        count_visits = 0
        while True:
            scroll_infinitely(self.driver)
            adjust_zoom(self.driver, 50)
            list_persons = LinkedInParser.parse_result_page(self.driver)

            for person in list_persons:
                try:
                    Person.get(Person.relative_link == person.relative_link)
                except peewee.DoesNotExist as e:
                    self.visit_profile(person, new_tab=True)
                    count_visits += 1

            try:
                self.driver.find_element(By.XPATH, LC.XPath.NEXT_BUTTON).send_keys(Keys.ENTER)
                adjust_zoom(self.driver, 200)
            except common.exceptions.NoSuchElementException as e:
                break

            if count_visits > LC.Constraint.MAX_VISITS:
                break

    @sleep_after_function(LC.WaitTime.VISIT)
    def visit_profile(self, p: Person, new_tab=True):
        try:
            p: Person = Person.get(Person.relative_link == p.relative_link)
        except peewee.DoesNotExist as e:
            p: Person = Person.create(
                relative_link=p.relative_link,
                full_link=p.full_link,
                name=p.name,
                title=p.title,
                position=p.position,
                company=p.company,
                location=p.location
            )

        if new_tab:
            old_tab = self.driver.window_handles[0]
            open_link_new_tab(self.driver, p.full_link)
            if len(self.driver.window_handles) > 1:
                new_tab = self.driver.window_handles[1]
                self.driver.switch_to_window(new_tab)
                time.sleep(LC.WaitTime.VIEW)
                self.driver.close()
                self.driver.switch_to_window(old_tab)

        elif p.visited is False:
            self.driver.get(p.full_link)

        p.visited = True
        LC.String.person_visited(p)
