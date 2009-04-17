from paver.easy import *
from paver.setuputils import setup
from paver.virtual import bootstrap
from setuptools import find_packages
import paver.doctools

version = '0.1.0'

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
    'Cheetah'
    ]

entry_points="""
    # -*- Entry points: -*-
    """

setup(name='github.tools',
    version=version,
    description='Helpers for hosting  python projects on GitHub',
    long_description=long_description,
    classifiers=classifiers,
    keywords='',
    author='Damien Lebrun',
    author_email='dinoboff@hotmail.com',
    url='',
    license='BSD',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['github'],
    include_package_data=True,
    test_suite='nose.collector',
    test_requires=['Nose'],  
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entry_points,
    )

options(
    virtualenv=Bunch(
        script_name='bootstrap.py'
        ),
    )

@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
