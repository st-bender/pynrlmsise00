# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import datetime as dt
import numpy as np
import pytest

from nrlmsise00.dataset import msise_4d


@pytest.mark.parametrize(
	"ap, lon, lst", [
		(None, -70., None),
		(4., -70., 16.),
		([5., 6.], -70., [6., 18.]),
		(None, [-70, 0., 70.], [5., 7., 12.]),
		(None, [-70, 0., 70.], [[5., 17.], [6., 18.], [7., 19.]]),
		(None, [-70, 0., 70.], [[5., 6., 7.], [17., 18., 19.]]),
	]
)
def test_dataset(ap, lon, lst):
	# checks that broadcasting works as intended
	ds = msise_4d(
		[dt.datetime(2009, 6, 21, 8, 3, 20), dt.datetime(2009, 12, 21, 16, 3, 20)],
		[400, 200, 100],  # alt
		[60, 30, 0, -30, -60],  # g_lat
		lon,    # g_long
		150,    # f107A
		150,    # f107
		ap=ap,  # ap
		lst=lst,
	)
	assert ds


@pytest.mark.parametrize(
	"lon, lst, lst_expected", [
		(
			0,
			None,
			np.array([8., 16.]).reshape(2, 1),
		),
		(
			[30, 150],
			None,
			np.array([[10., 18.], [18., 26.]]).reshape(2, 2),
		),
		(
			[30, 120, 150],
			None,
			np.array([[10., 16., 18.], [18., 24., 26.]]),
		),
		(
			[30, 120, 150],
			[10., 16.],  # same shape as "time"
			np.array([[10., 10., 10.], [16., 16., 16.]]),
		),
		(
			[30, 120, 150],
			[10., 16., 18.],  # same shape as "lon"
			np.array([[10., 16., 18.], [10., 16., 18.]]),
		),
	]
)
def test_lst(lon, lst, lst_expected):
	# checks that local time works as intended
	ds = msise_4d(
		[dt.datetime(2009, 6, 21, 8), dt.datetime(2009, 12, 21, 16)],
		[400, 200, 100],  # alt
		[60, 30, 0, -30, -60],  # g_lat
		lon,    # g_long
		150,    # f107A
		150,    # f107
		4,      # ap
		lst=lst,
	)
	assert ds
	np.testing.assert_allclose(ds.lst.values, lst_expected)


def test_nd_raise():
	with pytest.raises(ValueError, match=r"Only scalars and up to 1-D .*"):
		msise_4d(
			dt.datetime(2009, 6, 21, 8),
			# 2-d should fail
			[[200]],  # alt
			60,   # g_lat
			-70,  # g_long
			150,  # f107A
			150,  # f107
			4,    # ap
		)
