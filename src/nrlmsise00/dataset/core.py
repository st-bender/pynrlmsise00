# Copyright (c) 2020 Stefan Bender
#
# This file is part of pynrlmsise00.
# pynrlmsise00 is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying LICENSE file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python 4-D `xarray.dataset` interface to the NRLMSISE-00 model

"""
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
	"""4-D Xarray Interface to :func:`msise_flat()`.

	4-D MSIS model atmosphere as a `xarray.Dataset` with dimensions
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
	msise_4d: `xarray.Dataset`
		The MSIS atmosphere with dimensions ("time", "alt", "lat", "lon")
		and shape (I, J, K, L) containing the data arrays:
		"He", "O", "N2", "O2", "Ar", "rho", "H", "N", "AnomO", "Texo", "Talt",
		as well as the local solar times "lst" (I,L), and the
		values used for "Ap" (I,), "f107" (I,), "f107a" (I,).

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
	dtps = dts - pd.to_timedelta("1d")

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
			t.hour + t.minute / 60. + t.second / 3600 + lon / 15.
			for t in time
		])

	msis_data = msise_flat(
		ts, alts, lats, lons,
		f107as, f107s, aps,
		lst=lst, ap_a=ap_a, flags=flags, method=method,
	)
	ret = xr.Dataset(
		{
			m[0]: (
				["time", "alt", "lat", "lon"],
				d,
				{"long_name": m[1], "units": m[2]}
			)
			for m, d in zip(MSIS_OUTPUT, np.rollaxis(msis_data, -1))
		},
		coords={"time": time, "alt": alt, "lat": lat, "lon": lon},
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
