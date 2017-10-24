#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
        开发出一个日志系统，既要把日志输出到控制台，还要写入日志文件
        CRITICAL = 50
        FATAL = CRITICAL
        ERROR = 40
        WARNING = 30
        WARN = WARNING
        INFO = 20
        DEBUG = 10
        NOTSET = 0
"""

import os
import os.path
import logging
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
from setting_global_variable import MACHINE_LOG_DIR


class WorkLogger(object):
    #TODO 新增日志输出标记 create_log_flag  True: 输出 False: 不输出 default: True
    def __init__(self, log_filename=None, log_level=INFO, log_time=None, create_log_flag=True):
        self.log_filename = log_filename
        self.log_level = log_level
        self.create_log_flag = create_log_flag

        if create_log_flag:
            self.log_time = log_time
            self.log_name = self.log_filename + '_' + self.log_time + '.txt'

        if not os.path.isdir(MACHINE_LOG_DIR):
            os.mkdir(MACHINE_LOG_DIR)

        if create_log_flag:
            self.write_file = open(MACHINE_LOG_DIR + os.sep + self.log_name, 'a+')

    def print_message(self, msg='', logger_name=None, definition_log_level=INFO):
        self.log_level = definition_log_level
        #todo 创建一个logger以及设置日志级别
        self.work_logger = logging.getLogger(self.log_filename)
        self.work_logger.setLevel(DEBUG)

        #todo 创建控制端输出handler，用于输出到控制端并设置输出日志级别
        console_handler = logging.StreamHandler()
        console_handler.setLevel(DEBUG)

        #todo 定义handler的输出格式并将格式应用到handler
        formatter = logging.Formatter('%(asctime)s | %(filename)s | %(lineno)d | %(levelname)s | %(message)s')
        console_handler.setFormatter(formatter)

        #todo 将handler加入到logger
        self.work_logger.addHandler(console_handler)

        #todo 根据日志级别打印信息
        if self.log_level == DEBUG or self.log_level == NOTSET:
            self.work_logger.debug(msg)
            level = 'DEBUG'
        elif self.log_level == INFO:
            self.work_logger.info(msg)
            level = 'INFO'
        elif self.log_level == WARNING:
            self.work_logger.warning(msg)
            level = 'WARNING'
        elif self.log_level == ERROR:
            self.work_logger.error(msg)
            level = 'ERROR'
        elif self.log_level == CRITICAL:
            self.work_logger.critical(msg)
            level = 'CRITICAL'
        else:
            raise ValueError("Log level parameter is incorrect:\t[ %d ]" %(self.log_level))

        if self.create_log_flag:
            self.write_file.write(' | '.join([self.log_time, logger_name, level, msg]) + '\n')

        #todo 将handler从logger中移除
        self.work_logger.removeHandler(console_handler)

    def file_close(self):
        self.write_file.close()

    def return_log_file(self):
        return self.log_name


if __name__ == '__main__':
    _logger =  WorkLogger('Test Log', 20)
    _logger.print_message(msg='Hello！This is a test message', logger_name='test_custom_log')