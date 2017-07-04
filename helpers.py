import time
'''
 Meta-decorator, that is a decorator for decorators. 
 As a decorator is a function, it actually works as a regular decorator with arguments
SO: https://stackoverflow.com/a/26151604/5258887
'''
def _parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl
    return layer

@_parametrized
def sleepAfterFunction(func, waitTime):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        time.sleep(waitTime)
        return result

    return wrapper

@_parametrized
def sleepBeforeFunction(func, waitTime):
    def wrapper(*args, **kwargs):
        time.sleep(waitTime)
        return func(*args, **kwargs)

    return wrapper