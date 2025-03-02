# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys
sys.path.insert(0, os.path.abspath('../'))
import covsirphy as cs  # noqa: E402


# -- Project information -----------------------------------------------------

project = 'CovsirPhy'
copyright = '2020-2023, Hirokazu Takaya and CovsirPhy Development Team'
author = 'Hirokazu Takaya and CovsirPhy Development Team'
version = cs.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
    'sphinxcontrib.seqdiag',
    'nbsphinx',
    'sphinx.ext.mathjax',
    'sphinx_copybutton',
    'myst_parser',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store', '_build', '**.ipynb_checkpoints'
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_logo = "https://raw.githubusercontent.com/lisphilar/covid19-sir/master/docs/logo/covsirphy_logo_100.png"
html_favicon = "https://raw.githubusercontent.com/lisphilar/covid19-sir/master/docs/logo/covsirphy_favicon.ico"
html_show_sourcelink = False

html_theme_options = {
    "logo_only": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Extension configuration -------------------------------------------------

napoleon_use_param = True
napoleon_use_rtype = False
napoleon_use_ivar = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    'numpy': ('http://docs.scipy.org/doc/numpy', None),
    'matplotlib': ('http://matplotlib.org/stable', None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# https://stackoverflow.com/questions/20864406/remove-package-and-module-name-from-sphinx-function
add_module_names = False

# nbsphinx
# nbsphinx_execute: "always", "auto" or "never"
nbsphinx_execute = "always"
nbsphinx_kernel_name = "python"
