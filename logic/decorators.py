from functools import lru_cache, wraps
from datetime import datetime, timedelta
import time


def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)
        return wrapped_func
    return wrapper_cache


def logger(function):
    """
    регистрируя время её запуска и окончания выполнения.
    :param function:
    :return:
    """
    def wrapper(*args, **kwargs):
        print(f"----- {function.__name__}: start -----")
        output = function(*args, **kwargs)
        print(f"----- {function.__name__}: end -----")
        return output
    return wrapper


def repeat(number_of_times):
    """
    Этот декоратор запускает вызов функции несколько раз подряд.
    Это может быть полезно для целей отладки, стресс-тестирования или
    автоматизации повторения нескольких задач.
    :param number_of_times:
    :return:
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(number_of_times):
                func(*args, **kwargs)
        return wrapper
    return decorate


def timeit(func):
    """
    Этот декоратор измеряет время выполнения функции и выводит результат:
     он служит для отладки или мониторинга
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'{func.__name__} took {end - start:.6f} seconds to complete')
        return result
    return wrapper


def countcall(func):
    """
    Этот декоратор подсчитывает, сколько раз была вызвана функция.
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        result = func(*args, **kwargs)
        print(f'{func.__name__} has been called {wrapper.count} times')
        return result
    wrapper.count = 0
    return wrapper
