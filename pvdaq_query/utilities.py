# -*- coding: utf-8 -*-
import sys

def progress(count, total, status=''):
    """
    Python command line progress bar in less than 10 lines of code. · GitHub

    https://gist.github.com/vladignatyev/06860ec2040cb497f0f3

    :param count: the current count, int
    :param total: to total count, int
    :param status: a message to display
    :return:
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()