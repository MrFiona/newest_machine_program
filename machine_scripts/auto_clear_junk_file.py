#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-07-24 08:34
# Author  : MrFiona
# File    : auto_clear_junk_file.py
# Software: PyCharm Community Edition


import os
import glob

pwd_file_list = glob.glob(os.getcwd() + os.sep + '*.pyc')
parent_path = os.path.split(os.getcwd())[0]
parent_file_list = glob.glob(parent_path + os.sep + '*.pyc')
pwd_file_list.extend(parent_file_list)
for name in pwd_file_list:
    os.remove(name)