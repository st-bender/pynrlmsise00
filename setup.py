from codecs import open
from os import path
from sys import version_info
# Always prefer setuptools over distutils
from setuptools import find_packages, setup
from subprocess import check_call
from distutils.core import Extension

extnrlmsise00 = Extension(
		name="nrlmsise00._nrlmsise00",
		sources=[
			"src/nrlmsise00/nrlmsise00module.c",
			"src/c_nrlmsise-00/nrlmsise-00.c",
			"src/c_nrlmsise-00/nrlmsise-00_data.c"
		],
		include_dirs=["src/c_nrlmsise-00"])

extras_require = {
		"tests": ["pytest"],
		"dataset": ["xarray"],
}
extras_require["all"] = sorted(
		{v for req in extras_require.values() for v in req})

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
	long_description = f.read()

if __name__ == "__main__":
	# Approach copied from dfm (celerite, emcee, and george)
	# Hackishly inject a constant into builtins to enable importing of the
	# package before the library is built.
	if version_info[0] < 3:
		import __builtin__ as builtins
	else:
		import builtins
	builtins.__PYNRLMSISE_SETUP__ = True
	from src.nrlmsise00 import __version__

	# update git submodules
	if path.exists(".git"):
		check_call(["git", "submodule", "update", "--init", "--recursive"])

	setup(name="nrlmsise00",
		version=__version__,
		description="Python interface for the NRLMSISE-00 neutral atmosphere model",
		long_description=long_description,
		long_description_content_type="text/markdown",
		url="http://github.com/st-bender/pynrlmsise00",
		author="Stefan Bender",
		author_email="stefan.bender@ntnu.no",
		license="GPLv2",
		classifiers=[
			"Development Status :: 3 - Alpha",
			"Intended Audience :: Science/Research",
			"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
			"Programming Language :: Python",
			"Programming Language :: Python :: 2",
			"Programming Language :: Python :: 3",
			'Programming Language :: Python :: Implementation :: CPython',
			'Topic :: Scientific/Engineering :: Physics',
			'Topic :: Utilities',
		],
		packages=find_packages("src"),
		package_dir={"": "src"},
		package_data={},
		install_requires=[
			"numpy>=1.13.0",
		],
		extras_require=extras_require,
		ext_modules=[extnrlmsise00],
		scripts=[],
		entry_points={},
		zip_safe=False)
