"""
Github-tools Models. 
"""
from __future__ import with_statement
from urllib import urlencode
from ConfigParser import RawConfigParser
import urllib2
import os
from git.errors import GitCommandError

try:
    import json #@UnresolvedImport
except ImportError:
    import simplejson as json

from git import Git, Repo as _Repo


class Credentials(object):
    """
    User credential for Github API.
    """
    
    def __init__(self, user=None, token=None):
        self.user = user
        self.token = token
        
    def __len__(self):
        return bool(self.user and self.token)
        
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
            user=_git.config('github.user', with_exceptions=False),
            token=_git.config('github.token', with_exceptions=False)
            )


class GitHubProject(object):
    """
    GitHub project class
    """
    
    def __init__(self,
                name= None,
                owner=None,
                description=None,
                is_public=None):
        self.name = name
        self.owner = owner
        self.description = description
        self.is_public = is_public
        self._url = ProjectUrl(self)
    
    @property
    def url(self):
        return self._url
    
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


class ProjectUrl(object):
    """
    Holds the different GitHub urls of a project.
    """
    _tmpls = dict(
        ssh='git@github.com:%s/%s.git',
        git='git://github.com/%s/%s.git',
        http='http://github.com/%s/%s',
        gh_pages='http://%s.github.com/%s',
        issue='http://github.com/%s/%s/issues'
        )
    
    def __init__(self, project):
        self.project = project
    
    @property  
    def ssh(self):
        """SSH url to of the repository for read/write access."""
        return self._url('ssh')
    
    @property  
    def git(self):
        """Git url of the repository for read access."""
        return self._url('git')
    
    @property  
    def http(self):
        """Url to project home page."""
        return self._url('http')
    
    @property
    def issue(self):
        """Url to issue tracker"""
        return self._url('issue')
    
    @property
    def gh_pages(self):
        """Url for the project's gh-pages."""
        return self._url('gh_pages')
        
    def _url(self, protocol='ssh'):
        if self.project.name is None:
            raise AttributeError('Project name not defined')
        if self.project.owner is None:
            self.project.owner = Credentials.get_credentials().user
        if not self.project.owner:
            raise AttributeError(
                'The project owner or the github user need to be set.')
        return self._tmpls[protocol] % (self.project.owner, self.project.name)
        
    def __str__(self):
        return self.http


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
        remote_name='origin',
        master_branch='master'):
        """
        Create a repository on GitHub, push your local copy to it,
        and add a remote alias name for it to your local copy.
        
        :param project_name: Name of the repository to create at GitHub.
        :param credentials: GitHub API credentials, used to create
            a new GitHub repository.
        :param description: Repository description.
        :param is_public: Should the GitHub repository be public.
        :param remote_name: GitHub repository remote name for your local copy
            (default to "origin").
        :param master_branch: Name of the branch to push to GitHub
            (default to "master") 
        """
        if credentials is None:
            credentials = Credentials.get_credentials(self)
        project = GitHubProject.create(
           project_name, credentials=credentials,
           description=description, is_public=is_public)
        self.git.remote('add', remote_name, project.url.ssh)
        self.git.push(remote_name, master_branch)
        return project
        
    def add_gh_pages_submodule(self, gh_pages_path, remote_name='origin'):
        """
        Add the gh-pages submodule, as a root branch of the GitHub repository.
        
        :param gh_pages_path: Path to gh-pages submodule.
        :param remote_name: Remote name of the GitHub repository.
        """
        project_url = self.git.config('remote.%s.url' % remote_name).strip()
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
        gh_pages.git.push('origin', 'gh-pages')
        
        # update submodule
        self.git.add(gh_pages_path)
        self.git.commit('-m', 'update gh-pages submodule')
        
    def validate_gh_pages_submodule(self, gh_pages_path):
        module = self.submodules[gh_pages_path]
        gh_pages_repo = Repo(module.path)
        
        try:
            active_branch = gh_pages_repo.active_branch
        except GitCommandError:
            active_branch = 'no active branch'
        
        if active_branch != 'gh-pages':
            raise ValueError('"gh-pages" is not the current branch of the "%s" submodule.' % gh_pages_path)
        
        return module


class Submodule(object):
    """
    A repository submodule.
    
    Hold its details: the module path, its repository url, sha and status.
    """
        
    def __init__(self, repo, url, module_path, sha=None, status=None):
        self.repo = repo
        self.path = module_path.rstrip('/')
        self.url = url
        self.sha = sha
        self.status = status
        self.git = Git(self.path)
        
    def init(self, msg=None):
        if msg is None:
            msg = 'Add a submodule for "%s" at "%s' % (self.url, self.path,)
        if self.status in (None, '-'):
            self.repo.git.submodule('add', self.url, self.path)
            self.repo.git.submodule('init', self.path)
            self.repo.git.commit('-m', msg)
    
    def update(self):
        if self.status == '-':
            self.repo.git.submodule('init', self.path)
        self.repo.git.submodule('update', self.path)


class SubmoduleDict(dict):
    """
    List the submodules of a repository.
    
    The keys are submodules name (and path).
    """
    
    def __init__(self, repo):
        self.repo = repo
        self._get_submodules()
        
    def __getitem__(self, path):
        self._get_submodules()
        return super(SubmoduleDict, self).__getitem__(path.rstrip('/'))
    
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
            status = None
            sha = None
            if info:
                status = info[0]
                sha    = info[1:41]
            module = Submodule(self.repo, url, path, sha=sha, status=status)
            super(SubmoduleDict, self).__setitem__(
                module.path,
                module)


class GitmoduleReader(file):
    """
    Extends file to trim the start of each read line (with readline()).
    
    Used by SubmoduleDict to parse .gitmodule files. RawConfigParser doesn't seems
    to be able to parse those .gitmodule lines that start a tab.
    """
    def readline(self,*args, **kw):
        return file.readline(self,*args, **kw).lstrip()