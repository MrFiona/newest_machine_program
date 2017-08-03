#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-05-09 10:57
# Author  : MrFiona
# File    : setting_gloab_variable.py
# Software: PyCharm Community Edition

import os

DO_PROF = True
MACHINE_LOG_DIR = os.getcwd() + os.sep + 'Log'
SRC_CACHE_DIR = os.getcwd() + os.sep + 'cache'
SRC_EXCEL_DIR = os.getcwd() + os.sep + 'excel_dir'
REPORT_HTML_DIR = os.getcwd() + os.sep + 'report_html'
BACKUP_EXCEL_DIR = os.getcwd() + os.sep + 'backup_excel'
BACKUP_CACHE_DIR = os.getcwd() + os.sep + 'backup_cache'
ORIGINAL_HTML_RESULT = os.getcwd() + os.sep + 'html_result'
MANUAL_ORIGINAL_HTML_RESULT = os.getcwd() + os.sep + 'manual_html_result'
SRC_WEEK_DIR = os.getcwd() + os.sep + 'choose_week_info_dir'
PRESERVE_TABLE_CHART_DIR = os.getcwd() + os.sep + 'preserve_table_chart'
BACKUP_PRESERVE_TABLE_CHART_DIR = os.getcwd() + os.sep + 'backup_preserve_table_chart'
SRC_SAVE_MISS_WEEK_DIR = os.getcwd() + os.sep + 'actually_week_info_dir'
IMAGE_ORIGINAL_RESULT = os.getcwd() + os.sep + 'image_original_result'
MANUAL_SRC_SAVE_MISS_WEEK_DIR = os.getcwd() + os.sep + 'manual_actually_week_info_dir'
MANUAL_IMAGE_ORIGINAL_RESULT = os.getcwd() + os.sep + 'manual_image_original_result'

DEBUG_FLAG=True

CONFIG_FILE_PATH = os.getcwd() + os.sep + 'machineConfig' + os.sep + 'machine.conf'
MANUAL_CONFIG_FILE_PATH = os.getcwd() + os.sep + 'machineConfig' + os.sep + 'manual_machine.conf'

type_sheet_name_list = ['Save-Miss', 'NewSi', 'ExistingSi', 'CaseResult', 'Trend']
type_sheet_name_list.sort(reverse=True)

PROGRAM_NAME_ID_DICT = {'Bakerville':'17', 'Purley-FPGA':'16', 'NFVi':'25'}