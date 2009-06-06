import os
import sys

from paver.easy import *
from paver.setuputils import setup
from setuptools import find_packages

try:
    from paver.virtual import bootstrap
except:
    info("bootstrap task not available")
    
try:
    from github.tools.task import (
        gh_pages_build,
        gh_pages_clean,
        gh_pages_create,
        gh_register) 
except:
    info("github-tools' task not available")

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, 'src'))

import github.tools

long_description = open('README.rst', 'r').read()

classifiers = [
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    "Programming Language :: Python :: 2.5", # not yet tested on python 2.6
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Framework :: Paste",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: POSIX :: Linux", # Not tested yet on osx or Windows
    "Topic :: Documentation",
    "Topic :: Software Development :: Version Control"
    ]

install_requires = [
    'setuptools',
    'Sphinx',
    'Paver',
    'PasteScript',
    'Cheetah',
    'virtualenv',
    'GitPython'
    ]

try:
    import json
except ImportError:
    install_requires.append('simplejson')

entry_points="""
    # -*- Entry points: -*-
    [paste.paster_create_template]
    gh_package = github.tools.template:GithubTemplate
    """

setup(name=github.tools.PROJECT,
    version=github.tools.RELEASE,
    description=github.tools.DESCRIPTION,
    long_description=long_description,
    classifiers=classifiers,
    keywords='sphinx, github, paster',
    author=github.tools.AUTHOR,
    author_email=github.tools.AUTHOR_EMAIL,
    url='http://dinoboff.github.com/github-tools/',
    license=github.tools.LICENCE,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['github'],
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entry_points,
    )

options(
    virtualenv=Bunch(
        script_name='bootstrap.py',
        dest_dir='./virtual-env/',
        packages_to_install=[
            'virtualenv',
            'Nose',
            'Mock',
            ]
        ),
    sphinx=Bunch(
        docroot='docs',
        builddir='build',
        sourcedir='source',
        ),
    )


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""

if 'gh_pages_build' in globals():
    
    @task
    @needs('gh_pages_build', 'github.tools.task.gh_pages_update')
    def gh_pages_update():
        """Overrides github.tools.task to rebuild the doc (with sphinx)."""