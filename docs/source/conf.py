# Configuration file for the Sphinx documentation builder.
import os
import sys

# -- Project information

project = 'pyGuardPoint'
copyright = '2025, SensorAccess'
author = 'John Owen'

release = '1.8.0'
version = '1.8.0'

# -- General configuration
sys.path.insert(0, os.path.abspath('../../pyGuardPoint_Build/pyGuardPoint'))


autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
}

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

autodoc_member_order = 'bysource'

