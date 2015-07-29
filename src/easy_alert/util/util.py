def apply_option(f, arg):
    """
    Apply function if the arg is not None
    :param f: function to apply
    :param arg: argument value
    :return: None if the arg is None, else the result of the function
    """
    return arg if arg is None else f(arg)


def with_retry(count):
    """
    Retryable function execution
    :param count: retry limit
    :return:
    """
    def f(thunk, c=count):
        while True:
            try:
                return thunk()
            except Exception as e:
                if c > 0:
                    c -= 1
                else:
                    raise e
    return f
