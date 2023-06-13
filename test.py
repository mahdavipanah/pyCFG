#!/usr/bin/env python3

import pytest

from itertools import product
from cfg import CFG


def test_old_behavior():
    g = CFG({'S'}, {'a', 'b', 'c', 'λ'}, {('S', 'aSa'),
                                          ('S', 'bSb'),
                                          ('S', 'cSc'),
                                          ('S', 'λ')}, 'S', 'λ')

    observed = {x for x in map(''.join, product(*['abc'] * 4)) if g.cyk(x)}
    expected = {'aaaa', 'abba', 'acca', 'baab', 'bbbb', 'bccb', 'caac', 'cbbc', 'cccc'}

    assert observed == expected
