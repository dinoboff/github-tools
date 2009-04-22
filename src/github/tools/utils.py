"""
Created on 19 Apr 2009

@author: damien
"""
import os


class Cwd(object):
    """
    Change and restore the current working directory.
    Implements the context manager interface to be used
    with the "with" statement::
    
        with Cwd('/some/path'):
            sh('ls -la')
    
    :param tmp_pwd: path to set the current working directory to
    """
    def __init__(self, tmp_pwd=None):
        self._old_pwd = os.path.abspath(os.curdir)
        self._tmp_pwd = tmp_pwd
    
    def __enter__(self):
        if self._tmp_pwd is not None:
            self.change(self._tmp_pwd)
        return self
    
    def __exit__(self, type, value, traceback):
        self.restore()
        
    def __str__(self):
        return os.path.abspath(os.curdir)
    
    def restore(self):
        """
        Reset the current working directory.
        """
        os.chdir(self._old_pwd)
        return self
        
    def change(self, tmp_pwd):
        """
        Change current working directory.
        
        :param tmp_pwd: path to set the current working directory to
        """
        os.chdir(os.path.abspath(tmp_pwd))
        return self