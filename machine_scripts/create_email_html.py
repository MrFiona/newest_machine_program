#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-05-09 09:40
# Author  : MrFiona
# File    : create_email_html.py
# Software: PyCharm Community Edition

from __future__ import absolute_import

import os
import sys
import time

from machine_scripts.pyh import PyH, h1, table, td, tr

from machine_scripts.public_use_function import get_report_data, get_url_list_by_keyword, get_interface_config
from setting_global_variable import ORIGINAL_HTML_RESULT, MANUAL_ORIGINAL_HTML_RESULT

try:
  import cPickle as pickle
except ImportError:
  import pickle

reload(sys)
sys.setdefaultencoding('utf-8')

def create_save_miss_html(sheet_name, Silver_url_list, purl_bak_string, win_book, WEEK_NUM, logger,
                          predict_execute_flag=False, type_string='', keep_continuous='NO'):
    if sheet_name != 'Trend':
        if sheet_name == 'Save-Miss':
            page = PyH('excel结果html表格数据')
            page << h1(sheet_name + ' result')
            cell_data_list = get_report_data(sheet_name, win_book, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list, WEEK_NUM=WEEK_NUM
                                             ,type_string='' if type_string == '' else 'manual_', predict_execute_flag=predict_execute_flag, logger=logger,
                                             keep_continuous=keep_continuous)

            mytab = table(border="1", cellspacing="1px")
            for i in range(len(cell_data_list)):
                mytr = mytab << tr()
                for j in range(len(Silver_url_list) + 3):
                    if j == 0:
                        mytr << td(cell_data_list[i][j], style="width:60px")
                    else:
                        mytr << td(cell_data_list[i][j])
            page << mytab

        elif sheet_name in ('ExistingSi', 'NewSi'):
            page = PyH('excel结果html表格数据')
            page << h1(sheet_name + ' result')
            cell_data_list = get_report_data(sheet_name, win_book, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list, WEEK_NUM=WEEK_NUM
                                             ,type_string='' if type_string == '' else 'manual_', predict_execute_flag=predict_execute_flag, logger=logger,
                                             keep_continuous=keep_continuous)
            mytab = table(border="1", cellspacing="1px")

            for k in range(len(cell_data_list)):
                cell_data_list[k] = cell_data_list[k][2:]

            for i in range(len(cell_data_list)):
                mytr = mytab << tr()
                for j in range(len(cell_data_list[0])):
                    if j == 1:
                        mytr << td(cell_data_list[i][j], style="width:150px")
                    else:
                        mytr << td(cell_data_list[i][j])
            page << mytab

        else:
            page = PyH('excel结果html表格数据')
            page << h1(sheet_name + ' result')
            cell_data_list = get_report_data(sheet_name, win_book, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list, WEEK_NUM=WEEK_NUM
                                             , type_string='' if type_string == '' else 'manual_', predict_execute_flag=predict_execute_flag, logger=logger,
                                             keep_continuous=keep_continuous)
            mytab = table(border="1", cellspacing="1px")

            cell_data_list[0][2] = ''
            for i in range(len(cell_data_list)):
                mytr = mytab << tr()
                for j in range(len(cell_data_list[0])):
                    if i == 0 and j == 0:
                        mytr << td(cell_data_list[i][j], style="background-color:#D2691E;width:60px")
                    elif i == 0 and j == 1:
                        mytr << td(cell_data_list[i][j], style="font-size:30px;color:#00008B;background-color:#FFDEAD;width:50px")
                    elif i == 0 and j == 2:
                        mytr << td(cell_data_list[i][j], style="background-color:#FFDEAD;width:50px")
                    elif i == 0 and j == 3:
                        mytr << td(cell_data_list[i][j], style="background-color:#FFDEAD;width:120px")
                    elif i == 1 and j != 0:
                        mytr << td(cell_data_list[i][j], style="font-weight:bold")
                    elif j == 0 and cell_data_list[i][j] == True:
                        mytr << td(cell_data_list[i][j], style="background-color:#FFB6C1;color:#800000")
                    elif (j == 0 and cell_data_list[i][j] == False) or (i == 1 and j == 0):
                        mytr << td(cell_data_list[i][j])
                    else:
                        mytr << td(cell_data_list[i][j], style="background-color:#FFDEAD")
            page << mytab

        if type_string == '':
            original_html_result_dir = ORIGINAL_HTML_RESULT
        else:
            original_html_result_dir = MANUAL_ORIGINAL_HTML_RESULT

        if not os.path.exists(original_html_result_dir):
            os.makedirs(original_html_result_dir)

        page.printOut(original_html_result_dir + os.sep + purl_bak_string + '_' + sheet_name + '_html_data.html')

    else:
        get_report_data(sheet_name, win_book, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list, WEEK_NUM=WEEK_NUM
                        , type_string='' if type_string == '' else 'manual_', predict_execute_flag=predict_execute_flag, logger=logger,
                        keep_continuous=keep_continuous)



if __name__ == '__main__':
    start = time.time()
    from machine_scripts.public_use_function import easyExcel
    win_book = easyExcel(r'C:\Users\pengzh5x\Desktop\python_scripts\backup_dir\backup_excel_2017_05_31_13_14_22\Bakerville_100_report_result_2017_05_31_13_11_03.xlsx')
    # create_save_miss_html(sheet_name='ExistingSi', Silver_url_list=Silver_url_list, purl_bak_string=PURL_BAK_STRING)
    # TODO 类型: Bakerville or Purley-FPGA
    purl_bak_string = get_interface_config('default_purl_bak_string', 'PURL_BAK_STRING')
    Silver_url_list = get_url_list_by_keyword(purl_bak_string, 'Silver')
    create_save_miss_html(sheet_name='Trend', win_book=win_book, Silver_url_list=Silver_url_list, purl_bak_string=purl_bak_string)
    # create_save_miss_html(sheet_name='Save-Miss', Silver_url_list=Silver_url_list, purl_bak_string=purl_bak_string)
    print time.time() - start

