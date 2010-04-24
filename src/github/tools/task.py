"""
:Description: Paver task to manage Python packages hosted at GitHub.

Configuration
-------------

These tasks use:

 * ``options.setup.name``, used for your GitHub repository name.
 * ``options.setup.description``, used for your GitHub repository description.
 * ``options.sphinx.docroot``, set by default to ``docs/``.
 * ``options.sphinx.build``, set by default to ``build``.
 * ``options.sphinx.source``, set by default to ``source``.
 * ``options.gh_pages.root``, local path to gh_pages root; set by default to
   ``<options.sphinx.docroot>``/``<options.sphinx.build>/html``
 * ``options.gh_pages.htmlroot``, local path to the html output of your doc
    built;  set by default ``options.gh_pages.root`` (you might want to host 
    more than your Sphinx doc there).
 * ``options.gh_pages.remote_name``, set by default to ``origin` and used for
   your github repository remote name.
 * ``options.gh_pages.master_branch``, set by default to ``master``.
 
``options.gh_pages.root`` and ``options.gh_pages.htmlroot`` will only be of
any used if you are using something else than Sphinx (and don't want to use 
Sphinx options).
"""

from __future__ import with_statement
import webbrowser
import sys
import os

from paver.easy import task, options, sh, Bunch, path, needs, cmdopts, dry, info
from git import Git

from github.tools.gh_pages import GitHubRepo, Credentials
from git.errors import GitCommandError


def _adjust_options():
    """
    Set default sphinx and gh_pages options.
    """
    if options.get('_github_tools_options_adjusted') is None:
        options.setdefault('sphinx', Bunch())
        options.setdefault('gh_pages', Bunch())
        options.setdefault('gh_pages_update', Bunch())
        
        options.sphinx.docroot = docroot \
            = path( options.sphinx.get('docroot', 'docs'))
        options.sphinx._buildir = buildir = \
            docroot /  options.sphinx.get('builddir', 'build')
        options.sphinx._sourcedir = \
            docroot /  options.sphinx.get('sourcedir', 'source')
        options.sphinx._doctrees = buildir / "doctrees"
        options.sphinx._htmldir = htmldir = \
            buildir / 'html'
        
        gh_pages_root = options.gh_pages.get('root', None)
        if gh_pages_root is None:
            options.gh_pages.root = htmldir
        else:
            options.gh_pages.root = path(gh_pages_root)
            
        gh_pages_htmlroot = options.gh_pages.get('htmlroot', None)
        if gh_pages_htmlroot is None:
            options.gh_pages.htmlroot = options.gh_pages.root
        else:
            options.gh_pages.htmlroot = path(gh_pages_htmlroot)
        options.gh_pages.setdefault('remote_name', 'origin')
        options.gh_pages.setdefault('master_branch', 'master')
        
        options._github_tools_options_adjusted = True

def _get_repo(working_copy):
    """
    Check that a directory is a git working copy.
    
    return a GitHubRepo instance or exit.
    """
    git_dir = os.path.join(working_copy, '.git')
    if os.path.exists(git_dir) and os.path.isdir(git_dir):
        return GitHubRepo(working_copy)
    sys.exit('%s is not a git directory.' % os.getcwd())

@task
def gh_register():
    """Create a repository at GitHub and push it your local repository."""
    _adjust_options()
    repo = _get_repo(os.getcwd())
    project_name = options.setup.name
    project_description = options.setup.get('description','')
    remote_name = options.gh_pages.remote_name
    master_branch = options.gh_pages.master_branch
    credentials = Credentials.get_credentials(repo)
    if not credentials:
        sys.exit('Your github name and token git config are not set.'
                 'Check http://github.com/blog/170-token-authentication' % os.getcwd())
    project = dry(
        "Create a repository called %s at %s's GitHub account..." % (
            project_name, credentials.user),
        repo.register,
        project_name,
        credentials,
        description=project_description,
        is_public=True,
        remote_name=remote_name,
        master_branch=master_branch)
    if project is not None:
        info('Opening your project home pages:%s', project.url.http)
        webbrowser.open(project.url.http)

@task
def gh_pages_create():
    """Create a submodule to host your documentation."""
    _adjust_options()
    repo = _get_repo(os.getcwd())
    remote_name = options.gh_pages.remote_name
    gh_pages_root = str(options.gh_pages.root)
    dry(
        "Create a submodule at %s and a gh-pages root branch "
            "to host your gh-pages..." % gh_pages_root,
        repo.add_gh_pages_submodule,
        gh_pages_path=gh_pages_root,
        remote_name=remote_name)

@task
@cmdopts([
    ('commit-message=', 'm', 'commit message for the doc update')
])
def gh_pages_update():
    """Push your documentation it to GitHub."""
    _adjust_options()
    
    
    repo = _get_repo(os.getcwd())
    remote_name = options.gh_pages.remote_name
    gh_pages_root = options.gh_pages.root
    
    # The gh_pages submodule need to checkout the
    try:
        gh_pages = repo.validate_gh_pages_submodule(gh_pages_root)
    except ValueError, e:
        sys.exit('You gh-pages is either not set or set on the wrong branch. \n'
                 'Update your submodule, checkout the gh-pages branch ' 
                 '(cd %s; git checkout -t origin/gh-pages) '
                 'and rebuild the documentation.' % gh_pages_root)
    
    dry("Add modified and untracked content to git index", gh_pages.git.add, '.')
    if options.gh_pages_update.get('commit_message') is None:
        info("No commit message set... "
            "You will have to commit the last changes "
            "and push them to GitHub")
        return
    msg = options.gh_pages_update.commit_message
    dry('"Commit any changes with message "%s".' % msg,
        gh_pages.git.commit, '-m', msg)
    dry("Push any changes on the gh-pages branch.",
        gh_pages.git.push, remote_name, 'gh-pages')
    info('You might want to update your submodule reference:\n\t'
        'git add %s\n\tgit commit -m "built html doc updated"'
        % options.gh_pages.root)

@task
def gh_pages_clean():
    """Clean your documentation.
    
    Update the submodule (every changes not committed and pushed will be lost),
    pull any changes and remove any file in options.gh_pages.docroot.
    """
    _adjust_options()
    remote_name = options.gh_pages.remote_name
    repo = _get_repo(os.getcwd())
    module = repo.submodules.get(options.gh_pages.root, None)
    if module is None:
        info("You have not yet created the gh-pages submodule.")
        return
    
    module.update()
    try:
        dry('Checkout the gh-pages branch', module.git.checkout, 'gh-pages') 
    except GitCommandError:
        dry('Checkout the gh-pages remote branch', 
            module.git.checkout, '-t', '%s/gh-pages' % remote_name)
    else:
        dry('Fetch any changes on the gh-pages remote branch',
            module.git.pull, remote_name, 'gh-pages')
    
    for dir_entry in options.gh_pages.htmlroot.listdir():
        if dir_entry.isdir():
            if dir_entry.basename() != '.git':
                dry("Remove %s" % dir_entry, dir_entry.rmtree)
        else:
            dry('Remove %s' % dir_entry, dir_entry.unlink)

@task
@needs('github.tools.task.gh_pages_clean', 'setuptools.command.egg_info')
def gh_pages_build():
    """Build your documentation with sphinx."""
    _adjust_options()
    sh('sphinx-build -d %s -b html %s %s' % (
        options.sphinx._doctrees,
        options.sphinx._sourcedir,
        options.sphinx._htmldir))
    # a .nojekyll file at the root of the gh-pages repository disable
    # Jekyll (http://github.com/blog/572-bypassing-jekyll-on-github-pages)
    no_jekyll = options.gh_pages.htmlroot / '.nojekyll'
    no_jekyll.touch()
    