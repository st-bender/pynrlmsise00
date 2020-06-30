# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import datetime as dt
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
