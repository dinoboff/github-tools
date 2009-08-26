"""
Created on 19 Apr 2009

@author: damien
"""
from __future__ import with_statement
from StringIO import StringIO
from ConfigParser import RawConfigParser
import os
import unittest
import cgi

from mock import patch, Mock

from github.tools.test.utils import eq_, ok_,TempDir, path
from github.tools.gh_pages import Credentials, GitHubRepo, GitHubProject,\
    GitmoduleReader, Submodule, Repo


class TestCredentials(unittest.TestCase):
    
    def test_new(self):
        c = Credentials(user='damien', token='xyz')
        eq_('damien', c.user)
        eq_('xyz', c.token)
        
    def test_get_credential(self):
        with TempDir() as tmp:
            repo = Repo.init_bare(path(tmp) / 'repo.git')
            repo.git.config('github.user', 'damien')
            repo.git.config('github.token', 'xyz')
            c = Credentials.get_credentials(repo)
            eq_('damien', c.user)
            eq_('xyz', c.token)


class TestProject(unittest.TestCase):
    GITHUB_JSON_RESPONSE = ('{"repository": '
        '{"description": "just a test", '
        '"name": "foo", "private": false, '
        '"url": "http://github.com/damien/foo", '
        '"watchers": 0, "forks": 0, "fork": false, '
        '"owner": "damien", "homepage": ""}}')
    
    def test_new(self):
        project = GitHubProject(
            name='foo',
            owner='damien',
            description='just a test',
            is_public=True)
        
        eq_('foo', project.name)
        eq_('damien', project.owner)
        eq_('just a test' , project.description)
        eq_(True, project.is_public)
        eq_('http://github.com/damien/foo', str(project.url))
        eq_('http://github.com/damien/foo', project.url.http)
        eq_('git@github.com:damien/foo.git',project.url.ssh)
        eq_('git://github.com/damien/foo.git',project.url.git)
        eq_('http://github.com/damien/foo/issues',project.url.issue)

    def test_get_project_from_json(self):
        project = GitHubProject.get_project_from_json(
                StringIO(self.GITHUB_JSON_RESPONSE))
        eq_('foo', project.name)
        eq_('damien', project.owner)
        eq_('just a test' , project.description)
        eq_(True, project.is_public)
        eq_('git@github.com:damien/foo.git',project.url.ssh)
        
    @patch('urllib2.urlopen')
    def test_get_project(self, urlopen_mock):
        urlopen_mock.return_value = StringIO(self.GITHUB_JSON_RESPONSE)
        
        project = GitHubProject.get_project('foo', 'damien')
        urlopen_mock.assert_called_with('http://github.com/api/v2/json/repos/show/damien/foo')
        eq_('foo', project.name)
        eq_('damien', project.owner)
        eq_('just a test' , project.description)
        eq_(True, project.is_public)
        eq_('git@github.com:damien/foo.git',project.url.ssh)
    
    @patch('urllib2.urlopen')    
    def test_create(self, urlopen_mock):
        urlopen_mock.return_value = StringIO(self.GITHUB_JSON_RESPONSE)
        credentials = Credentials('damien', 'xyz')
        project = GitHubProject.create(
            'foo', credentials, description='just a test', is_public=True)
        
        # test request to github
        url, data = urlopen_mock.call_args[0]
        data_dict = dict(cgi.parse_qsl(data))
        eq_('http://github.com/api/v2/json/repos/create', url)
        eq_('foo', data_dict['name'])
        eq_('just a test', data_dict['description'])
        eq_('1', data_dict['public'])
        eq_('damien', data_dict['login'])
        eq_('xyz', data_dict['token'])
        
        # test returned project
        eq_('foo', project.name)
        eq_('damien', project.owner)
        eq_('just a test' , project.description)
        eq_(True, project.is_public)
        eq_('git@github.com:damien/foo.git',project.url.ssh)
        
        
class TestRepo(unittest.TestCase):
    
    def test_create(self):
        with TempDir() as tmp:
            repo = GitHubRepo.create(tmp)
            git_dir = tmp / '.git'
            ok_(git_dir.exists())
            eq_(str(git_dir), repo.path)
            
    def test_create_no_folder(self):
        with TempDir() as tmp:
            repo_path = tmp / 'no-folder'
            repo = GitHubRepo.create(repo_path, mk_dir=True)
            git_dir = repo_path / '.git'
            ok_(git_dir.exists())
            eq_(str(git_dir), repo.path)
            

class TestGitHubRepo():
    
    @patch('urllib2.urlopen')
    def test_register(self, urlopen_mock):
        urlopen_mock.return_value = \
            StringIO(TestProject.GITHUB_JSON_RESPONSE)
        with TempDir() as tmp:
            repo = GitHubRepo.create(tmp)
            git_mock = Mock()
            repo.git = git_mock
            credentials = Credentials('damien', 'xyz')
            repo.register(
                'foo', credentials=credentials,
                description='just a test', is_public=True)
            
            # test project creation 
            url, data = urlopen_mock.call_args[0]
            data_dict = dict(cgi.parse_qsl(data))
            eq_('http://github.com/api/v2/json/repos/create', url)
            eq_('foo', data_dict['name'])
            eq_('just a test', data_dict['description'])
            eq_('1', data_dict['public'])
            eq_('damien', data_dict['login'])
            eq_('xyz', data_dict['token'])
            
            # test remote added
            eq_(('add', 'origin', 'git@github.com:damien/foo.git'),
                git_mock.remote.call_args[0])
            eq_(('origin', 'master'), git_mock.push.call_args[0])
            
    def test_add_gh_pages_submodule(self):
        #assert False
        pass
        
        


class TestSubmodule(unittest.TestCase):
    
    def test_new(self):
        with TempDir() as tmp: 
            local_path = tmp / 'local-repo'
            local_repo  = Repo.create(local_path, mk_dir=True)
            module = Submodule(
                local_repo,
                'file://%s' % local_path,
                'test', sha='a'*40, status=' ')
            eq_('file://%s' % local_path, module.url)
            eq_('test', module.path)
            eq_('a'*40, module.sha)
            eq_(' ', module.status)

    def test_init(self):
        with TempDir() as tmp:
            remote_path = tmp / 'remote-repo'
            remote_repo = Repo.create(remote_path, mk_dir=True)
            with open(remote_path / 'test.txt', 'w') as f:
                f.write('testing...')
            remote_repo.git.add('test.txt')
            remote_repo.git.commit('-m', 'testing...')
            
            # set a local repository and add the module
            local_path = tmp / 'local-repo'
            local_repo = Repo.create(local_path, mk_dir=True)
            module = Submodule(local_repo,
                'file://%s' % remote_path, 'test')
            module.init('testing')
            ok_(os.path.exists(local_path / 'test/.git'))
            ok_(os.path.exists(local_path / 'test/test.txt'))
            ok_(os.path.exists(local_path / '.gitmodules'))
            
class TestSubmoduleDict(unittest.TestCase):
    
    def test_add(self):
        with TempDir() as tmp:
            # set a remote repository
            remote_path = tmp / 'remote-repo'
            remote_repo = Repo.create(remote_path, mk_dir=True)
            with open(remote_path / 'test.txt', 'w') as f:
                f.write('testing...')
            remote_repo.git.add('test.txt')
            remote_repo.git.commit('-m', 'testing...')
            
            # set a local repository and add the module
            local_path = tmp / 'local-repo'
            local_repo = Repo.create(local_path, mk_dir=True)
            eq_(0, len(local_repo.submodules))
            local_repo.submodules.add('file://%s' % remote_path, 'test')
            ok_(os.path.exists(local_path / 'test/.git'))
            ok_(os.path.exists(local_path / 'test/test.txt'))
            ok_(os.path.exists(local_path / '.gitmodules'))
            eq_(1, len(local_repo.submodules))
            eq_('file://%s' % remote_path, local_repo.submodules['test'].url)

class TestGitmoduleReader(unittest.TestCase):
    
    def test_readline(self):
        cfg_txt = (
            '[submodule "docs/build/html"]\n'
            '\tpath = docs/build/html\n'
            '\turl = git@github.com:damien/foo.git\n'
            )
        with TempDir() as tmp:
            cfg_path = os.path.join(tmp, 'config')
            with open(cfg_path, 'w') as f:
                f.write(cfg_txt)
            fp = GitmoduleReader(cfg_path)
            cfg = RawConfigParser()
            cfg.readfp(fp)
            section_name = 'submodule "docs/build/html"'
            eq_(section_name, cfg.sections()[0])
            eq_('docs/build/html', cfg.get(section_name, 'path'))
            eq_('git@github.com:damien/foo.git',
                cfg.get(section_name, 'url'))