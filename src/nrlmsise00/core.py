# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
#
# Copyright (c) 2019 Stefan Bender
#
# This file is part of pynrlmsise00.
# pynrlmsise00 is free software: you can redistribute it or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
# See accompanying LICENSE file or http://www.gnu.org/licenses/gpl-2.0.html.
"""NRLMSISE-00 python wrapper for the C version [#]_

.. [#] https://www.brodo.de/space/nrlmsise
"""
from __future__ import absolute_import, division, print_function

from functools import wraps

import numpy as np

from ._nrlmsise00 import gtd7, gtd7d

__all__ = ["gtd7_flat", "gtd7d_flat", "msise_model", "msise_flat", "scale_height"]


def _doc_param(*sub):
	def dec(obj):
		obj.__doc__ = obj.__doc__.format(*sub)
		return obj
	return dec


def vectorize_function(pyfunc, **kwargs):
	"""Function decorator acting like :class:`numpy.vectorize`.

	All arguments are passed to :class:`numpy.vectorize`. Unlike
	:class:`numpy.vectorize`, this decorator does not convert the decorated
	function into an instance of the :class:`numpy.vectorize` class. As a
	result, the decorated function's docstring will be taken into account
	properly by doc generators (pydoc or Sphinx)
	"""
	wrapped = np.vectorize(pyfunc, **kwargs)
	@wraps(pyfunc)
	def run_wrapped(*args, **kwargs):
		return wrapped(*args, **kwargs)
	run_wrapped.__doc__ = wrapped.__doc__  # preserve np.vectorize's `doc` arg
	return run_wrapped


@_doc_param(gtd7.__doc__)
def _gtd7_flat(*args, **kwargs):
	"""Flattened variant of the MSIS `gtd7()` function

	Returns a single 11-element :class:`numpy.ndarray` instead of
	the two lists. All arguments except the keywords `flags` and
	`ap_a` can be :class:`numpy.ndarray` to facilitate calculations
	at many locations/times.

	{0}
	"""
	ds, ts = gtd7(*args, **kwargs)
	return np.asarray(ds + ts)


@_doc_param(gtd7d.__doc__)
def _gtd7d_flat(*args, **kwargs):
	"""Flattened variant of the MSIS `gtd7d()` function

	Returns a single 11-element :class:`numpy.ndarray` instead of
	the two lists. All arguments except the keywords `flags` and
	`ap_a` can be :class:`numpy.ndarray` to facilitate calculations
	at many locations/times.

	{0}
	"""
	ds, ts = gtd7d(*args, **kwargs)
	return np.asarray(ds + ts)


gtd7_flat = vectorize_function(_gtd7_flat,
		signature='(),(),(),(),(),(),(),(),(),()->(n)',
		excluded=["ap_a", "flags"])

gtd7d_flat = vectorize_function(_gtd7d_flat,
		signature='(),(),(),(),(),(),(),(),(),()->(n)',
		excluded=["ap_a", "flags"])


def msise_model(time, alt, lat, lon, f107a, f107, ap,
		lst=None, ap_a=None, flags=None, method="gtd7"):
	"""Interface to `gtd7()` [1]_ and `gtd7d()` [2]_

	Calls the C model function using a :class:`datetime.datetime`
	instance to calculate the day of year, seconds and so on.
	The `method` keyword decides which version to call, the difference
	being that `gtd7d()` includes anomalous oxygen in the total
	mass density (`d[5]`), `gtd7()` does not.

	.. [1] https://git.linta.de/?p=~brodo/nrlmsise-00.git;a=blob;f=nrlmsise-00.c#l916
	.. [2] https://git.linta.de/?p=~brodo/nrlmsise-00.git;a=blob;f=nrlmsise-00.c#l1044

	Parameters
	----------
	time: datetime.datetime
		Date and time as a `datetime.dateime`.
	alt: float
		Altitude in km.
	lat: float
		Latitude in degrees north.
	lon: float
		Longitude in degrees east.
	f107a: float
		The observed f107a (81-day running mean of f107) centred at date.
	f107: float
		The observed f107 value on the previous day.
	ap: float
		The ap value at date.
	lst: float, optional
		The local solar time, can be different from the calculated one.
	ap_a: list, optional
		List of length 7 containing ap values to be used when flags[9] is set
		to -1, otherwise no effect.
	flags: list, optional
		List of length 24 setting the NRLMSIS switches explicitly.
	method: string, optional
		Set to "gtd7d" to use `gtd7d()` (which includes anomalous oxygen
		in the total mass density) instead of the "standard" `gtd7()` function
		without it.

	Returns
	-------
	densities: list of floats
		0. He number density [cm^-3]
		1. O number density [cm^-3]
		2. N2 number density [cm^-3]
		3. O2 number density [cm^-3]
		4. AR number density [cm^-3]
		5. total mass density [g cm^-3] (includes d[8] in gtd7d)
		6. H number density [cm^-3]
		7. N number density [cm^-3]
		8. Anomalous oxygen number density [cm^-3]
	temperatures: list of floats
		0. Exospheric temperature [K]
		1. Temperature at `alt` [K]

	Note
	----
	No date and time conversion will be attempted, the input needs to be
	converted before, `dateutil` or `pandas` provide convenient functions.
	For example to convert :class:`pandas.DatetimeIndex`
	use ``<index>.to_pydatetime()``,
	for :class:`astropy.time.Time` use ``<Time>.to_datetime()``.

	The local solar time is calculated from time and longitude, except when
	`lst` is set, then that value is used.

	The solar and geomagnetic indices have to be provided, so far the values
	are not included in the module.
	"""
	year = time.year
	doy = int(time.strftime("%j"))
	sec = (time.hour * 3600.
			+ time.minute * 60.
			+ time.second
			+ time.microsecond * 1e-6)
	if lst is None:
		lst = sec / 3600. + lon / 15.0

	kwargs = {}
	if ap_a is not None:
		kwargs.update({"ap_a": ap_a})
	if flags is not None:
		kwargs.update({"flags": flags})

	if method == "gtd7d":
		return gtd7d(year, doy, sec, alt, lat, lon, lst, f107a, f107, ap, **kwargs)
	return gtd7(year, doy, sec, alt, lat, lon, lst, f107a, f107, ap, **kwargs)


def _msise_flat(*args, **kwargs):
	ds, ts = msise_model(*args, **kwargs)
	return np.asarray(ds + ts)


_msise_flatv = np.vectorize(_msise_flat,
		signature='(),(),(),(),(),(),(),(),(),()->(n)',
		excluded=["method"])


@_doc_param(msise_model.__doc__.replace("Interface", "interface"))
def msise_flat(*args, **kwargs):
	"""Flattened {0}
	Attention
	---------
	This flattened version returns a single 11-element array instead of two
	separate lists. Additionally, it can take :class:`numpy.ndarray` as input.
	However, the `time` input needs to contain entries of :class:`datetime.datetime`,
	e.g. using :meth:`pandas.DatetimeIndex.to_pydatetime()`
	or :meth:`astropy.time.Time.to_datetime()`.
	"""
	# Set keyword arguments to None if not given to make `np.vectorize` happy
	lst = kwargs.pop("lst", None)
	ap_a = kwargs.pop("ap_a", None)
	flags = kwargs.pop("flags", None)

	return _msise_flatv(*args, lst=lst, ap_a=ap_a, flags=flags, **kwargs)


def scale_height(alt, lat, molw, temp):
	"""Atmospheric scale height

	Extracted from the C-code for easy access, with
	constants updated to the standard SI values.
	It is reasonably fast and :mod:`numpy`-broadcasting compatible.

	Parameters
	----------
	alt: float or array_like
		Altitude in [km].
	lat: float or array_like
		Geodetic latitude in [degrees N].
	molw: float or array_like
		Molecular mass at alt in [kg / mol].
		Can be derived by dividing the total mass density by
		the sum of number densities, e.g. from :func:`gtd7()`,
		multiplied by Avogadro's constant (6.0221407e23 / mol).
	temp: float or array_like
		Temperature at alt in [K].

	Returns
	-------
	scale_height: float or array_like
		Scale height in [m].
	"""
	# Rgas = 8.31446261815324  # J / K / mol
	# dgtr = 1.7453292519943295e-2  # rad / deg
	c2 = np.cos(2. * 1.7453292519943295e-2 * lat)
	gsurf = 9.80665 * (1.0 - 0.0026373 * c2)  # m / s2
	# re in [km]
	re = 2. * gsurf / (3.085462e-6 + 2.27e-9 * c2) * 1.0e-3
	g = gsurf / (1 + alt / re)**2
	return 8.31446261815324 * temp / (g * molw)
