import time


def apply_option(f, arg):
    """
    Apply function if the arg is not None
    :param f: function to apply
    :param arg: argument value
    :return: None if the arg is None, else the result of the function
    """
    return arg if arg is None else f(arg)


def with_retry(count, interval=1):
    """
    Retryable function execution
    :param count: retry limit
    :param interval: retry interval in sec
    :return:
    """

    def f(thunk, c=count, it=interval):
        while True:
            try:
                return thunk()
            except Exception as e:
                if c > 0:
                    c -= 1
                    time.sleep(it)
                else:
                    raise e

    return f
