#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-07-12 14:13
# Author  : MrFiona
# File    : manual_mode_entrance.py
# Software: PyCharm Community Edition

from __future__ import absolute_import


import os
import time
from logging import ERROR
# TODO 执行之前安装所需模块
from machine_scripts.install_module import install_module;install_module()
from machine_scripts.create_email_html import create_save_miss_html
from machine_scripts.custom_log import WorkLogger
from machine_scripts.get_all_html import GetUrlFromHtml
from machine_scripts.machine_config import MachineConfig
from machine_scripts.manual_machine_config_gui import manual_machine_config_gui_main
from machine_scripts.public_use_function import (easyExcel, get_url_list_by_keyword,
        error_tracking_decorator)
from machine_scripts.common_interface_func import performance_analysis_decorator
from machine_scripts.send_email import SendEmail
from machine_scripts.generate_chart import generate_chart
from setting_global_variable import type_sheet_name_list, MANUAL_CONFIG_FILE_PATH

log_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
_logger = WorkLogger(log_filename='manual_machine_log', log_time=log_time)
WIN_BOOK_CLOSE_FLAG = False
_file_name = os.path.split(__file__)[1]
LOGGER_CLOSE_FLAG = False


# TODO 生成html文件
def manual_create_email_html(win_book, purl_bak_string, all_Silver_url_list):
    start = time.time()
    Silver_url_list = []
    for j in range(1, 104):
        data = win_book.getCell(sheet='Save-Miss', row=3, col=j)
        if data is not None and data != 'Average':
            Silver_url_list.append(data)
    _logger.print_message('Silver_url_list:\t%s\t%d' % (Silver_url_list, len(Silver_url_list)), _file_name)
    conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
    week_info = conf.get_node_info('manual_machine_info', 'week_info')
    if week_info not in Silver_url_list:
        raise UserWarning('The selected week does not exist!!!')
    # TODO 手动场景
    if Silver_url_list:
        if week_info in all_Silver_url_list:
            newest_week_index = all_Silver_url_list.index(week_info)
            _logger.print_message('newest_week_index:\t%s' % newest_week_index, _file_name)
            Silver_url_list = all_Silver_url_list[newest_week_index:]

    _logger.print_message('Silver_url_list:\t%s\t%d' % (Silver_url_list, len(Silver_url_list)), _file_name)
    _logger.print_message('get week info time:\t%d' % (time.time() - start), _file_name)

    try:
        for type_name in type_sheet_name_list:
            create_save_miss_html(sheet_name=type_name, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list,
                                win_book=win_book, WEEK_NUM=100, type_string='manual_')
    except:
        global WIN_BOOK_CLOSE_FLAG
        WIN_BOOK_CLOSE_FLAG = True
        win_book.close()

    if not WIN_BOOK_CLOSE_FLAG:
        win_book.close()

    _logger.print_message('create html time:\t%d' % (time.time() - start), _file_name)


# TODO 手动执行模型主程序
@performance_analysis_decorator('manual_mkm_run.prof')
@error_tracking_decorator(_logger, _file_name, log_time)
def manual_machine_model_entrance():
    try:
        # TODO 界面参数配置
        manual_machine_config_gui_main()
        conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
        excel_file = conf.get_node_info('manual_machine_info', 'template_info')
        win_book = easyExcel(excel_file)
        pur_string_info = win_book.getCell(sheet='Save-Miss', row=1, col=1)
        purl_bak_string = pur_string_info.split()[-1]
        _logger.print_message('purl_bak_string:\t%s' % purl_bak_string, _file_name)

        object_get_html = GetUrlFromHtml(html_url_pre='https://dcg-oss.intel.com/ossreport/auto/', logger=_logger)
        object_get_html.get_all_type_data(purl_bak_string, get_only_department=True)
        all_Silver_url_list = get_url_list_by_keyword(purl_bak_string, 'Silver')
        for ele in range(len(all_Silver_url_list)):
            url_split_string = all_Silver_url_list[ele].split('/')[-2]
            week_string = url_split_string[-4:]
            year_string = url_split_string.split('%')[0]
            date_string = ''.join([year_string, week_string])
            all_Silver_url_list[ele] = date_string

        _logger.print_message('all_Silver_url_list:\t%s\t%d' % (all_Silver_url_list, len(all_Silver_url_list)), _file_name)

        # TODO 生成html文件
        manual_create_email_html(win_book, purl_bak_string, all_Silver_url_list)
        # TODO 发送邮件
        SendEmail(purl_bak_string, _logger, type_string='manual_')
        # TODO 生成图表
        generate_chart(purl_bak_string, log_time, _logger, 'manual_')
    except:
        _logger.print_message('occurred error', _file_name, ERROR)
        global LOGGER_CLOSE_FLAG
        LOGGER_CLOSE_FLAG = True
        _logger.file_close()

    if not LOGGER_CLOSE_FLAG:
        _logger.print_message('close normal', _file_name)
        _logger.file_close()




if __name__ == '__main__':
    manual_machine_model_entrance()