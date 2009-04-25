import os
import sys

from paver.easy import *
from paver.setuputils import setup
from setuptools import find_packages

try:
    from github.tools.task import *
    from paver.virtual import bootstrap
except:
    print "bootstrap task not available"

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, 'src'))

from github.tools import project, release as version, author, author_email, description, licence

long_description = open('README.rst', 'r').read()

classifiers = [
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    "Programming Language :: Python",
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

setup(name=project,
    version=version,
    description=description,
    long_description=long_description,
    classifiers=classifiers,
    keywords='',
    author=author,
    author_email=author_email,
    url='',
    license=licence,
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
           packages_to_install=[
            'Sphinx',
            'virtualenv',
            'Nose'
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
    