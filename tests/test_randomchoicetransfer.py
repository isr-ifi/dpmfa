# -*- coding: utf-8 -*-
"""Module tests."""
from dpmfa.components import Compartment
from dpmfa.components import RandomChoiceTransfer

from numpy import ndarray

import pytest


def test_randomchoicetransfers_typechecking():
    """Test that with typechecking enabled exceptions are thrown."""
    c = Compartment("Compartment 1", None, None)
    a = ndarray(shape=(2, 2))
    with pytest.raises(TypeError):
        RandomChoiceTransfer("", c, priority=1)
    with pytest.raises(TypeError):
        RandomChoiceTransfer([], None, priority=1)
    with pytest.raises(TypeError):
        RandomChoiceTransfer(a, None, priority=1)
    with pytest.raises(TypeError):
        RandomChoiceTransfer([], c, priority="string")

    RandomChoiceTransfer([], c, priority=1)
