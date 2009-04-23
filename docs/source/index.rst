Welcome to github.tools's documentation!
========================================

PasteScript template, Paver tasks and Sphinx extension to setup a new package
and easily host its on GitHub (including its documentation).

Setting up a root branch for gh-pages or integrating it with something like
Sphinx is quite complex; especially since Sphinx put its source and static files
in directories that gh-pages cannot serves.

The Sphinx extension (github.tools.sphinx) corrects the last problem; some paver
tasks (github.tools.task.*) take care of creation of a Git submodule to host
the built html documentation; The PasteScript template create the basic layout and
pavement.py script to get started.

This extension requires git (tested with 1.6.2.4), a GitHub user account and 
python 2.5 - which should not be a problem since your users won't need it.

Installation:
-------------

Assuming easy_installed, simple execute...::

	easy_install github.tools
	
Usage:
------

If you are starting from scratch, create the basic layout with paster::

	paster create -t gh_package <Project Name>
	
The project name will be used for pypi and for your Github repository
(http://github.com/<user>/<project name>). You can change it later
in your __init__.py package.

Paver will need your user name and github token to use GitHub api. You can
set them with the following command::

	git config --global github.user <user>
	git config --global github.token <token>
	
You can find your token on you Github account page.


 

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

