"""
Created on 19 Apr 2009

@author: damien
"""
from __future__ import with_statement
import os

from github.tools.test.utils import eq_, TempDir
from github.tools.utils import Cwd

def test_set_pwd():
    with TempDir() as tmp_pwd:
        current_pwd = os.path.abspath(os.curdir)
        with Cwd(tmp_pwd):
            eq_(tmp_pwd, os.path.abspath(os.curdir))
        eq_(current_pwd, os.path.abspath(os.curdir))