#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-25 16:07
# Author  : MrFiona
# File    : install_module.py
# Software: PyCharm Community Edition

import os

def install_module():
    'requirements.txt' in os.listdir(os.getcwd()) and os.system('pip --proxy child-prc.intel.com:913 install -r requirements.txt')

if __name__ == '__main__':
    install_module()