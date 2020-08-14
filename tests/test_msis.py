# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import os

import datetime as dt
import numpy as np
import pytest

import nrlmsise00 as msise

# standard inputs for direct interface
STD_INPUT_C = [
		0,      # year /* without effect */
		172,    # doy
		29000,  # sec
		400,    # alt
		60,     # g_lat
		-70,    # g_long
		16,     # lst
		150,    # f107A
		150,    # f107
		4,      # ap
]

# standard inputs for python functions
STD_INPUT_PY = [
		dt.datetime(2009, 6, 21, 8, 3, 20),
		400,    # alt
		60,     # g_lat
		-70,    # g_long
		150,    # f107A
		150,    # f107
		4,      # ap
]
STD_KW_PY = {"lst": 16}


def test_structure():
	assert msise
	assert msise._nrlmsise00
	assert msise._nrlmsise00.gtd7
	assert msise._nrlmsise00.gtd7d
	assert msise.msise_model
	assert msise.msise_flat


def test_c_gtd7():
	# high ap values
	aph = [100.] * 7
	# standard flags
	flags = [0] + [1] * 23
	# copy the list contents, otherwise they would all point to the
	# same list which would get overwritten every time a value changes
	inputs = [STD_INPUT_C[:] for _ in range(17)]
	# update input lists with values to test
	inputs[1][1] = 81  # doy
	inputs[2][2] = 75000  # sec
	inputs[2][3] = 1000  # alt
	inputs[3][3] = 100  # alt
	inputs[10][3] = 0  # alt
	inputs[11][3] = 10  # alt
	inputs[12][3] = 30  # alt
	inputs[13][3] = 50  # alt
	inputs[14][3] = 70  # alt
	inputs[16][3] = 100  # alt
	inputs[4][4] = 0  # g_lat
	inputs[5][5] = 0  # g_long
	inputs[6][6] = 4  # lst
	inputs[7][7] = 70  # f107A
	inputs[8][8] = 180  # f107
	inputs[9][9] = 40  # ap
	# MSIS test outputs from the documentation
	test_file = os.path.join(
			os.path.realpath(os.path.dirname(__file__)),
			"msis_testoutput.txt")
	test_output = np.genfromtxt(test_file)

	outputs = []
	for inp in inputs[:15]:
		ds, ts = msise._nrlmsise00.gtd7(*inp, flags=flags)
		outputs.append(ds + ts)
	flags[9] = -1
	for inp in inputs[15:17]:
		ds, ts = msise._nrlmsise00.gtd7(*inp, ap_a=aph, flags=flags)
		outputs.append(ds + ts)
	# Compare results
	np.testing.assert_allclose(np.asarray(outputs), test_output, rtol=1e-6)


def test_py_msise():
	# high ap values
	aph = [100.] * 7
	# standard flags
	flags = [0] + [1] * 23
	kws = [STD_KW_PY.copy() for _ in range(17)]
	# copy the list contents, otherwise they would all point to the
	# same list which would get overwritten every time a value changes
	inputs = [STD_INPUT_PY[:] for _ in range(17)]
	# update input lists with values to test
	inputs[1][0] = dt.datetime(2009, 3, 22, 8, 3, 20)
	inputs[2][0] = dt.datetime(2009, 6, 21, 20, 50, 0)
	inputs[2][1] = 1000  # alt
	inputs[3][1] = 100  # alt
	inputs[10][1] = 0  # alt
	inputs[11][1] = 10  # alt
	inputs[12][1] = 30  # alt
	inputs[13][1] = 50  # alt
	inputs[14][1] = 70  # alt
	inputs[16][1] = 100  # alt
	inputs[4][2] = 0  # g_lat
	inputs[5][3] = 0  # g_long
	inputs[7][4] = 70  # f107A
	inputs[8][5] = 180  # f107
	inputs[9][6] = 40  # ap
	kws[6].update({"lst": 4})  # lst
	# MSIS test outputs from the documentation
	test_file = os.path.join(
			os.path.realpath(os.path.dirname(__file__)),
			"msis_testoutput.txt")
	test_output = np.genfromtxt(test_file)

	outputs = []
	for inp, kw in zip(inputs[:15], kws[:15]):
		ds, ts = msise.msise_model(*inp, flags=flags, **kw)
		outputs.append(ds + ts)
	flags[9] = -1
	for inp, kw in zip(inputs[15:17], kws[15:17]):
		ds, ts = msise.msise_model(*inp, ap_a=aph, flags=flags, **kw)
		outputs.append(ds + ts)
	# Compare results
	np.testing.assert_allclose(np.asarray(outputs), test_output, rtol=1e-6)


def test_py_msise_flat():
	# high ap values
	aph = [100.] * 7
	# set up empty arrays for the aps and flags
	aphs = np.empty((17,), dtype=object)
	flags = np.empty((17,), dtype=object)
	# standard flags
	for i in range(17):
		flags[i] = [0] + [1] * 23
	# set the standard values 17 times
	times = [dt.datetime(2009, 6, 21, 8, 3, 20)] * 17
	alts = [400] * 17   # alt
	lats = [60] * 17    # g_lat
	lons = [-70] * 17   # g_long
	f107a = [150] * 17  # f107A
	f107 = [150] * 17   # f107
	ap = [4] * 17       # ap
	lsts = [16] * 17
	# update for individual tests
	times[1] = dt.datetime(2009, 3, 22, 8, 3, 20)
	times[2] = dt.datetime(2009, 6, 21, 20, 50, 0)
	alts[2] = 1000  # alt
	alts[3] = 100  # alt
	alts[10] = 0  # alt
	alts[11] = 10  # alt
	alts[12] = 30  # alt
	alts[13] = 50  # alt
	alts[14] = 70  # alt
	alts[16] = 100  # alt
	lats[4] = 0  # g_lat
	lons[5] = 0  # g_long
	f107a[7] = 70  # f107A
	f107[8] = 180  # f107
	ap[9] = 40  # ap
	lsts[6] = 4
	# include ap array for the last two tests
	flags[15][9] = -1
	flags[16][9] = -1
	aphs[15] = aph
	aphs[16] = aph
	# MSIS test outputs from the documentation
	test_file = os.path.join(
			os.path.realpath(os.path.dirname(__file__)),
			"msis_testoutput.txt")
	test_output = np.genfromtxt(test_file)
	output = msise.msise_flat(times, alts, lats, lons,
			f107a, f107, ap, lst=lsts, ap_a=aphs, flags=flags)
	# Compare results
	np.testing.assert_allclose(output, test_output, rtol=1e-6)
	# single call only, default ap and flags
	output0 = msise.msise_flat(times[0], alts[0], lats[0], lons[0],
			f107a[0], f107[0], ap[0], lst=lsts[0])
	np.testing.assert_allclose(output0, test_output[0], rtol=1e-6)
	# special flags and ap setting in a single call
	aps0 = np.empty((1,), dtype=object)
	flags0 = np.empty((1,), dtype=object)
	aps0[0] = aphs[16]
	flags0[0] = flags[16]
	output0 = msise.msise_flat(times[16], alts[16], lats[16], lons[16],
			f107a[16], f107[16], ap[16], lst=lsts[16], ap_a=aps0, flags=flags0)
	np.testing.assert_allclose(output0[0], test_output[16], rtol=1e-6)


def test_c_invalid_length():
	# C interface
	with pytest.raises(ValueError):
		ds, ts = msise._nrlmsise00.gtd7(*STD_INPUT_C, ap_a=[0., 1., 2., 3.])
	with pytest.raises(ValueError):
		ds, ts = msise._nrlmsise00.gtd7(*STD_INPUT_C, flags=[0, 1, 2, 3])


def test_c_invalid_types():
	# C interface
	with pytest.raises(ValueError):
		ds, ts = msise._nrlmsise00.gtd7(*STD_INPUT_C, ap_a=list(range(6)) + ["6"])
	# C interface
	with pytest.raises(ValueError):
		ds, ts = msise._nrlmsise00.gtd7(*STD_INPUT_C, flags=list(range(23)) + [24.])


def test_py_invalid_length():
	# python functions
	with pytest.raises(ValueError):
		ds, ts = msise.msise_model(*STD_INPUT_PY, ap_a=[0., 1., 2., 3.])
	with pytest.raises(ValueError):
		ds, ts = msise.msise_model(*STD_INPUT_PY, flags=[0, 1, 2, 3])


def test_py_invalid_types():
	# python functions
	with pytest.raises(ValueError):
		ds, ts = msise.msise_model(*STD_INPUT_PY, ap_a=list(range(6)) + ["6"])
	with pytest.raises(ValueError):
		ds, ts = msise.msise_model(*STD_INPUT_PY, flags=list(range(23)) + [24.])
