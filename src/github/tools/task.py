"""
Created on 19 Apr 2009

@author: damien
"""
from __future__ import with_statement
import webbrowser
import sys
import os

from paver.easy import task, options, sh, Bunch, path, needs, cmdopts
from git import Git

from github.tools.gh_pages import GitHubRepo, Credentials

def _adjust_options():
    if options.get('_github_tools_options_adjusted') is None:
        options.setdefault('sphinx', Bunch())
        options.setdefault('gh_pages', Bunch())
        
        options.sphinx.docroot = docroot \
            = path( options.sphinx.get('docroot', 'docs'))
        options.sphinx._buildir = buildir = \
            docroot /  options.sphinx.get('builddir', 'build')
        options.sphinx._sourcedir = docroot /  options.sphinx.get('sourcedir', 'source')
        options.sphinx._doctrees = buildir / "doctrees"
        options.sphinx._htmldir = htmldir = \
            buildir / 'html'
        
        gh_pages_root = options.gh_pages.get('root', None)
        if gh_pages_root is None:
            options.gh_pages.root = htmldir
        else:
            options.gh_pages.root = path(gh_pages_root)
        
        options._github_tools_options_adjusted = True

def _get_repo(wc):
    git_dir = os.path.join(wc, '.git')
    if os.path.exists(git_dir) and os.path.isdir(git_dir):
        return GitHubRepo(wc)
    sys.exit('%s is not a git directory.' % os.getcwd())
    

def get_repo_deco(fn):
    def checker(self, *args, **kw):
        wc = os.getcwd()
        kw['_repo'] = _get_repo(wc)
        return fn(*args, **kw)
    return checker

@task
def gh_register():
    """Create a repository at GitHub and push it your local repository"""
    repo = _get_repo(os.getcwd())
    project = repo.register(
        options.setup.name,
        Credentials.get_credentials(repo),
        description='',
        is_public=True,
        remote_name='origin')
    webbrowser.open(project.url.http)

@task
def gh_pages_create():
    """Create a submodule to host your Sphinx documentation."""
    _adjust_options()
    repo = _get_repo(os.getcwd())
    repo.add_gh_pages_submodule(
        gh_pages_path=str(options.gh_pages.root),
        remote_name='origin')

@task
@needs('github.tools.task.gh_html')
@cmdopts([
    ('commit-message=', 'm', 'commit message for the doc update')
])
def gh_pages_update():
    """Rebuild your documentation push it to GitHub"""
    _adjust_options()
    repo = _get_repo(options.gh_pages.root)
    repo.git.add('.')
    if options.gh_pages_update.get('commit_message') is None:
        print ("No commit message set... "
            "You will have to commit the last changes "
            "and push them to GitHub")
    repo.git.commit('-m', options.gh_pages_update.commit_message)
    repo.git.push('origin', 'gh-pages')

@task
def gh_doc_clean():
    """Clean your documentation.
    
    Update the submodule (every changes not committed and pushed will be lost),
    pull any changes and remove any file
    """
    _adjust_options()
    repo = _get_repo(os.getcwd())
    repo.submodules[options.gh_pages.root].update()
    Git(options.gh_pages.root).pull('origin', 'gh-pages')
    for f in options.sphinx._htmldir.listdir():
        if f.isdir():
            if f.basename() != '.git':
                f.rmtree()
        else:
            f.unlink()

@task
@needs('github.tools.task.gh_doc_clean')
def gh_html():
    """Build documentation."""
    _adjust_options()
    sh('sphinx-build -d %s -b html %s %s' % (
        options.sphinx._doctrees,
        options.sphinx._sourcedir,
        options.sphinx._htmldir))