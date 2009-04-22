"""
Models to manage the hosting of a package on GitHub 
"""
from __future__ import with_statement
from urllib import urlencode
from ConfigParser import RawConfigParser
import urllib2
import os

try:
    import json #@UnresolvedImport
except ImportError:
    import simplejson as json

from git import Git, Repo as _Repo


class Credentials(object):
    """
    User credential as set with
    the github.user and github.token git config values
    """
    
    def __init__(self, user=None, token=None):
        self.user = user
        self.token = token
        
    @classmethod
    def get_credentials(cls, repo=None):
        """
        Get credentials from the github.user and github.token config values
        """
        if repo:
            _git = repo.git
        else:
            _git = Git(os.getcwd())
        return cls(
            user=_git.config('github.user'),
            token=_git.config('github.token')
            )


class GitHubProject(object):
    """
    GitHub project class
    """
    PROJECT_URL_TEMPLATE = 'git@github.com:%s/%s.git'
    
    def __init__(self,
                name= None,
                owner=None,
                description=None,
                is_public=None):
        self.name = name
        self.owner = owner
        self.description = description
        self.is_public = is_public
    
    @property 
    def url(self):
        """
        return project url on github
        """ 
        if self.name is None:
            raise AttributeError('Project name not defined')
        if self.owner is None:
            self.owner = Credentials.get_credentials(self.repo).user
        if not self.owner:
            raise AttributeError('The project owner or the github user need to be set.')
        return self.PROJECT_URL_TEMPLATE % (
            self.owner, self.name)
    
    @classmethod
    def create(cls,
        project_name, credentials,
        description='', is_public=True):
        """
        Create a new GitHub project.
        """ 
        data = dict(
            login=credentials.user,
            token=credentials.token,
            name=project_name,
            description=description,
            public=int(is_public))
        url = 'http://github.com/api/v2/json/repos/create'
        json_details = urllib2.urlopen(url, urlencode(data))
        return cls.get_project_from_json(json_details)
    
    @classmethod
    def get_project(cls, project_name, owner):
        """Fetch the project details from GitHub"""
        url = "http://github.com/api/v2/json/repos/show/%s/%s" % (
            owner, project_name)
        json_details = urllib2.urlopen(url)
        return cls.get_project_from_json(json_details)
    
    @classmethod
    def get_project_from_json(cls, json_details):    
        details = json.load(json_details)['repository']
        return GitHubProject(
            name=details['name'],
            owner=details['owner'],
            description=details['description'],
            is_public= not details['private'])


class Repo(_Repo):
    """
    Overwrite git.Repo to add submodule support
    and create repository with working copy.
    """
    
    def __init__(self, path=None):
        super(Repo, self).__init__(path)
        self.submodules = SubmoduleDict(self)
        
    @classmethod
    def create(cls, path=None, mk_dir=False):
        """
        Initialise the repository WITH a working copy
        """
        if not os.path.exists(path) and mk_dir:
            os.mkdir(path)
        _git = Git(path or os.curdir)
        _git.init()
        return cls(path=path)


class GitHubRepo(Repo):
    """
    GitHubRepo instance for a repository cloned to/from GitHub.
    
    Allow to manage gh-pages as a submodule.
    """
    
    def __init__(self, path=None):
        super(GitHubRepo, self).__init__(path)
        self.submodules = SubmoduleDict(self)
    
    def register(self,
        project_name, credentials=None,
        description='', is_public=True,
        remote_name='origin'):
        """
        Add the project to GitHub 
        """
        if credentials is None:
            credentials = Credentials.get_credentials(self)
        project = GitHubProject.create(
           project_name, credentials=credentials,
           description=description, is_public=is_public)
        self.git.remote('add', remote_name, project.url)
        self.git.push(remote_name, 'master')
        
    def add_gh_pages_submodule(self, project_url, gh_pages_path):
        self.submodules.add(project_url, gh_pages_path)
        
        #create gh-pages branch
        gh_pages = Repo(gh_pages_path)
        gh_pages.git.symbolic_ref('HEAD', 'refs/heads/gh-pages')
        index = os.path.join(gh_pages.path, 'index')
        if os.path.exists(index):
            os.unlink(index)
        with open(os.path.join(gh_pages_path, 'index.html'), 'w') as f:
            f.write('Documentation coming soon...')
        gh_pages.git.add('index.html')
        gh_pages.git.commit('-m', 'initial commit')
        gh_pages.push('origin', 'gh-pages')
        
        # update submodule
        self.git.add(gh_pages_path)
        self.git.commit('-m', 'update gh-pages submodule')


class Submodule(object):
        
    def __init__(self, repo, url, module_path, sha=None, status=None):
        self.repo = repo
        self.path = module_path.rstrip('/')
        self.url = url
        self.sha = sha
        self.status = status
        
    def init(self, msg=None):
        if msg is None:
            msg = 'Add a submodule for "%s" at "%s' % (self.url, self.path,)
        if self.status in (None, '-'):
            self.repo.git.submodule('add', self.url, self.path)
            self.repo.git.submodule('init', self.path)
            self.repo.git.commit('-m', msg)


class SubmoduleDict(dict):
    
    def __init__(self, repo):
        self.repo = repo
        self._get_submodules()
        
    def __getitem__(self, path):
        self._get_submodules()
        return super(SubmoduleDict, self).__getitem__(path)
    
    def __setitem__(self, path, module):
        if module.path not in self:
            module.init()
        self._get_submodules()
        
    def __delitem__(self, name):
        raise AttributeError('Not implemented. You need to remove the module yourself.')
    
    def add(self,url, path):
        module = Submodule(self.repo, url, path)
        self.__setitem__(path, module)
    
    def clear(self):
        self._get_submodules()
    
    def _get_submodules(self):
        """
        Parse .gitmodule to get the list of submodules.
        """
        super(SubmoduleDict, self).clear()
        gitmodule = os.path.join(self.repo.git.get_dir, '.gitmodules')     
        if not os.path.exists(gitmodule):
            return
        cfg = RawConfigParser() 
        cfg.readfp(GitmoduleReader(gitmodule), gitmodule)
        for section in cfg.sections():
            path   = cfg.get(section, 'path')
            url    = cfg.get(section, 'url')
            info   = self.repo.git.submodule('status', path)
            status = info[0]
            sha    = info[1:41]
            module = Submodule(self.repo, url, path, sha=sha, status=status)
            super(SubmoduleDict, self).__setitem__(
                module.path,
                module)


class GitmoduleReader(file):
    def readline(self,*args, **kw):
        return file.readline(self,*args, **kw).lstrip()