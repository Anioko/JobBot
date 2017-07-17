import random
import time
from typing import Callable, List
import nltk

from selenium.webdriver.common.by import By
from selenium import webdriver, common


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
def sleep_after_function(func: Callable, wait_time: float):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        random_wait_time = random.uniform(wait_time * .9, wait_time * 1.2)
        time.sleep(random_wait_time)
        return result

    return wrapper


@_parametrized
def sleep_before_function(func: Callable, wait_time: float):
    def wrapper(*args, **kwargs):
        random_wait_time = random.uniform(wait_time * .9, wait_time * 1.2)
        time.sleep(random_wait_time)
        return func(*args, **kwargs)

    return wrapper


def does_element_exist(driver: webdriver, by_selector, identifier: str) -> bool:
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


def any_in(a: list, b: list) -> bool:
    return any(i in b for i in a)

def tokenize_text(text:str) -> List[str]:
    tokens = nltk.word_tokenize(text)
    tokens = set([word.lower() for word in tokens if word.isalpha()])
    tokens = [word for word in tokens if word not in nltk.corpus.stopwords.words('english')]
    return tokens