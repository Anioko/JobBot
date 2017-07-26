import random
import time
from typing import Callable, List

import nltk

from Shared.constants import HTMLConstants
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


def any_in(a: list, b: list) -> bool:
    return any(i in b for i in a)


def tokenize_text(text:str) -> List[str]:
    text = text.replace('/',' ')  # Pre-processing
    tokens = nltk.word_tokenize(text)
    tokens = set([word.lower() for word in tokens if word.isalpha()])
    tokens = [word for word in tokens if word not in nltk.corpus.stopwords.words('english')]
    return tokens


def set_similarity(a: set, b: set) -> float:
    count_intersection = len(a.intersection(b))
    count_difference = len(a.difference(b))
    return count_intersection / (count_intersection + count_difference)


def has_single_answer(input_type: str) -> bool:
    """
    Helper to determine whether the input has a single selectable answer
    :param input_type:
    :return:
    """
    if input_type == HTMLConstants.InputTypes.TEXT or \
                    input_type == HTMLConstants.InputTypes.FILE or \
                    input_type == HTMLConstants.InputTypes.EMAIL or \
                    input_type == HTMLConstants.InputTypes.PHONE:
        return True
    else:
        return False
