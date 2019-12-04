from math import factorial, ceil
import numpy as np


def _calc_eq(n, q):
    res = 0
    for k in range(0, ceil(n / 2)):
        res += factorial(n) / factorial(k) / factorial(n-k) * q ** (n - k) * (1 - q) ** k
    return res


def _optimize(q, a0):
    n = 1
    while _calc_eq(n, q) < a0:
        n += 1
    return n


def get_price_levels(p0, levels=[0.8, 0.99], a0=0.99):
    res = {}
    for q in levels:
        q = round(q, 2)
        n = _optimize(q, a0)
        p = round(p0 / n, 2)
        res[q] = p
    return res


def is_empty(seq):
     try:
         return all(is_empty(x) for x in seq) if not isinstance(seq, str) else False
     except TypeError:
         return False
