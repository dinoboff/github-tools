# -*- coding: utf-8 -*-

import os

from pkg_resources import parse_version
import pkginfo


class Develop(pkginfo.Develop):
    
    def __init__(self):
        here = os.path.dirname(__file__)
        egg_path = os.path.join(here, '..', '..', 'src')
        super(Develop, self).__init__(egg_path)
    
    def version_info(self):
         parsed_version = parse_version(self.version)
         version = '%s.%s' % tuple([int(x) for x in parsed_version[0:2]])
         revision = self.version
         return version, revision


egg_info = Develop()

version, release = egg_info.version_info()
project = egg_info.name
author = egg_info.author
copyright = '2009, %s' % author

# Extension
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'github.tools.sphinx',
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