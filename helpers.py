import random
import time

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
def sleep_after_function(func, waitTime):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        randomWaitTime = random.uniform(waitTime * .9, waitTime * 1.2)
        time.sleep(randomWaitTime)
        return result

    return wrapper

@_parametrized
def sleep_before_function(func, waitTime, waitDelta):
    def wrapper(*args, **kwargs):
        randomWaitTime = random.uniform(waitTime * .9, waitTime * 1.2)
        time.sleep(randomWaitTime)
        return func(*args, **kwargs)

    return wrapper
