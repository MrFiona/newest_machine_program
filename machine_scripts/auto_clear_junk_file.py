#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-07-24 08:34
# Author  : MrFiona
# File    : auto_clear_junk_file.py
# Software: PyCharm Community Edition


import os
import glob


parent_path = os.path.split(os.getcwd())[0]
print 'parent_path:\t', parent_path
parent_pyc_file_list = glob.glob(parent_path + os.sep + '*.pyc')
print 'parent_pyc_file_list:\t', parent_pyc_file_list
pwd_pyc_file_list = glob.glob(parent_path + os.sep + 'machine_scripts' + os.sep + '*.pyc')
print 'pwd_pyc_file_list:\t', pwd_pyc_file_list
pwd_pyc_file_list.extend(parent_pyc_file_list)
for name in pwd_pyc_file_list:
    os.remove(name)


