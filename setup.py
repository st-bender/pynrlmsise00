from codecs import open
from os import path
import re
# Always prefer setuptools over distutils
from setuptools import find_packages, setup
from subprocess import check_call
from distutils.core import Extension

name = "nrlmsise00"
meta_path = path.join("src", name, "__init__.py")
here = path.abspath(path.dirname(__file__))

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
		"dataset": ["spaceweather", "xarray"],
		"docs": ["sphinx!=3.2.0"],
}
extras_require["all"] = sorted(
		{v for req in extras_require.values() for v in req})


# Approach taken from
# https://packaging.python.org/guides/single-sourcing-package-version/
# and the `attrs` package https://www.attrs.org/
# https://github.com/python-attrs/attrs
def read(*parts):
	"""
	Builds an absolute path from *parts* and and return the contents of the
	resulting file.  Assumes UTF-8 encoding.
	"""
	with open(path.join(here, *parts), "rb", "utf-8") as f:
		return f.read()


def find_meta(meta, *path):
	"""
	Extract __*meta*__ from *path* (can have multiple components)
	"""
	meta_file = read(*path)
	meta_match = re.search(
		r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta), meta_file, re.M
	)
	if not meta_match:
		raise RuntimeError("__{meta}__ string not found.".format(meta=meta))
	return meta_match.group(1)


# Get the long description from the README file
long_description = read("README.md")
version = find_meta("version", meta_path)

if __name__ == "__main__":
	# update git submodules
	if path.exists(".git"):
		check_call(["git", "submodule", "update", "--init", "--recursive"])

	setup(name=name,
		version=version,
		description="Python interface for the NRLMSISE-00 neutral atmosphere model",
		long_description=long_description,
		long_description_content_type="text/markdown",
		keywords="atmosphere earth model python-interface",
		author="Stefan Bender",
		author_email="stefan.bender@ntnu.no",
		url="https://github.com/st-bender/pynrlmsise00",
		project_urls={
			"Documentation": "https://pynrlmsise00.readthedocs.io",
		},
		license="GPLv2",
		classifiers=[
			"Development Status :: 4 - Beta",
			"Intended Audience :: Science/Research",
			"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
			"Operating System :: MacOS :: MacOS X",
			"Operating System :: Microsoft :: Windows",
			"Operating System :: POSIX :: Linux",
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
