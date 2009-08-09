import os
import sys
import sets

from paver.easy import *
from paver.setuputils import setup

try:
    from paver.virtual import bootstrap
    from github.tools.task import (
        gh_pages_build,
        gh_pages_clean,
        gh_pages_create,
        gh_register)
    from git import Git
except ImportError:
    info("Some tasks could not been loaded")


version='0.1.7'

long_description = open('README.rst', 'r').read()

classifiers = [
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    "Programming Language :: Python :: 2.5", # not yet tested on python 2.6
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: POSIX :: Linux", # Not tested yet on osx or Windows
    "Topic :: Documentation",
    "Topic :: Software Development :: Version Control"
    ]

install_requires = [
    'setuptools>=0.6c9',
    'paver-templates>=0.1.0b3',
    'GitPython>=0.1.6',
    'simplejson',
    ]

entry_points="""
    # -*- Entry points: -*-
    [paste.paster_create_template]
    gh_package = github.tools.template:GithubTemplate
    """

setup(name='github-tools',
    version=version,
    description='Helpers for Python package hosting at GitHub',
    long_description=long_description,
    classifiers=classifiers,
    keywords='sphinx github paster',
    author='Damien Lebrun',
    author_email='dinoboff@hotmail.com',
    url='http://dinoboff.github.com/github-tools/',
    license='BSD',
    packages = ['github.tools'],
    package_dir = {'': 'src'},
    namespace_packages=['github'],
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entry_points,
    )

options(
    minilib=Bunch(
        extra_files=[
            'doctools',
            'virtual'
            ]
        ),
    virtualenv=Bunch(
        script_name='bootstrap.py',
        dest_dir='./virtual-env/',
        packages_to_install=[
            'virtualenv>=1.3.3',
            'Nose>=0.10.4',
            'Mock>=0.5.0',
            ]
        ),
    sphinx=Bunch(
        docroot='docs',
        builddir='build',
        sourcedir='source',
        ),
    )


    
@task
def pip_requirements():
    """Create a pip requirement file."""
    req = sets.Set()
    for d in (
        options.virtualenv.get('packages_to_install', [])
        + options.setup.get('install_requires', [])
        ):
        req.add(d+'\n')
    
    f = open('dev-requirements.txt', 'w')
    try:
        f.writelines(req)
    finally:
        f.close()
        
@task
def manifest():
    """Generate a Manifest using 'git ls-files'"""
    manifest_in = open('MANIFEST.in', 'w')    
    try: 
        includes = (
            "include %s\n" % f 
            for f in Git('.').ls_files().splitlines()
            if (not os.path.basename(f).startswith('.') 
                and f != 'docs/build/html')
            )
        manifest_in.writelines(includes)
    finally:
        manifest_in.close()

@task
@needs('pip_requirements', 'generate_setup', 'manifest', 'minilib',
    'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""


@task
@needs('gh_pages_build', 'github.tools.task.gh_pages_update')
def gh_pages_update():
    """Overrides github.tools.task to rebuild the doc (with sphinx)."""
    
    
tag_name = 'v%s' % version
    
@task
def tag():
    """tag a new version of this distribution"""
    git = Git('.')
    git.pull('origin', 'master')
    git.tag(tag_name)


@task
@needs('sdist', 'tag', 'setuptools.command.upload',)
def upload():
    """Upload the distribution to pypi, the new tag and the doc to Github"""
    options.update(
        gh_pages_update=Bunch(commit_message='Update doc to %s' % version))
    gh_pages_update()
    Git('.').push('origin', 'master', tag_name)