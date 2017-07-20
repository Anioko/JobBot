import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver, common
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.webelement import FirefoxWebElement

def does_element_exist(driver: webdriver.Chrome, by_selector, identifier: str) -> bool:
    """
    Function that checks if a element exists on the page
    :param driver: selenium.webdriver
    :param by
    :param identifier: either a ID attribute or an xPath
    :return:
    """
    try:
        driver.find_element(by_selector, identifier)
        return True

    except common.exceptions.NoSuchElementException:
        return False


def get_rendered_html(driver: webdriver.Chrome) -> str:
    rendered_html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    return rendered_html


def scroll_infinitely(driver: webdriver.Chrome, pause_time_seconds:float = 0.5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time_seconds)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scroll_gradually(driver: webdriver.Chrome, pause_time_seconds=0.5, scroll_amount=200):
    prev_height = driver.execute_script("return window.pageYOffset")
    while True:
        driver.execute_script("window.scrollTo(0, {0});".format(prev_height + scroll_amount))
        time.sleep(pause_time_seconds)
        cur_height = driver.execute_script("return window.pageYOffset")
        if prev_height == cur_height:
            break
        prev_height = cur_height

def adjust_zoom(driver: webdriver.Chrome, zoom_percentage: float):
    zoom_string = "document.body.style.zoom='{0}%'".format(zoom_percentage)
    driver.execute_script(zoom_string)


def open_in_new_tab(driver: webdriver.Chrome, by: By, identifier: str, ) -> bool:
    try:
        element_to_click = driver.find_element(by, identifier)
        ActionChains(driver).key_down(Keys.CONTROL).click(element_to_click).key_up(Keys.CONTROL).perform()
        return True
    except common.exceptions.NoSuchElementException:
        return False

def open_link_new_tab(driver: webdriver.Chrome, link:str):
    driver.execute_script("$(window.open('{0}'))".format(link))