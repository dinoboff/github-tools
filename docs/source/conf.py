# -*- coding: utf-8 -*-

import os

from pkg_resources import parse_version
import pkginfo


def _egg_info(path_to_egg='../../src/'):
    path_to_egg = os.path.join(
        os.path.dirname(__file__), path_to_egg)
    egg_info = pkginfo.Develop(path_to_egg)
    release = egg_info.version
    version = '%s.%s' % tuple(map(int, parse_version(release)[0:2]))
    return egg_info.name, egg_info.author, version, release

project, author, version, release = _egg_info()
copyright = '2009, %s' % author

# Extension
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    ]
intersphinx_mapping = {'http://docs.python.org/': None}

# Source
master_doc = 'index'
templates_path = ['_templates']
source_suffix = '.rst'
exclude_trees = []
pygments_style = 'sphinx'

# html build settings
html_theme = 'default'
html_static_path = ['_static']

# htmlhelp settings
htmlhelp_basename = '%sdoc' % project

# latex build settings
latex_documents = [
  ('index', '%s.tex' % project, u'%s Documentation' % project,
   author, 'manual'),
]