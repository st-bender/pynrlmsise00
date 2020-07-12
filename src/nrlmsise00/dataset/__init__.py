# Copyright (c) 2019 Stefan Bender
#
# This module is part of pynrlmsise00.
# pynrlmsise00 is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying LICENSE file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python 4-D `xarray.dataset` interface to the NRLMSISE-00 model

"""
from warnings import warn

try:
	from .core import *
except ImportError as e:
	msg = (
		"nrlmsise00 dataset requirements not installed.\n"
		"Please install them using:\n"
		"  pip intsall 'nrlmsise00[dataset]'  # for xarray.Dataset support\n"
		"or:\n"
		"  pip intsall 'nrlmsise00[all]'      # for all optional modules"
	)
	raise ImportError(msg)

__all__ = ["msise_4d"]

warn("The xarray 4d interface is experimental.", UserWarning)
