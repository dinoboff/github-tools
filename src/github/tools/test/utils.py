"""
Created on 19 Apr 2009

@author: damien
"""
from nose.tools import eq_, ok_

import tempfile

from paver.easy import path

__all__ = ['eq_', 'ok_', 'path', 'TempDir']

class TempDir(object):
    
    def __enter__(self):
        self.tmp_dir = path(tempfile.mkdtemp())
        return self.tmp_dir
        
    def __exit__(self, type, value, traceback):
        self.tmp_dir.rmtree()