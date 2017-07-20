from collections import OrderedDict
from datetime import datetime
from typing import Optional, List, Dict
import re

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.support.ui import Select

from Shared.constants import HTMLConstants as HTML
from Bot.LinkedIn.constants import LinkedInConstant as LC
from Shared.selenium_helpers import get_rendered_html, scroll_infinitely
from Shared.models import Person


class LinkedInParser(object):
    @staticmethod
    def parse_result_page(driver: webdriver.Chrome) -> List[Person]:
        rendered_html = get_rendered_html(driver)
        soup = BeautifulSoup(rendered_html, 'html.parser')
        list_results_soup = soup.find_all('div', attrs={'class': LC.Class.SEARCH_RESULT})

        list_persons = []
        for soup in list_results_soup:
            list_persons.append(LinkedInParser._parse_result(soup))

        return list_persons

    @staticmethod
    def _parse_result(soup: BeautifulSoup) -> Person:
        p = Person()
        p.name = soup.find('span', attrs={'class': LC.Class.ACTOR_NAME}).text
        p.title = soup.find('p', attrs={'class': LC.Class.ACTOR_TITLE}).text
        p.location = soup.find('p', attrs={'class': LC.Class.ACTOR_LOCATION}).text


        position_string_soup: BeautifulSoup = soup.find('p', attrs={'class': LC.Class.ACTOR_POSITION})
        if position_string_soup is not None:
            tup_position_company_list = re.findall(LC.Regex.position_string, position_string_soup.text)
            if len(tup_position_company_list) != 0:
                tup_position_company = tup_position_company_list[0]
                p.position = tup_position_company[0]
                p.company = tup_position_company[1]

        p.relative_link = soup.find('a', attrs={'class': LC.Class.ACTOR_LINK})['href']
        p.full_link = LC.URL.HOST + p.relative_link
        return p