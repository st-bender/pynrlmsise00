# Copyright (c) 2019 Stefan Bender
#
# This module is part of pynrlmsise00.
# pynrlmsise00 is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying LICENSE file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python interface based on the NRLMSISE-00 C version [0]_

.. [0] https://www.brodo.de/space/nrlmsise
"""
__version__ = "0.1.0"

from . import _nrlmsise00
from .core import *

__all__ = ["msise_model", "msise_flat", "gtd7_flat", "gtd7d_flat"]
