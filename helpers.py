import random
import time
from selenium import webdriver, common
import typing

"""
Point of these two classes is to allow me to make a constant object dictionary.
Acts somewhat similar to a String Enum or a object in Javascript
"""


class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError


class Const(object, metaclass=MetaConst):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError


def _parametrized(dec):
    """
     Meta-decorator, that is a decorator for decorators.
     As a decorator is a function, it actually works as a regular decorator with arguments
    SO: https://stackoverflow.com/a/26151604/5258887
    """
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl
    return layer


# TODO: Maybe add parameter for how random delta amount
@_parametrized
def sleep_after_function(func: typing.Callable, wait_time: float):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        random_wait_time = random.uniform(wait_time * .9, wait_time * 1.2)
        time.sleep(random_wait_time)
        return result

    return wrapper


@_parametrized
def sleep_before_function(func: typing.Callable, wait_time: float):
    def wrapper(*args, **kwargs):
        random_wait_time = random.uniform(wait_time * .9, wait_time * 1.2)
        time.sleep(random_wait_time)
        return func(*args, **kwargs)

    return wrapper


def does_element_exist(driver: webdriver, identifier: str, use_xpath=True) -> bool:
    """
    Function that checks if a element exists on the page
    :param driver: selenium.webdriver
    :param identifier: either a ID attribute or an xPath
    :param use_xpath:
    :return:
    """
    try:
        if use_xpath:
            driver.find_element_by_xpath(identifier)
        else:
            driver.find_element_by_id(identifier)
        return True

    except common.exceptions.NoSuchElementException:
        return False
