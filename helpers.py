import random
import time

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
def sleepAfterFunction(func, waitTime):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        randomWaitTime = random.uniform(waitTime * .9, waitTime * 1.2)
        time.sleep(randomWaitTime)
        return result

    return wrapper

@_parametrized
def sleepBeforeFunction(func, waitTime, waitDelta):
    def wrapper(*args, **kwargs):
        randomWaitTime = random.uniform(waitTime * .9, waitTime * 1.2)
        time.sleep(randomWaitTime)
        return func(*args, **kwargs)

    return wrapper