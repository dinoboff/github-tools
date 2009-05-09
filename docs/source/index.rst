Welcome to github.tools' documentation!
========================================

Summary:
--------

PasteScript template, Paver tasks and Sphinx extension to setup a new package
and easily host it on GitHub (including its documentation).


Description:
------------

Github features Git repository hosting, a download page for your Git tags (or any archive),
a basic issue tracker, a wiki and static page hosting (gh-pages). It would be perfect
for hosting a Python package and its documentation if gh-pages was easy to setup
and was compatible with Sphinx. 

Setting up a root branch for gh-pages and setting Sphinx html build directory as a repository
is quite complex; especially since Sphinx put its source and static files
in directories named "_static" and "_source" that gh-pages doesn't want to serve them.

The Sphinx extension (github.tools.sphinx) corrects the last problem; some paver
tasks (github.tools.task.*) take care of the creation of a Git submodule to host
the built html documentation; The PasteScript template create the basic layout and
pavement.py script to get started.

Requirements:
-------------

This extension and its dependencies require:

 * setup-tools,
 * Git (tested with 1.6.2.4),
 * a GitHub user account and, 
 * Python 2.5+.
 
It currently has only been tested on Ubuntu 8.04 (and Git built from source)
with Python 2.5.


Installation:
-------------

Assuming easy_install is installed, simple execute...::

	easy_install github-tools


Usage:
------

If you are starting from scratch, create the basic layout with paster::

	paster create -t gh_package <project name>
	
The project name will be used for pypi and for your Github repository
(http://github.com/<user>/<project name>). The project details are saved in
src/<package name>/__init__.py.

To finish your development environment setup, create a virtual environment
and deploy your package in development mode::

	cd <project name>
	python bootstrap.py --no-site-packages
	
The basic package comes with a virtualenv boostrap script
to create an  isolated Python environments. To activate this environment
in your shell, run::

	source ./virtual-env/bin/activate
	# or .\virtual-env\Scripts\activate.bat on windows

Finally::

	paver generate_setup minilib develop.

Paver add a setup.py file to your package and a portable paver library
(required by setup.py), and deploy your application in development mode; the src folder
which contains your package is added to the python path.

You are ready to write your package (in src/) and its documentation (in docs/source).
You should probably start tracking your project now::

	git init
	git add .
	git commit -m "initial import"  

When you are ready to share your work, you will need to 
create a repository at GitHub and push your local repository. Paver can do it for you.
Paver will need your GitHub user name and token to create the repository. You can
set them with the following command::

	git config --global github.user <user>
	git config --global github.token <token>
	
You can find your token on your Github account page.

Then, to create the repository and upload your project::

	paver gh_register
	
Once the project is created, you can create your gh-pages branch and upload it to github::

	paver gh_pages_create gh_html
	
Paver will create a submodule of your project at docs/build/html,
create a gh-pages root branch and push the branch to your project.
It then build the html doc. To clean the html build folder, it update the submodule
(you will lose changes not committed and pushed), remove every files and directory
(except .git/) and rebuild the documentation.

When your documentation can be published, simply push your gh-pages submodule to GitHub::

	paver gh_pages_update -m "update docs with..."

You might also want to update the submodule reference (a submodule point to specific
commit on a remote repository, not to the HEAD of a specific branch)::

	git add docs/build/html
	git commit -m "update gh-pages submodule" 


.. toctree::
   :maxdepth: 2
   
   template
   task
   sphinx

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

