# -*- coding: utf-8 -*-
# Copyright (c) 2020 Stefan Bender
#
# This file is part of pynrlmsise00.
# pynrlmsise00 is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying LICENSE file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python 4-D `xarray.dataset` interface to the NRLMSISE-00 model

"""
from collections import OrderedDict

import numpy as np
import pandas as pd
import xarray as xr

from spaceweather import sw_daily

from ..core import msise_flat

__all__ = ["msise_4d"]

MSIS_OUTPUT = [
	# name, long name, units
	# number densities
	("He", "He number density", "cm^-3"),
	("O", "O number density", "cm^-3"),
	("N2", "N2 number density", "cm^-3"),
	("O2", "O2 number density", "cm^-3"),
	("Ar", "AR number density", "cm^-3"),
	("rho", "total mass density", "g cm^-3"),  # includes d[8] in gtd7d
	("H", "H number density", "cm^-3"),
	("N", "N number density", "cm^-3"),
	("AnomO", "Anomalous oxygen number density", "cm^-3"),
	# temperature
	("Texo", "Exospheric temperature", "K"),
	("Talt", "Temperature at alt", "K"),
]

SW_INDICES = [
	# name, long name, units
	("Ap", "Daily Ap index", "nT"),
	(
		"f107",
		"Observed solar f10.7 cm radio flux of the previous day",
		"sfu, 10^-22 W m^-2 Hz^-1"
	),
	(
		"f107a",
		"Observed 81-day running average of the solar f10.7 cm radio flux centred on day",
		"sfu, 10^-22 W m^-2 Hz^-1"
	),
]


# helper functions
def _check_nd(a, ndim=1):
	a = np.atleast_1d(a)
	if a.ndim > ndim:
		raise ValueError(
			"Only scalars and up to {ndim}-D arrays are currently supported, "
			"got {a.ndim} dimensional array.".format(ndim=ndim, a=a)
		)
	return a


def _check_gm(gm, dts, df=None):
	"""Check that GM indices have the correct shape

	Returns the GM index broadcasted to shape (`dts`,).
	"""
	def _dfloc(t, df=None):
		return df.loc[t.floor("D")]

	if gm is None and df is not None:
		# select arbitrary shapes from pandas dataframes
		return np.vectorize(_dfloc, excluded=["df"])(dts, df=df)
	gm = np.atleast_1d(gm)
	if gm.ndim > 1:
		raise ValueError(
			"GM coefficients must be either scalars or one-dimensional arrays, "
			"other shapes are currently not supported."
		)
	if gm.shape != dts.shape:
		gm = np.broadcast_to(gm, dts.shape)
	return gm


def _check_lst(lst, time, lon):
	"""Check that LST has the correct shape

	Returns the LST broadcasted to shape (`time`, `lon`).
	"""
	lst = np.atleast_1d(lst)
	if lst.ndim > 2:
		raise ValueError("Only up to 2-D arrays are supported for LST.")
	if lst.ndim == 2:
		if (
			lst.shape[0] in [1, lon.size]
			and lst.shape[1] in [1, time.size]
		):
			# got shape (lon, time), (1, time), (lon, 1) or (1, 1)
			lst = lst.T
		else:
			# require shape (time, lon), (1, lon), (time, 1), or (1, 1)
			assert (
				lst.shape[0] in [1, time.size]
				and lst.shape[1] in [1, lon.size]
			)
	elif lst.ndim == 1:
		if lst.size == lon.size:
			# longitude takes precedence
			lst = lst[None, :]
		else:
			assert lst.size in [1, time.size]
			lst = lst[:, None]
	lsts = np.broadcast_to(lst, (time.size, lon.size))
	return lsts


def msise_4d(
	time, alt, lat, lon,
	f107a=None, f107=None, ap=None,
	lst=None,
	ap_a=None, flags=None,
	method="gtd7",
):
	u"""4-D Xarray Interface to :func:`msise_flat()`.

	4-D MSIS model atmosphere as a :class:`xarray.Dataset` with dimensions
	(time, alt, lat, lon). Only scalars and 1-D arrays for `time`, `alt`,
	`lat`, and `lon` are supported.

	The geomagnetic and Solar flux indices can be acquired using the
	`spaceweather` package (when set to `None`, the default).
	They can also be supplied explicitly as scalars or 1-D arrays with
	the same shape as `time`.

	The local solar time (LST) will usually be calculated from `time` and `lon`,
	but can be set explicitly using a fixed scalar LST, a 1-D array matching
	the shape of either `time` or `lon`, or a 2-D array matching the shape
	of (`time`, `lon`).

	Parameters
	----------
	time: float or 1-d array_like (I,)
		Time as `datetime.datetime`s.
	alt: float or 1-d array_like (J,)
		Altitudes in [km].
	lat: float or 1-d array_like (K,)
		Latitudes in [°N].
	lon: float or 1-d array_like (L,)
		Longitudes in [°E]
	f107a: float or 1-d array_like (I,), optional
		The 81-day running average Solar 10.7cm radio flux,
		centred at the day(s) of `time`.
		Set to `None` (default) to use the `spaceweather` package.
	f107: float or 1-d array_like (I,), optional
		The Solar 10.7cm radio flux at the previous day(s) of `time`.
		Set to `None` (default) to use the `spaceweather` package.
	ap: float or 1-d array_like (I,), optional
		The daily geomagnetic Ap index at the day(s) of `time`.
		Set to `None` (default) to use the `spaceweather` package.
	lst: float, 1-d (I,) or (L,) or 2-d array_like (I,L), optional
		The local solar time at `time` and `lon`, to override the
		calculated values.
		Default: `None` (calculate from `time` and `lon`)
	ap_a: list of int (7,), optional
		List of Ap indices, passed to `msise_flat()`,
		broadcasting is currently not supported.
	flags: list of int (23,), optional
		List of flags, passed to `msise_flat()`,
		broadcasting is currently not supported.
	method: str, optional, default "gtd7"
		Select MSISE-00 method, changes the output of "rho",
		the atmospheric mass density.

	Returns
	-------
	msise_4d: :class:`xarray.Dataset`
		The MSIS atmosphere with dimensions ("time", "alt", "lat", "lon")
		and shape (I, J, K, L) containing the data arrays:
		"He", "O", "N2", "O2", "Ar", "rho", "H", "N", "AnomO", "Texo", "Talt",
		as well as the local solar times "lst" (I,L), and the
		values used for "Ap" (I,), "f107" (I,), "f107a" (I,).

	Example
	-------
	Using "internal" setting of the geomagnetic and Solar indices
	and automatic conversion to 4-D looks like this
	("time" can be an array of :class:`datetime.datetime` as well):

	>>> from datetime import datetime
	>>> from nrlmsise00.dataset import msise_4d
	>>> alts = np.arange(200, 401, 100.)  # = [200, 300, 400] [km]
	>>> lats = np.arange(60, 71, 10.)  # = [60, 70] [°N]
	>>> lons = np.arange(-70., 71., 35.)  # = [-70, -35,  0, 35, 70] [°E]
	>>> # broadcasting is done internally
	>>> ds = msise_4d(datetime(2009, 6, 21, 8, 3, 20), alts, lats, lons)
	>>> ds
	<xarray.Dataset>
	Dimensions:  (alt: 3, lat: 2, lon: 5, time: 1)
	Coordinates:
	  * time     (time) datetime64[ns] 2009-06-21T08:03:20
	  * alt      (alt) float64 200.0 300.0 400.0
	  * lat      (lat) float64 60.0 70.0
	  * lon      (lon) float64 -70.0 -35.0 0.0 35.0 70.0
	Data variables:
	    He       (time, alt, lat, lon) float64 8.597e+05 1.063e+06 ... 4.936e+05
	    O        (time, alt, lat, lon) float64 1.248e+09 1.46e+09 ... 2.635e+07
	    N2       (time, alt, lat, lon) float64 2.555e+09 2.654e+09 ... 1.667e+06
	    O2       (time, alt, lat, lon) float64 2.1e+08 2.062e+08 ... 3.471e+04
	    Ar       (time, alt, lat, lon) float64 3.16e+06 3.287e+06 ... 76.55 67.16
	    rho      (time, alt, lat, lon) float64 1.635e-13 1.736e-13 ... 7.984e-16
	    H        (time, alt, lat, lon) float64 3.144e+05 3.02e+05 ... 1.237e+05
	    N        (time, alt, lat, lon) float64 9.095e+06 1.069e+07 ... 6.765e+05
	    AnomO    (time, alt, lat, lon) float64 1.173e-08 1.173e-08 ... 1.101e+04
	    Texo     (time, alt, lat, lon) float64 805.2 823.7 807.1 ... 818.7 821.2
	    Talt     (time, alt, lat, lon) float64 757.9 758.7 766.4 ... 818.7 821.1
	    lst      (time, lon) float64 3.389 5.722 8.056 10.39 12.72
	    Ap       (time) int32 6
	    f107     (time) float64 66.7
	    f107a    (time) float64 69.0

	See also
	--------
	msise_flat
	"""

	time = _check_nd(time)
	alt = _check_nd(alt)
	lat = _check_nd(lat)
	lon = _check_nd(lon)

	sw = sw_daily()
	# convert arbitrary shapes
	dts = np.vectorize(pd.to_datetime)(time, utc=True)
	dtps = np.array([dt - pd.to_timedelta("1d") for dt in dts])

	ap = _check_gm(ap, dts, df=sw[["Apavg"]])
	f107 = _check_gm(f107, dtps, df=sw[["f107_obs"]])
	f107a = _check_gm(f107a, dts, df=sw[["f107_81ctr_obs"]])

	# expand dimensions to 4d
	ts = time[:, None, None, None]
	alts = alt[None, :, None, None]
	lats = lat[None, None, :, None]
	lons = lon[None, None, None, :]

	aps = ap[:, None, None, None]
	f107s = f107[:, None, None, None]
	f107as = f107a[:, None, None, None]

	if lst is not None:
		lsts = _check_lst(lst, time, lon)
		lst = lsts[:, None, None, :]
	else:
		lsts = np.array([
			t.hour + t.minute / 60. + t.second / 3600. + lon / 15.
			for t in time
		])

	msis_data = msise_flat(
		ts, alts, lats, lons,
		f107as, f107s, aps,
		lst=lst, ap_a=ap_a, flags=flags, method=method,
	)
	ret = xr.Dataset(
		OrderedDict([(
			m[0], (
				["time", "alt", "lat", "lon"],
				d,
				{"long_name": m[1], "units": m[2]}
			))
			for m, d in zip(MSIS_OUTPUT, np.rollaxis(msis_data, -1))
		]),
		coords=OrderedDict([
			("time", list(map(np.datetime64, time))),
			("alt", alt), ("lat", lat), ("lon", lon),
		]),
	)
	ret["lst"] = (
		["time", "lon"], lsts, {"long_name": "Mean Local Solar Time", "units": "h"}
	)
	ret["Ap"] = (["time"], ap)
	ret["f107"] = (["time"], f107)
	ret["f107a"] = (["time"], f107a)
	for _sw in SW_INDICES:
		ret[_sw[0]].attrs.update({"long_name": _sw[1], "units": _sw[2]})
	return ret
