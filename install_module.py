#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-25 16:07
# Author  : MrFiona
# File    : install_module.py
# Software: PyCharm Community Edition


"""

    只有第一次使用machine_model_entrance.py或者manual_mode_entrance.py脚本的时候才执行此文件

"""


import os

# TODO requirements.txt如果不在当前目录则上一级目录取文件
def install_module():
    if 'requirements.txt' in os.listdir(os.getcwd()):
        cmd_1_status = os.system('pip --proxy child-prc.intel.com:913 install -r requirements.txt')
    else:
        cmd_1_status = os.system('pip --proxy child-prc.intel.com:913 install -r ../requirements.txt')

    if cmd_1_status:
        if 'requirements.txt' in os.listdir(os.getcwd()):
            cmd_status = os.system('pip install -r requirements.txt')
        else:
            cmd_status = os.system('pip install -r ../requirements.txt')

        if cmd_status:
            if 'requirements.txt' not in os.listdir(os.getcwd()):
                print 'There is a lack of module installation file requirements.txt in the current directory'
            else:
                print 'The module is not installed in the offline state'


if __name__ == '__main__':
    install_module()