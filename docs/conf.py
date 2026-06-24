import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'Contacts REST API'
copyright = '2026, Fedir Voynarovskiy'
author = 'Fedir Voynarovskiy'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']