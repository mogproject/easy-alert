import sys
from contextlib import contextmanager
from StringIO import StringIO


@contextmanager
def captured_output():
    """
    Capture and suppress stdout and stderr.

    example:
        with captured_output() as (out, err):
            (do main logic)
        (verify out.getvalue() or err.getvalue())
    :return:
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
