# -*- coding: utf-8 -*-
"""Module tests."""
from dpmfa.components import Compartment
from dpmfa.components import ConstTransfer

import pytest


def test_compartments_typechecking():
    """Test that with typechecking enabled exceptions are thrown."""
    c = Compartment("Compartment 1", None, None)
    with pytest.raises(TypeError):
        ConstTransfer("1.0", c)
    with pytest.raises(TypeError):
        ConstTransfer(1.0, 0)
    ConstTransfer(1.0, c)
