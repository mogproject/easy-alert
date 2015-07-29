import re
from case_class import CaseClass


class Matcher(CaseClass):
    def __init__(self, s):
        super(Matcher, self).__init__(['operator', 'threshold'])

        m = re.match("""([=!<>]+)\s*(\d+)""", s)
        if m is None:
            raise Exception('Invalid matcher string: %s' % s)

        op, tt = m.groups()
        t = int(tt)

        if op == '==':
            op = '='
        f = {
            '=': lambda x: x == int(t),
            '!=': lambda x: x != int(t),
            '<': lambda x: x < int(t),
            '<=': lambda x: x <= int(t),
            '>': lambda x: x > int(t),
            '>=': lambda x: x >= int(t),
        }.get(op)

        if f is None:
            raise Exception('Invalid matcher string: %s' % s)
        self.operator = op
        self.threshold = t
        self.check = f

    def __str__(self):
        return '"%s %d"' % (self.operator, self.threshold)
