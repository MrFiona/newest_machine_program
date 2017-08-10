#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-25 16:07
# Author  : MrFiona
# File    : install_module.py
# Software: PyCharm Community Edition

import os

def install_module():
    cmd_1_status = os.system('pip --proxy child-prc.intel.com:913 install -r requirements.txt')
    if cmd_1_status:
        cmd_status = os.system('pip install -r requirements.txt')
        if cmd_status:
            if 'requirements.txt' not in os.listdir(os.getcwd()):
                print 'There is a lack of module installation file requirements.txt in the current directory'
            else:
                print 'The module is not installed in the offline state'


if __name__ == '__main__':
    install_module()