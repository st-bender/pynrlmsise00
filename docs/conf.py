# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import getenv

from nrlmsise00 import __version__

project = u'pynrlmsise00'
copyright = u'2020, Stefan Bender'
author = u'Stefan Bender'

version = __version__
release = __version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'recommonmark',
    'numpydoc'
]
if getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_GB'

master_doc = 'index'

language = None

htmlhelp_basename = 'pynrlmsise00doc'

# autodoc_docstring_signature = False
# autodoc_dumb_docstring = True
autosummary_generate = True

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'pynrlmsise00.tex', u'pynrlmsise00 Documentation',
     u'Stefan Bender', 'manual'),
]

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'pynrlmsise00', u'pynrlmsise00 Documentation',
     [author], 1)
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'pynrlmsise00', u'pynrlmsise00 Documentation',
     author, 'pynrlmsise00', 'Space weather indices for python.',
     'Miscellaneous'),
]

# on_rtd is whether we are on readthedocs.org
on_rtd = getenv("READTHEDOCS", None) == "True"
if not on_rtd:
    import sphinx_rtd_theme
    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

exclude_patterns = [u'_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'default'
templates_path = ['_templates']
html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = True
html_sidebars = {
    '**': ['searchbox.html', 'localtoc.html', 'relations.html',
          'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)
html_context = dict(
    display_github=True,
    github_user="st-bender",
    github_repo="pynrlmsise00",
    github_version="master",
    conf_py_path="/docs/",
)
html_static_path = ["_static"]
# Switch to old behavior with html4, for a good display of references,
# as described in https://github.com/sphinx-doc/sphinx/issues/6705
html4_writer = True

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'xarray': ('https://xarray.pydata.org/en/stable/', None),
}
