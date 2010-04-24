Changes
=======

0.2-rc1 (April 24, 2010)
------------------------

- Change GitPython requirement. Requires version 1.6 specifically (version 0.3 will track GitPython 2.x).
- The gh_pages_clean task correctly checkout the gh-pages branch in the gh-pages submodule.

0.2b3 (January 30, 2010)
------------------------

- Installation of Template dependencies is now optional.

0.2b2 (January 11, 2010)
------------------------

- Fix bug with gh_package template when github.user or github.token
  git config values are not set.
- Disable Sphinx extension and add a .nojekyll file to allow the use of 
  folder starting with "_".

0.2b1 (August 26, 2009)
-----------------------

- New Layout, without a ``src/`` folder to hold package(s) or ``docs/source``
  to  hold the ReST documentation - Based on `Paver-templates`_' main template.


0.1.7 (July 18, 2009)
---------------------

- Fixed bug in gh_register, failing to set default gh_pages options.


0.1.6 (July 9, 2009)
--------------------

- Fixed with github-tools' template. Failed when git's user.name and user.email
  config variables were not set
- Removed distribution info from package's ``__init__.py`` file,
  so that pavement.py doesn't need to the package to get them.
  Github-tools uses pkginfo to get these info when it needs them.


0.1.4 (July 5, 2009)
--------------------

- Added required files to MANIFEST.in; the gh_package template was 
  missing from the distribution.  


0.1.3 (Jun 17, 2009)
--------------------

- Fixed a bug with github-tools' pavement.py. 


0.1.2 (Jun 14, 2009)
--------------------

- Fixed a bug in in the ``doc/source/conf.py`` created with github-tools' paste
  template.


0.1.0 (Jun 12, 2009):
---------------------

- Initial release.


.. _Paver-Templates: http://pypi.python.org/pypi/paver-templates/