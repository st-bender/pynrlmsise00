#include <Python.h>
#include "nrlmsise-00.h"

PyObject *module;

static char module_docstring[] =
	"NRLMSISE-00 wrapper module";
static char gtd7_docstring[] =
	"MSIS Neutral Atmosphere Empircial Model from the surface to lower exosphere.\n\n\
	Parameters\n\
	----------\n\
	year: int\n\
		Year, but has no real effect, more important is `doy`.\n\
	doy: int\n\
		Day of the year.\n\
	sec: float\n\
		Seconds into the day (UT).\n\
	alt: float\n\
		Altitude in [km].\n\
	g_lat: float\n\
		Geodetic latitude in [degrees N].\n\
	g_long: float\n\
		Geodetic longitude in [degrees E].\n\
	lst: float\n\
		Apparent local solar timei [h].\n\
	f107A: float\n\
		81 day average of 10.7 cm radio flux (**centered on doy**)\n\
		at the actual distance of the Earth from the Sun rather\n\
		than the radio flux at 1 AU.\n\
	f107: float\n\
		Daily F10.7 flux for **previous day** at position of Earth.\n\
		Like `f107A` at the actual distance of the Earth from the Sun\n\
		rather than the radio flux at 1 AU.\n\
	ap: float\n\
		Daily geomagnetic ap index.\n\
	ap_a: list of 7 floats, optional\n\
		Array containing the following magnetic values:\n\n\
		0. daily AP\n\
		1. 3 hr AP index for current time\n\
		2. 3 hr AP index for 3 hrs before current time\n\
		3. 3 hr AP index for 6 hrs before current time\n\
		4. 3 hr AP index for 9 hrs before current time\n\
		5. Average of eight 3 hr AP indicies from 12 to 33 hrs \n\
			prior to current time\n\
		6. Average of eight 3 hr AP indicies from 36 to 57 hrs \n\
			prior to current time \n\
	flags: list of 24 int, optional\n\
		Sets the model's internal `switches` array.\n\
		Quote from the NRLMSISE-00 source code:\n\
		Switches: to turn on and off particular variations use these switches.\n\
		0 is off, 1 is on, and 2 is main effects off but cross terms on.\n\n\
		Standard values are 0 for switch 0 and 1 for switches 1 to 23. The \n\
		array 'switches' needs to be set accordingly by the calling program.\n\
		The arrays sw and swc are set internally.\n\n\
		switches[i]:\n\n\
		0. output in meters and kilograms instead of centimetres and grams\n\
		1. F10.7 effect on mean\n\
		2. time independent\n\
		3. symmetrical annual\n\
		4. symmetrical semiannual\n\
		5. asymmetrical annual\n\
		6. asymmetrical semiannual\n\
		7. diurnal\n\
		8. semidiurnal\n\
		9. daily ap\n\
			[when this is set to -1 (!) the pointer\n\
			ap_a in struct nrlmsise_input must\n\
			point to a struct ap_array]\n\
		10. all UT/long effects\n\
		11. longitudinal\n\
		12. UT and mixed UT/long\n\
		13. mixed AP/UT/LONG\n\
		14. terdiurnal\n\
		15. departures from diffusive equilibrium\n\
		16. all TINF var\n\
		17. all TLB var\n\
		18. all TN1 var\n\
		19. all S var\n\
		20. all TN2 var\n\
		21. all NLB var\n\
		22. all TN3 var\n\
		23. turbo scale height var\n\n\
	Returns\n\
	-------\n\
	densities: list\n\
		the NRLMSISE-00 densities:\n\n\
		- d[0] - HE NUMBER DENSITY(CM-3)\n\
		- d[1] - O NUMBER DENSITY(CM-3)\n\
		- d[2] - N2 NUMBER DENSITY(CM-3)\n\
		- d[3] - O2 NUMBER DENSITY(CM-3)\n\
		- d[4] - AR NUMBER DENSITY(CM-3)\n\
		- d[5] - TOTAL MASS DENSITY(GM/CM3) [includes d[8] in td7d]\n\
		- d[6] - H NUMBER DENSITY(CM-3)\n\
		- d[7] - N NUMBER DENSITY(CM-3)\n\
		- d[8] - Anomalous oxygen NUMBER DENSITY(CM-3)\n\n\
		O, H, and N are set to zero below 72.5 km\n\n\
		d[5], TOTAL MASS DENSITY, is NOT the same for subroutines GTD7 \n\
		and GTD7D\n\
		SUBROUTINE GTD7 -- d[5] is the sum of the mass densities of the\n\
		species labeled by indices 0-4 and 6-7 in output variable d.\n\
		This includes He, O, N2, O2, Ar, H, and N but does NOT include\n\
		anomalous oxygen (species index 8).\n\
	temperatures: list\n\
		the NRLMSISE-00 temperatures:\n\n\
		- t[0] - EXOSPHERIC TEMPERATURE\n\
		- t[1] - TEMPERATURE AT ALT\n\n\
		t[0], Exospheric temperature, is set to global average for\n\
		altitudes below 120 km. The 120 km gradient is left at global\n\
		average value for altitudes below 72 km.\n\n\
	";
static char gtd7d_docstring[] =
	"MSIS Neutral Atmosphere Empircial Model from the surface to lower exosphere.\n\n\
	This subroutine provides Effective Total Mass Density for output\n\
	d[5] which includes contributions from 'anomalous oxygen' which can\n\
	affect satellite drag above 500 km. See 'returns' for\n\
	additional details.\n\n\
	Parameters\n\
	----------\n\
	*args:\n\t\tSame as for :func:`gtd7()`.\n\
	**kwargs:\n\t\tSame as for :func:`gtd7()`.\n\n\
	Returns\n\
	-------\n\
	densities, temperatures: lists\n\
		See documentation for :func:`gtd7()`, except for `d[5]`:\n\n\
		SUBROUTINE GTD7D -- d[5] is the 'effective total mass density\n\
		for drag' and is the sum of the mass densities of all species\n\
		in this model, INCLUDING anomalous oxygen.\
	";

/* Define PyInt_Check (python 2) also for python 3.
 * Improves python 2/3 compatibility. */
#if PY_MAJOR_VERSION >= 3
#define PyInt_Check PyLong_Check
#endif

static int list_to_ap(PyObject *ap_list, struct ap_array *ap_a)
{
	int i, ap_list_size = PyList_Size(ap_list);
	PyObject *val;

	if (ap_list_size != 7) {
		PyErr_SetString(PyExc_ValueError,
			"ap list has wrong size, must contain 7 elements.");
		return -1;
	}

	for (i = 0; i < 7; i++) {
		val = PyList_GetItem(ap_list, i);
		if (val && (PyFloat_Check(val) || PyInt_Check(val)))
			ap_a->a[i] = PyFloat_AsDouble(val);
		else {
			PyErr_SetString(PyExc_ValueError,
				"ap list has an invalid element, must be int or float.");
			return -22;
		}
	}

	return 0;
}

static int list_to_flags(PyObject *fl_list, struct nrlmsise_flags *fl)
{
	int i, sw_list_size = PyList_Size(fl_list);
	PyObject *val;

	if (sw_list_size != 24) {
		PyErr_SetString(PyExc_ValueError,
			"nrlmsise flags list ha wrong size, expected 24 elements");
		return -1;
	}

	for (i = 0; i < 24; i++) {
		val = PyList_GetItem(fl_list, i);
		if (val && PyInt_Check(val))
			fl->switches[i] = PyLong_AsLong(val);
		else {
			PyErr_SetString(PyExc_ValueError,
				"nrlmsise flags list has an invalid element, must be int.");
			return -22;
		}
	}

	return 0;
}

static PyObject *nrlmsise00_gtd7(PyObject *self, PyObject *args, PyObject *kwargs)
{
	struct nrlmsise_flags msis_flags = {
		{0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}};
	struct nrlmsise_output msis_output;
	struct nrlmsise_input msis_input;
	struct ap_array ap_arr;

	PyObject *ap_list = NULL, *flags_list = NULL;
	static char *kwlist[] = {"year", "doy", "sec", "alt", "g_lat", "g_long",
		"lst", "f107A", "f107", "ap", "ap_a", "flags", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iidddddddd|O!O!", kwlist,
				&msis_input.year,   /* year, currently ignored */
				&msis_input.doy,    /* day of year */
				&msis_input.sec,    /* seconds in day (UT) */
				&msis_input.alt,    /* altitude in kilometers */
				&msis_input.g_lat,  /* geodetic latitude */
				&msis_input.g_long, /* geodetic longitude */
				&msis_input.lst,    /* local apparent solar time (hours), see note below */
				&msis_input.f107A,  /* 81 day average of F10.7 flux (centered on doy) */
				&msis_input.f107,   /* daily F10.7 flux for previous day */
				&msis_input.ap,     /* magnetic index(daily) */
				&PyList_Type, &ap_list,
				&PyList_Type, &flags_list)) {
		return NULL;
	}
	if (ap_list)
		if (list_to_ap(ap_list, &ap_arr) != 0)
			return NULL;

	if (flags_list)
		if (list_to_flags(flags_list, &msis_flags) != 0)
			return NULL;

	msis_input.ap_a = &ap_arr;

	gtd7(&msis_input, &msis_flags, &msis_output);

	return Py_BuildValue("[ddddddddd][dd]",
			msis_output.d[0], msis_output.d[1], msis_output.d[2],
			msis_output.d[3], msis_output.d[4], msis_output.d[5],
			msis_output.d[6], msis_output.d[7], msis_output.d[8],
			msis_output.t[0], msis_output.t[1]);
}

static PyObject *nrlmsise00_gtd7d(PyObject *self, PyObject *args, PyObject *kwargs)
{
	struct nrlmsise_flags msis_flags = {
		{0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}};
	struct nrlmsise_output msis_output;
	struct nrlmsise_input msis_input;
	struct ap_array ap_arr;

	PyObject *ap_list = NULL, *flags_list = NULL;
	static char *kwlist[] = {"year", "doy", "sec", "alt", "g_lat", "g_long",
		"lst", "f107A", "f107", "ap", "ap_a", "flags", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iidddddddd|O!O!", kwlist,
				&msis_input.year,   /* year, currently ignored */
				&msis_input.doy,    /* day of year */
				&msis_input.sec,    /* seconds in day (UT) */
				&msis_input.alt,    /* altitude in kilometers */
				&msis_input.g_lat,  /* geodetic latitude */
				&msis_input.g_long, /* geodetic longitude */
				&msis_input.lst,    /* local apparent solar time (hours), see note below */
				&msis_input.f107A,  /* 81 day average of F10.7 flux (centered on doy) */
				&msis_input.f107,   /* daily F10.7 flux for previous day */
				&msis_input.ap,     /* magnetic index(daily) */
				&PyList_Type, &ap_list,
				&PyList_Type, &flags_list)) {
		return NULL;
	}
	if (ap_list)
		if (list_to_ap(ap_list, &ap_arr) != 0)
			return NULL;

	if (flags_list)
		if (list_to_flags(flags_list, &msis_flags) != 0)
			return NULL;

	msis_input.ap_a = &ap_arr;

	gtd7d(&msis_input, &msis_flags, &msis_output);

	return Py_BuildValue("[ddddddddd][dd]",
			msis_output.d[0], msis_output.d[1], msis_output.d[2],
			msis_output.d[3], msis_output.d[4], msis_output.d[5],
			msis_output.d[6], msis_output.d[7], msis_output.d[8],
			msis_output.t[0], msis_output.t[1]);
}

static PyMethodDef nrlmsise00_methods[] = {
	{"gtd7", (PyCFunction) nrlmsise00_gtd7, METH_VARARGS | METH_KEYWORDS, gtd7_docstring},
	{"gtd7d", (PyCFunction) nrlmsise00_gtd7d, METH_VARARGS | METH_KEYWORDS, gtd7d_docstring},
	{NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef nrlmsise00_module = {
	PyModuleDef_HEAD_INIT,
	"_nrlmsise00",   /* name of module */
	module_docstring, /* module documentation, may be NULL */
	-1,       /* size of per-interpreter state of the module,
				 or -1 if the module keeps state in global variables. */
	nrlmsise00_methods
};


PyMODINIT_FUNC PyInit__nrlmsise00(void)
{
	module = PyModule_Create(&nrlmsise00_module);
	return module;
}

#else

PyMODINIT_FUNC init_nrlmsise00(void)
{
	module = Py_InitModule("_nrlmsise00", nrlmsise00_methods);
}

#endif
