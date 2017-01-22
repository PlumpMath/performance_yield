"""An investigation into the cost of function calls vs. method calls vs. coroutine calls.

The current use case is a function which requires some external references, e.g.
global constants or functions, but all data that is not constant is passed as
arguments.  Thus, what state is there is constant as far as the core function is
concerned.

1) Measure the cost of invocation if no external references are used

2) Measure the cost of looking up static values in class or module scope
    Here a coroutine might excel because it can look things up once and then use
    the same local references on each run.  So we are paying only the cost of the
    context switch when invoking the coroutine, not the lookup in other namespaces.
"""
import timeit
import random


def core_function(x, y):
    """This represents the core of your program.

    This is the code that needs to be run thousands of times.
    """
    z = x * y


def frequently_called_function(p1, p2):
    """This represents the core of your program.

    This stands for the function or functions that you call thousands of times.
    """
    core_function(p1, p2)


def frequently_called_coroutine():
    """This represents the core of your program.

    This stands for the function or functions that you call thousands of times.
    In this case, we represent it as a coroutine which gets new parameters via
    yield.
    """
    # do some initialization
    pass

    while True:
        p1, p2 = (yield)
        # run your stuff
        core_function(p1, p2)

    # do some cleanup on GeneratorExit
    pass


class MyClass:
    def __init__(self):
        # do some initialization
        pass

    def frequently_called_method(self, p1, p2):
        """This represents the core of your program.

        This stands for the function or functions that you call thousands of times.
        In this case it is a method within some class.  Otherwise it is identical
        to frequently_called_function.
        """
        core_function(p1, p2)


def function_runner(n=1000):
    for i in range(n):
        x = random.random()
        y = random.randint(0,100)
        frequently_called_function(x, y)


def coroutine_runner(n=1000):
    cr = frequently_called_coroutine()
    next(cr)
    for i in range(n):
        x = random.random()
        y = random.randint(0,100)
        frequently_called_coroutine.send(x, y)


def method_runner(n=1000):
    obj = MyClass()
    for i in range(n):
        x = random.random()
        y = random.randint(0,100)
        obj.frequently_called_method(x, y)


def evaluate(measurements, msg=''):
    print("{}: best of {}: {}".format(msg, len(measurements), min(measurements)))
    return min(measurements)


if __name__ == '__main__':
    ncalls = 100000000
    rounds = 5

    t_function = timeit.Timer('__main__.function_runner({})'.format(ncalls),
                              setup='import __main__',)
    evaluate(t_function.repeat(rounds, number=1), msg="function call")

    t_coroutine = timeit.Timer('coroutine_runner({})'.format(ncalls),
                               setup='import __main__', )
    evaluate(t_function.repeat(rounds, number=1), msg="coroutine.send")

    t_method = timeit.Timer('method_runner({})'.format(ncalls),
                            setup='import __main__',)
    evaluate(t_function.repeat(rounds, number=1), msg="method call")
