# Python interface for the NRLMSISE-00 empirical neutral atmosphere model

[![builds](https://travis-ci.com/st-bender/pynrlmsise00.svg?branch=master)](https://travis-ci.com/st-bender/pynrlmsise00)
[![package](https://img.shields.io/pypi/v/nrlmsise00.svg?style=flat)](https://pypi.org/project/nrlmsise00)
[![wheel](https://img.shields.io/pypi/wheel/nrlmsise00.svg?style=flat)](https://pypi.org/project/nrlmsise00)
[![pyversions](https://img.shields.io/pypi/pyversions/nrlmsise00.svg?style=flat)](https://pypi.org/project/nrlmsise00)
[![codecov](https://codecov.io/gh/st-bender/pynrlmsise00/badge.svg)](https://codecov.io/gh/st-bender/pynrlmsise00)
[![coveralls](https://coveralls.io/repos/github/st-bender/pynrlmsise00/badge.svg)](https://coveralls.io/github/st-bender/pynrlmsise00)
[![scrutinizer](https://scrutinizer-ci.com/g/st-bender/pynrlmsise00/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/st-bender/pynrlmsise00/?branch=master)

This python version of the NRLMSISE00 upper atmosphere model is
based on the C-version of the code, available at www.brodo.de/space/nrlmsise.
The C code is imported as a `git` submodule from
[git://git.linta.de/~brodo/nrlmsise-00.git](git://git.linta.de/~brodo/nrlmsise-00.git)
(browsable version at:
[https://git.linta.de/?p=~brodo/nrlmsise-00.git](https://git.linta.de/?p=~brodo/nrlmsise-00.git)).

:warning: This python interface is in the **alpha** stage, that is, it may or
may not work, and the interface will most likely change in future versions.

**Quote** from https://ccmc.gsfc.nasa.gov/models/modelinfo.php?model=MSISE:

“The MSISE model describes the neutral temperature and densities in Earth's atmosphere from ground to thermospheric heights.
The NRLMSIS-00 empirical atmosphere model was developed by Mike Picone, Alan Hedin, and Doug Drob.”

## Install

### Requirements

- `numpy` - required
- `pytest` - optional, for testing

To compile the C source code, additional system header files may be required.
For example on Debian/Ubuntu Linux, the package `libc6-dev` is needed.

### pynrlmsise00

An **experimental** `pip` package called `nrlmsise00` is available from the
main package repository, and can be installed with:
```sh
$ pip install nrlmsise00
```
In some cases this will install from the source package and the note
above about the additional requirements applies.

As binary package support is limited, pynrlmsise00 can be installed
with [`pip`](https://pip.pypa.io) directly from github
(see <https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support>
and <https://pip.pypa.io/en/stable/reference/pip_install/#git>):
```sh
$ pip install [-e] git+https://github.com/st-bender/pynrlmsise00.git
```

The other option is to use a local clone:
```sh
$ git clone https://github.com/st-bender/pynrlmsise00.git
$ cd pynrlmsise00
$ git submodule init
$ git submodule update
```
and then using `pip` (optionally using `-e`, see
<https://pip.pypa.io/en/stable/reference/pip_install/#install-editable>):
```sh
$ pip install [-e] .
```

or using `setup.py`:
```sh
$ python setup.py install
```

Optionally, test the correct function of the module with
```sh
$ py.test [-v]
```

or even including the [doctests](https://docs.python.org/library/doctest.html)
in this document:
```sh
$ py.test [-v] --doctest-glob='*.md'
```

## Usage

The python module itself is named `nrlmsise00` and is imported as usual:
```python
>>> import nrlmsise00

```

Basic class and method documentation is accessible via `pydoc`:
```sh
$ pydoc nrlmsise00
```

### Python interface

The Python interface functions take `datetime.datetime` objects for
convenience. The local solar time is calculated from that time
and the given location, but it can be set explicitly via the `lst` keyword.
The returned value has the same format as the original C version (see below).
Because of their similarity, `gtd7()` and `gtd7d()` are selected via the
`method` keyword, `gtd7` is the default.

The return values are tuples of two lists containing
the densities (`d[0]`--`d[8]`) and temperatures (`t[0]`, `t[1]`).

The output has the same order as the C reference code, in particular:
* `d[0]` - He number density [cm⁻³]
* `d[1]` - O number density [cm⁻³]
* `d[2]` - N2 number density [cm⁻³]
* `d[3]` - O2 number density [cm⁻³]
* `d[4]` - Ar number density [cm⁻³]
* `d[5]` - total mass density [g cm⁻³]) (includes d[8] in `gtd7d()`)
* `d[6]` - H number density [cm⁻³]
* `d[7]` - N number density [cm⁻³]
* `d[8]` - Anomalous oxygen number density [cm⁻³]
* `t[0]` - exospheric temperature [K]
* `t[1]` - temperature at `alt` [K]

The `flags` and `ap_a` value array are set via keywords, but both default
to the standard setting, such that changing them should not be necessary
for most use cases.
For example setting `flag[0]` to `1` changes the output to metres
and kilograms instead of centimetres and grams (`0` is the default).

```python
>>> from datetime import datetime
>>> from nrlmsise00 import msise_model
>>> msise_model(datetime(2009, 6, 21, 8, 3, 20), 400, 60, -70, 150, 150, 4, lst=16)
([666517.690495152, 113880555.97522168, 19982109.255734544, 402276.3585712511, 3557.464994515886, 4.074713532757222e-15, 34753.12399717142, 4095913.2682930017, 26672.73209335869], [1250.5399435607994, 1241.4161300191206])

```

### NumPy interface

A `numpy` compatible *flat* version is available as `msise_flat()`,
it returns a 11-element `numpy.ndarray` with the densities in the
first 9 entries and the temperatures in the last two entries.
That is `ret = numpy.ndarray([d[0], ..., d[8], t[0], t[1]])`.
```python
>>> from datetime import datetime
>>> from nrlmsise00 import msise_flat
>>> msise_flat(datetime(2009, 6, 21, 8, 3, 20), 400, 60, -70, 150, 150, 4)
array([5.65085279e+05, 6.79850175e+07, 1.18819263e+07, 2.37030166e+05,
       1.32459684e+03, 2.39947892e-15, 5.32498381e+04, 1.07596246e+06,
       2.66727321e+04, 1.10058413e+03, 1.09824872e+03])

```

All arguments can be `numpy.ndarray`s, but must be broadcastable
to a common shape. For example to calculate the values for
three altitudes (200, 300, and 400 km) and two latitude locations
(60 and 70 °N) simultaneously, one can use `numpy.newaxis`
(which is equal to `None`) like this:
```python
>>> from datetime import datetime
>>> import numpy as np
>>> from nrlmsise00 import msise_flat
>>> alts = np.arange(200, 401, 100.)  # = [200, 300, 400] [km]
>>> lats = np.arange(60, 71, 10.)  # = [60, 70] [°N]
>>> # Using broadcasting, the output will be a 2 x 3 x 11 element array:
>>> msise_flat(datetime(2009, 6, 21, 8, 3, 20), alts[None, :], lats[:, None], -70, 150, 150, 4)
array([[[1.36949418e+06, 1.95229496e+09, 3.83824808e+09, 1.79130515e+08,
         4.92145034e+06, 2.40511268e-13, 8.34108685e+04, 1.74317585e+07,
         3.45500931e-08, 1.10058413e+03, 9.68827485e+02],
        [8.40190601e+05, 3.25739060e+08, 1.82477392e+08, 5.37973134e+06,
         6.53609278e+04, 1.75304136e-14, 5.92944463e+04, 4.36516218e+06,
         1.03939126e+02, 1.10058413e+03, 1.08356514e+03],
        [5.65085279e+05, 6.79850175e+07, 1.18819263e+07, 2.37030166e+05,
         1.32459684e+03, 2.39947892e-15, 5.32498381e+04, 1.07596246e+06,
         2.66727321e+04, 1.10058413e+03, 1.09824872e+03]],
<BLANKLINE>
       [[1.10012225e+06, 1.94725472e+09, 4.08547233e+09, 1.92320077e+08,
         6.65460281e+06, 2.52846563e-13, 6.16745965e+04, 2.45012145e+07,
         5.21846603e-08, 1.13812434e+03, 1.00132640e+03],
        [6.83809952e+05, 3.42643970e+08, 2.13434661e+08, 6.43426889e+06,
         1.01162173e+05, 1.95300073e-14, 4.36031132e+04, 6.70490625e+06,
         1.59911615e+02, 1.13812434e+03, 1.12084651e+03],
        [4.65787225e+05, 7.52160226e+07, 1.51795904e+07, 3.13560147e+05,
         2.32541183e+03, 2.76353370e-15, 3.92811827e+04, 1.73321928e+06,
         4.12296154e+04, 1.13812434e+03, 1.13580463e+03]]])

```

### Xarray Dataset interface

Output to a 4-D `xarray.Dataset` is supported via the `dataset` submodule
which can be installed with:
```sh
pip install [-U] 'nrlmsise00[dataset]'
```

This module provides a 4-D version `msise_4d()` to broadcast the
1-D inputs for time, altitude, latitude, and longitude.
It also uses the [`spaceweather`](https://pypi.org/spaceweather) package
by default to automatically obtain the geomagnetic and Solar flux indices.
The variable names are set according to the MSIS output.
```python
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

```

### C model interface

The C submodule directly interfaces the model functions `gtd7()` and `gtd7d()`
by importing `nrlmsise00._nrlmsise00`.
```python
>>> from nrlmsise00._nrlmsise00 import gtd7, gtd7d
>>> # using the standard flags
>>> gtd7(2009, 172, 29000, 400, 60, -70, 16, 150, 150, 4)
([666517.690495152, 113880555.97522168, 19982109.255734544, 402276.3585712511, 3557.464994515886, 4.074713532757222e-15, 34753.12399717142, 4095913.2682930017, 26672.73209335869], [1250.5399435607994, 1241.4161300191206])

```

This module also provides "flat" variants of the C functions as `gtd7_flat()`
and `gtd7d_flat()`. For example using `gtd7()` the same way as above:
```python
>>> import numpy as np
>>> from nrlmsise00 import gtd7_flat
>>> alts = np.arange(200, 401, 100.)  # = [200, 300, 400] [km]
>>> lats = np.arange(60, 71, 10.)  # = [60, 70] [°N]
>>> # Using broadcasting, the output will be a 2 x 3 x 11 element array:
>>> gtd7_flat(2009, 172, 29000, alts[None, :], lats[:, None], -70, 16, 150, 150, 4)
array([[[1.55567936e+06, 2.55949597e+09, 4.00342724e+09, 1.74513806e+08,
         6.56916263e+06, 2.64872982e-13, 5.63405578e+04, 4.71893934e+07,
         3.45500931e-08, 1.25053994e+03, 1.02704994e+03],
        [9.58507714e+05, 4.66979460e+08, 2.31041924e+08, 6.58659651e+06,
         1.16566762e+05, 2.38399390e-14, 3.86535595e+04, 1.43755262e+07,
         1.03939126e+02, 1.25053994e+03, 1.20645403e+03],
        [6.66517690e+05, 1.13880556e+08, 1.99821093e+07, 4.02276359e+05,
         3.55746499e+03, 4.07471353e-15, 3.47531240e+04, 4.09591327e+06,
         2.66727321e+04, 1.25053994e+03, 1.24141613e+03]],
<BLANKLINE>
       [[1.31669842e+06, 2.40644124e+09, 4.21778196e+09, 1.89878716e+08,
         8.17662024e+06, 2.71788520e-13, 4.64192484e+04, 5.13265845e+07,
         5.21846603e-08, 1.24246351e+03, 1.04698385e+03],
        [8.22632403e+05, 4.52803942e+08, 2.53857090e+08, 7.50201654e+06,
         1.53431033e+05, 2.46179628e-14, 3.20594861e+04, 1.62651506e+07,
         1.59911615e+02, 1.24246351e+03, 1.20963726e+03],
        [5.73944168e+05, 1.10836468e+08, 2.19925518e+07, 4.58648922e+05,
         4.68600377e+03, 4.10277781e-15, 2.89330169e+04, 4.65636025e+06,
         4.12296154e+04, 1.24246351e+03, 1.23665288e+03]]])

```

### Note

All functions require the solar 10.7 cm radio flux and and the geomagnetic Ap
index values to produce correct results.
In particular, according to the C source code:

- f107A: 81 day average of F10.7 flux (centered on the given day of year)
- f107: daily F10.7 flux for previous day
- ap: magnetic index (daily)

The f107 and f107A values used to generate the model correspond
to the 10.7 cm radio flux at the actual distance of the Earth
from the Sun rather than the radio flux at 1 AU.
The following site provides both classes of values (**outdated**):
ftp://ftp.ngdc.noaa.gov/STP/SOLAR_DATA/SOLAR_RADIO/FLUX/

f107, f107A, and ap effects are neither large nor well
established below 80 km and these parameters should be set to
150., 150., and 4. respectively.

# License

This python interface is free software: you can redistribute it or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 (GPLv2), see [local copy](./COPYING.GPLv2)
or [online version](http://www.gnu.org/licenses/gpl-2.0.html).

The [C source code of NRLMSISE-00](https://www.brodo.de/space/nrlmsise)
is in the public domain, see [COPYING.NRLMSISE-00](./COPYING.NRLMSISE-00).
