from Bot.Robot import Robot
from selenium.webdriver.common.by import By
from userconfig import UserConfig
import json
from selenium import webdriver, common
from Bot.constants import RobotConstants, AngelConstants

class AngelBot(Robot):
    def __init__(self, user_config: UserConfig, dry_run=False, reload_tags_blurbs=True):
        super().__init__(user_config, dry_run=dry_run, reload_tags_blurbs=reload_tags_blurbs)

    def login(self):
        self.driver.get(AngelConstants.URL.LOGIN)
        element_email = self.driver.find_element(By.ID, AngelConstants.Id.LOGIN_EMAIL)
        element_email.send_keys(self.user_config.EMAIL)
        self.driver.find_element(By.ID, AngelConstants.Id.LOGIN_PASSWORD).send_keys(self.user_config.PASSWORD)
        element_email.submit()

    def apply(self, query_parameters):
        assert self._is_authenticated()

        string_parameters = AngelBot._encode_parameters(query_parameters)
        self.driver.get(AngelConstants.URL.JOBS + string_parameters)

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
        return string_parameters.replace(',','%2C').replace(':','%3A')
