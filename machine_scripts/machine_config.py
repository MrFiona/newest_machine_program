#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
        机器学习模型的操作配置文件模块
"""

import os
from ConfigParser import NoSectionError, RawConfigParser


class MachineConfig():
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

    def get_node_info(self, master_node=None, child_node=None):
        #todo 节点信息和配置文件路径不能为空
        if not master_node or not child_node:
            raise UserWarning('Please fill in the complete node parameter information!!!')
        if not self.config_file_path:
            raise UserWarning('Please specify the profile path!!!')

        conf = RawConfigParser()
        conf_status = conf.read(self.config_file_path)
        #todo 验证配置文件路径是否正确
        if conf_status:
            try:
                child_node_format = conf.get(master_node, child_node)

            except NoSectionError as e:
                raise UserWarning('Please check the machine.conf file,section[ %s ] '
                                  'is not exist!' % (e.section))
            except AttributeError:
                raise UserWarning('The profile node information is not found!!!')
        else:
            raise UserWarning('Please check that the configuration file path is correct!!!')

        return child_node_format

    def modify_node_value(self, master_node=None, child_node=None, value=''):
        #todo 节点信息和配置文件路径不能为空
        if not master_node or not child_node:
            raise UserWarning('Please fill in the complete node parameter information!!!')
        if not self.config_file_path:
            raise UserWarning('Please specify the profile path!!!')

        conf = RawConfigParser()
        conf_status = conf.read(self.config_file_path)
        #todo 验证配置文件路径是否正确
        if conf_status:
            try:
                conf.set(section=master_node, option=child_node, value=value)
                conf.write(open(self.config_file_path, 'w'))

            except NoSectionError as e:
                raise UserWarning('Please check the machine.conf file,section[ %s ] '
                                  'is not exist!' % (e.section))
            except AttributeError:
                raise UserWarning('The profile node information is not found!!!')
        else:
            raise UserWarning('Please check that the configuration file path is correct!!!')


if __name__ == '__main__':
    m = MachineConfig(os.getcwd() + os.sep + 'machineConfig' + os.sep + 'machine.conf')
    info = m.get_node_info('logFormat','time_format')
    m.modify_node_value('logFormat','time_format', 'default_test')
    print '__name__'
    print info