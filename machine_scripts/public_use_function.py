#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-25 14:55
# Author  : MrFiona
# File    : public_use_function.py
# Software: PyCharm Community Edition

from __future__ import absolute_import


import re
import os
import sys
import glob
import time
import shutil
import traceback
import functools
import win32com.client
from logging import ERROR
from machine_scripts.machine_config import MachineConfig
from setting_global_variable import (CONFIG_FILE_PATH, MANUAL_SRC_SAVE_MISS_WEEK_DIR,
    REPORT_HTML_DIR, SRC_SAVE_MISS_WEEK_DIR, IMAGE_ORIGINAL_RESULT, MACHINE_LOG_DIR,
    MANUAL_IMAGE_ORIGINAL_RESULT, ORIGINAL_HTML_RESULT, MANUAL_ORIGINAL_HTML_RESULT, SRC_WEEK_DIR)

_file_name = os.path.split(__file__)[1]


# TODO 获取配置参数信息
def get_interface_config(para_name, purl_bak_string):
    # TODO classify 项目配置前缀
    if purl_bak_string == 'Purley-FPGA':
        string_sep = 'FPGA'
    elif purl_bak_string == 'Bakerville':
        string_sep = 'Bak'
    else:
        string_sep = 'NFV'

    # TODO 读取配置参数值
    conf = MachineConfig(CONFIG_FILE_PATH)
    if para_name == 'default_server_address':
        SERVER_ADDRESS = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                            'default_server_address')
        return SERVER_ADDRESS
    elif para_name == 'default_send_address':
        SEND_ADDRESS = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                          'default_send_address')
        return SEND_ADDRESS
    elif para_name == 'default_receive_address':
        RECEIVE_ADDRESS = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                             'default_receive_address')
        return RECEIVE_ADDRESS
    elif para_name == 'default_choose_week_num':
        CHOOSE_WEEK_NUM = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                             'default_choose_week_num')
        return CHOOSE_WEEK_NUM

    elif para_name == 'default_reacquire_data_flag':
        REACQUIRE_DATA_FLAG = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                                 'default_reacquire_data_flag')
        return REACQUIRE_DATA_FLAG
    elif para_name == 'default_verify_file_flag':
        VERIFY_FILE_FLAG = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                              'default_verify_file_flag')
        return VERIFY_FILE_FLAG
    elif para_name == 'default_max_waiting_time':
        MAX_WAITING_TIME = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                              'default_max_waiting_time')
        return MAX_WAITING_TIME
    elif para_name == 'default_purl_bak_string':
        PURL_BAK_STRING = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')
        return PURL_BAK_STRING
    elif para_name == 'default_get_default_flag':
        GET_DEFAULT_FLAG = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                              'default_get_default_flag')
        return GET_DEFAULT_FLAG
    elif para_name == 'default_on_off_line_save_flag':
        ON_OFF_LINE_SAVE_FLAG = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                                   'default_on_off_line_save_flag')
        return ON_OFF_LINE_SAVE_FLAG
    elif para_name == 'default_send_email_flag':
        DEFAULT_SEND_EMAIL = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                                'default_send_email_flag')
        return DEFAULT_SEND_EMAIL
    elif para_name == 'default_keep_continuous':
        DEFAULT_KEEP_CONTINOUS = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value',
                                                    'default_keep_continuous')
        return DEFAULT_KEEP_CONTINOUS

    elif para_name == 'server_address':
        server_address = conf.get_node_info(string_sep + '_server', 'server_address')
        return server_address
    elif para_name == 'from_address':
        from_address = conf.get_node_info(string_sep + '_from_address', 'from_address')
        return from_address
    elif para_name == 'receive_address':
        receive_address = conf.get_node_info(string_sep + '_receive_address', 'receive_address')
        return receive_address

    elif para_name == 'week_num':
        week_num = conf.get_node_info(string_sep + '_other_config', 'week_num')
        return week_num
    elif para_name == 'reacquire_data_flag':
        reacquire_data_flag = conf.get_node_info(string_sep + '_other_config', 'reacquire_data_flag')
        return reacquire_data_flag
    elif para_name == 'verify_file_flag':
        verify_file_flag = conf.get_node_info(string_sep + '_other_config', 'verify_file_flag')
        return verify_file_flag
    elif para_name == 'max_waiting_time':
        max_waiting_time = conf.get_node_info(string_sep + '_other_config', 'max_waiting_time')
        return max_waiting_time
    elif para_name == 'on_off_line_save_flag':
        on_off_line_save_flag = conf.get_node_info(string_sep + '_other_config', 'on_off_line_save_flag')
        return on_off_line_save_flag
    elif para_name == 'send_email_flag':
        send_email_flag = conf.get_node_info(string_sep + '_other_config', 'send_email_flag')
        return send_email_flag
    elif para_name == 'keep_continuous':
        keep_continuous = conf.get_node_info(string_sep + '_other_config', 'keep_continuous')
        return keep_continuous

    elif para_name == 'display_software':
        display_software = conf.get_node_info(string_sep + '_other_config', 'display_software')
        return display_software
    elif para_name == 'display_new':
        display_New = conf.get_node_info(string_sep + '_other_config', 'display_New')
        return display_New
    elif para_name == 'display_existing':
        display_Existing = conf.get_node_info(string_sep + '_other_config', 'display_Existing')
        return display_Existing
    elif para_name == 'display_closed':
        display_Closed = conf.get_node_info(string_sep + '_other_config', 'display_Closed')
        return display_Closed
    elif para_name == 'display_total':
        display_Total = conf.get_node_info(string_sep + '_other_config', 'display_Total')
        return display_Total
    elif para_name == 'display_save_test':
        display_save_test = conf.get_node_info(string_sep + '_other_config', 'display_save_test')
        return display_save_test
    elif para_name == 'display_save_effort':
        display_save_effort = conf.get_node_info(string_sep + '_other_config', 'display_save_effort')
        return display_save_effort
    elif para_name == 'display_miss':
        display_miss = conf.get_node_info(string_sep + '_other_config', 'display_miss')
        return display_miss
    elif para_name == 'template_file':
        template_file = conf.get_node_info(string_sep + '_other_config', 'template_file')
        return template_file
    else:
        raise UserWarning('Can not get the value corresponding to parameter [ %s ]' % para_name)


# TODO 根据是否加载默认配置----获取配置参数信息
def judge_get_config(name, purl_bak_string):
    get_default_flag = get_interface_config('default_get_default_flag', purl_bak_string)
    if name == 'week_num':
        # TODO 周数控制参数
        if get_default_flag == 'YES':
            week_num = get_interface_config('week_num', purl_bak_string)
        else:
            week_num = get_interface_config('default_choose_week_num', purl_bak_string)
        return week_num

    elif name == 'reacquire_data_flag':
        # TODO 是否重新获取数据标记  开启:YES   关闭:NO
        if get_default_flag == 'YES':
            reacquire_data_flag = get_interface_config('reacquire_data_flag', purl_bak_string)
        else:
            reacquire_data_flag = get_interface_config('default_reacquire_data_flag', purl_bak_string)
        return reacquire_data_flag

    elif name == 'verify_file_flag':
        # TODO 是否验证excel  开启:YES   关闭:NO
        if get_default_flag == 'YES':
            verify_file_flag = get_interface_config('verify_file_flag', purl_bak_string)
        else:
            verify_file_flag = get_interface_config('default_verify_file_flag', purl_bak_string)
        return verify_file_flag

    elif name == 'max_waiting_time':
        # TODO 打开execl文件的最长等待时间   单位: min
        if get_default_flag == 'YES':
            max_waiting_time = get_interface_config('max_waiting_time', purl_bak_string)
        else:
            max_waiting_time = get_interface_config('default_max_waiting_time', purl_bak_string)

        max_time = max_waiting_time.strip('min')
        return max_time

    elif name == 'on_off_line_save_flag':
        # TODO 是否验证excel  开启:YES   关闭:NO
        if get_default_flag == 'YES':
            on_off_line_save_flag = get_interface_config('on_off_line_save_flag', purl_bak_string)
        else:
            on_off_line_save_flag = get_interface_config('default_on_off_line_save_flag', purl_bak_string)
        return on_off_line_save_flag

    elif name == 'send_email_flag':
        # TODO 是否发送邮件  开启:YES   关闭:NO
        if get_default_flag == 'YES':
            send_email_flag = get_interface_config('send_email_flag', purl_bak_string)
        else:
            send_email_flag = get_interface_config('default_send_email_flag', purl_bak_string)
        return send_email_flag

    elif name == 'keep_continuous':
        # TODO 是否配置周数  开启:YES   关闭:NO
        if get_default_flag == 'YES':
            keep_continuous = get_interface_config('keep_continuous', purl_bak_string)
        else:
            keep_continuous = get_interface_config('default_keep_continuous', purl_bak_string)
        return keep_continuous

    elif name == 'server_address':
        # TODO 服务器地址
        if get_default_flag == 'YES':
            server_address = get_interface_config('server_address', purl_bak_string)
        else:
            server_address = get_interface_config('default_server_address', purl_bak_string)
        return server_address

    elif name == 'from_address':
        # TODO 发件人地址
        if get_default_flag == 'YES':
            from_address = get_interface_config('from_address', purl_bak_string)
        else:
            from_address = get_interface_config('default_send_address', purl_bak_string)
        return from_address

    elif name == 'receive_address':
        # TODO 收件人地址
        if get_default_flag == 'YES':
            receive_address = get_interface_config('receive_address', purl_bak_string)
        else:
            receive_address = get_interface_config('default_receive_address', purl_bak_string)
        return receive_address


# TODO 根据关键词获取url链接
def get_url_list_by_keyword(purl_bak_string, back_keyword, key_url_list=None, reserve_url_num=100, pre_url_list=None):
    if not key_url_list:
        key_url_list = []

    with open(REPORT_HTML_DIR + os.sep + purl_bak_string + '_url_info.txt', 'r') as f:
        for line in f:
            if not pre_url_list:
                if purl_bak_string in line and back_keyword in line:
                    key_url_list.append(line.strip('\n'))
            else:
                compare_url_string = line.strip('\n').split('/')[-2]
                if purl_bak_string in line and back_keyword in line and compare_url_string + '/' in pre_url_list:
                    key_url_list.append(line.strip('\n'))
        # todo 在选择周的时候返回的包含三种类型的url 此时reserve_url_num失效
        if not pre_url_list:
            key_url_list = key_url_list[:reserve_url_num]
    return key_url_list


# TODO 移除特定字符串
def remove_line_break(object_string_list, line_break=False, empty_string=False, blank_string=False,
                      first_method=True, second_method=False):
    if first_method:
        if line_break:
            try:
                while 1:
                    object_string_list.remove('\n')
            except ValueError:
                pass

        if empty_string:
            try:
                while 1:
                    object_string_list.remove('')
            except ValueError:
                pass

        if blank_string:
            try:
                while 1:
                    object_string_list.remove(' ')
            except ValueError:
                pass

    # TODO 第二种处理方法
    elif second_method:
        # TODO 改成元祖表达式又会比列表表达式快两倍
        if line_break:
            object_string_list = (ele for ele in object_string_list if ele != '\n')
        if empty_string:
            object_string_list = (ele for ele in object_string_list if ele != '')
        if blank_string:
            object_string_list = (ele for ele in object_string_list if ele != ' ')

    return object_string_list


# TODO 封装win32com.client的某些功能
class easyExcel(object):
    def __init__(self, filename=None):  # 打开文件或者新建文件（如果不存在的话）
        # TODO 开启新的进程打开Excel
        self.xlApp = win32com.client.DispatchEx('Excel.Application')
        self.xlApp.Visible = 0

        if filename:
            self.filename = filename
            self.xlBook = self.xlApp.Workbooks.Open(filename)
        else:
            self.xlBook = self.xlApp.Workbooks.Add()
            self.filename = ''

    def save(self, newfilename=None):  # 保存文件
        if newfilename:
            self.filename = newfilename
            self.xlBook.SaveAs(newfilename)
        else:
            self.xlBook.Save()

    def close(self):  # 关闭文件
        self.xlBook.Close(SaveChanges=0)
        del self.xlApp

    def getCell(self, sheet, row, col):  # 获取单元格的数据
        "Get value of one cell"
        sht = self.xlBook.Worksheets(sheet)
        # range_value = sht.Range('A1:CO10')
        # print range_value
        return sht.Cells(row, col).Value

    def setCell(self, sheet, row, col, value):  # 设置单元格的数据
        "set value of one cell"
        sht = self.xlBook.Worksheets(sheet)
        # sht.Cells(row, col).Value = value
        # sht.Cells(row, col).Font.Size = 15  # 字体大小
        # sht.Cells(row, col).Font.Bold = True  # 是否黑体
        # sht.Cells(row, col).Name = "Arial"  # 字体类型
        sht.Cells(row, col).Interior.ColorIndex = 2  # 表格背景
        # sht.Range("A1").Borders.LineStyle = xlDouble
        sht.Cells(row, col).BorderAround(1, 3)  # 表格边框
        # sht.Rows(3).RowHeight = 30  # 行高
        # sht.Cells(row, col).HorizontalAlignment = -4131  # 水平居中xlCenter
        # sht.Cells(row, col).VerticalAlignment = -4160  #

    def deleteRow(self, sheet, row):
        sht = self.xlBook.Worksheets(sheet)
        sht.Rows(row).Delete()  # 删除行
        sht.Columns(row).Delete()  # 删除列

    def getRange(self, sheet, row1, col1, row2, col2):  # 获得一块区域的数据，返回为一个二维元组
        "return a 2d array (i.e. tuple of tuples)"
        sht = self.xlBook.Worksheets(sheet)
        return sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value

    def addPicture(self, sheet, pictureName, Left, Top, Width, Height):  # 插入图片
        "Insert a picture in sheet"
        sht = self.xlBook.Worksheets(sheet)
        sht.Shapes.AddPicture(pictureName, 1, 1, Left, Top, Width, Height)

    def cpSheet(self, before):  # 复制工作表
        "copy sheet"
        shts = self.xlBook.Worksheets
        shts(1).Copy(None, shts(1))

    def inserRow(self, sheet, row):
        sht = self.xlBook.Worksheets(sheet)
        sht.Rows(row).Insert(1)


# TODO 读取Excel表数据----用于发邮件
def get_report_data(sheet_name, win_book, purl_bak_string, Silver_url_list, WEEK_NUM, logger, cell_data_list=None,
                    type_string='', predict_execute_flag=False, keep_continuous='NO'):
    '''
    :param sheet_name:
    :param win_book:
    :param purl_bak_string:
    :param Silver_url_list:
    :param WEEK_NUM:
    :param logger:
    :param cell_data_list:
    :param type_string: 识别manual和正常模式的字符串标记 manual_则manual模式，默认正常模式
    :param predict_execute_flag: True candidate数据位置需左移一周
    :param keep_continuous: 新加标记，选择周模式下发邮件以及产生html要与其对应 debug 2017-08-11 13:59
    :return:
    '''
    choose_week_newest_index = 0
    if sheet_name in ('NewSi', 'ExistingSi', 'CaseResult'):
        # TODO 在keep_continuous = YES选择周的情况下处理
        if keep_continuous == 'YES':
            with open(SRC_WEEK_DIR + os.sep + 'week_info.txt', 'r') as f:
                choose_week_string = f.readline()
                choose_week_list = choose_week_string.split(',')

            choose_compare_string = choose_week_list[0]
            temp_list = choose_compare_string.split('WW')
            temp_list[1] = '20WW' + temp_list[1]
            compare_week_string = '%'.join(temp_list)
            print 'compare_week_string:\t', compare_week_string

            for silver_url in Silver_url_list:
                if compare_week_string in silver_url:
                    choose_week_newest_index = Silver_url_list.index(silver_url)
                    print 'choose_week_newest_index:\t', choose_week_newest_index, sheet_name
    else:
        choose_week_newest_index = 0
        print 'choose_week_newest_index:\t', choose_week_newest_index, sheet_name

    if type_string == '':
        actually_week_info_dir = SRC_SAVE_MISS_WEEK_DIR
    else:
        actually_week_info_dir = MANUAL_SRC_SAVE_MISS_WEEK_DIR

    WEEK_NUM = int(WEEK_NUM)
    if cell_data_list is None:
        cell_data_list = []

    # TODO 新增对周数进行统计 方便定位最新周的位置 最新周从后往前算
    if sheet_name == 'Save-Miss':
        if predict_execute_flag:
            save_miss_left_location = WEEK_NUM + 3 - len(Silver_url_list) - 1
        else:
            save_miss_left_location = WEEK_NUM + 3 - len(Silver_url_list)
        logger.print_message('save_miss_left_location:\t%s' % save_miss_left_location, _file_name)

        for i in range(1, 8):
            temp_cell_list = []
            for j in range(1, 3):
                data = win_book.getCell(sheet=sheet_name, row=i, col=j)

                if i in (4, 5) and isinstance(data, float):
                    data = '%.2f%%' % (data * 100)
                elif i in (6, 7) and isinstance(data, float):
                    data = '%.2f' % (data)
                elif i == 2 and isinstance(data, float):
                    data = int(round(data))
                elif data is None:
                    data = ''
                temp_cell_list.append(data)

            for k in range(save_miss_left_location, WEEK_NUM + 4):
                data = win_book.getCell(sheet=sheet_name, row=i, col=k)
                if i in (1, 2, 6, 7) and isinstance(data, float):
                    data = int(round(data))
                elif i in (4, 5) and isinstance(data, float):
                    data = '%.f%%' % (data * 100)
                elif data is None:
                    data = ''

                temp_cell_list.append(data)
            cell_data_list.append(temp_cell_list)

        # TODO 统计实际周数存放指定文件 已与用户约定原始数据删除需要删除save-miss对应标记
        week_info_list = []
        for col in range(save_miss_left_location, WEEK_NUM + 3):
            week_data = win_book.getCell(sheet=sheet_name, row=3, col=col)
            week_compile = re.compile('\d+WW\d+')
            if re.match(week_compile, str(week_data)):
                week_info_list.append(str(week_data))

        if not os.path.exists(actually_week_info_dir):
            os.makedirs(actually_week_info_dir)

        with open(actually_week_info_dir + os.sep + 'actually_week_info.txt', 'w') as f:
            f.write(' '.join(week_info_list))

    elif sheet_name in ('NewSi', 'ExistingSi'):
        stop_flag = False
        # TODO 有candidate的情况下以candidate为准
        if predict_execute_flag:
            new_exist_left_location = (WEEK_NUM - len(Silver_url_list) + 1 - 1) * 13
        # TODO 无candidate而自定义选择了周则按照选择周为准
        elif not predict_execute_flag and keep_continuous == 'YES':
            new_exist_left_location = (WEEK_NUM - len(Silver_url_list) + 1 + choose_week_newest_index) * 13
        else:
            new_exist_left_location = (WEEK_NUM - len(Silver_url_list) + 1) * 13
        logger.print_message('new_exist_left_location:\t%s' % new_exist_left_location, _file_name)

        for i in range(3, 200):
            temp_cell_list = []
            # NewSi和existingSi用上一周的
            for j in range(new_exist_left_location + 3, new_exist_left_location + 1 + 13):
                data = win_book.getCell(sheet=sheet_name, row=i, col=j)
                if j == (new_exist_left_location + 1 + 1) and not data:
                    stop_flag = True

                if data is None:
                    data = ''
                elif isinstance(data, float):
                    data = int(data)

                temp_cell_list.append(data)

            if stop_flag:
                break

            # 排除True和False
            # print temp_cell_list
            temp = [cell for cell in temp_cell_list[2:] if isinstance(cell, (unicode, str)) and len(cell) != 0]
            if not temp:
                continue
            cell_data_list.append(temp_cell_list)

    # TODO 为后续作图提供数据  修复bug 在选择部分周时出现无法提取数据 2017-07-03
    elif sheet_name == 'Trend':
        if predict_execute_flag:
            trend_right_location = len(Silver_url_list) + 2 + 1
        else:
            trend_right_location = len(Silver_url_list) + 2
        logger.print_message('trend_right_location:\t%s' % trend_right_location, _file_name)

        if type_string == '':
            write_file_dir = IMAGE_ORIGINAL_RESULT
        else:
            write_file_dir = MANUAL_IMAGE_ORIGINAL_RESULT

        if not os.path.exists(write_file_dir):
            os.makedirs(write_file_dir)
        write_file = open(write_file_dir + os.sep + purl_bak_string + '_image_data.txt', 'w')

        for i in range(1, trend_right_location):
            temp_cell_list = []
            for j in range(1, 11):
                data = win_book.getCell(sheet=sheet_name, row=i, col=j)
                if isinstance(data, float):
                    if 1 <= j < 8:
                        data = int(data)
                    else:
                        if data < 0.005:
                            data = '%.f%%' % (data * 0)
                        else:
                            data = '%.f%%' % (data * 100)

                temp_cell_list.append(str(data))

            write_data = '\t'.join(temp_cell_list)
            write_file.write(write_data + '\n')
            cell_data_list.append(temp_cell_list)
        write_file.close()
        logger.print_message('Trend cell_data_list:\t%s' % cell_data_list, _file_name)

    else:
        fstop_flag = False
        if predict_execute_flag:
            case_result_left_location = (WEEK_NUM - len(Silver_url_list) - 1) * 41 + 35 + 10 + 2
        # TODO 无candidate而自定义选择了周则按照选择周为准
        elif not predict_execute_flag and keep_continuous == 'YES':
            case_result_left_location = (WEEK_NUM - len(Silver_url_list) + choose_week_newest_index) * 41 + 35 + 10 + 2
        else:
            case_result_left_location = (WEEK_NUM - len(Silver_url_list)) * 41 + 35 + 10 + 2
        logger.print_message('case_result_left_location:\t%s' % case_result_left_location, _file_name)

        for i in range(7, 400):
            temp_cell_list = []
            for j in range(case_result_left_location, case_result_left_location + 4):
                data = win_book.getCell(sheet=sheet_name, row=i, col=j)
                if data is None:
                    data = ''
                if (j == case_result_left_location + 1) and data == '':
                    fstop_flag = True

                temp_cell_list.append(data)

            if fstop_flag:
                break
            # print temp_cell_list
            cell_data_list.append(temp_cell_list)

    # print 'sheet_name:\t', sheet_name
    # print cell_data_list
    return cell_data_list


# TODO 对html文件处理，增加表格样式
def deal_html_data(type_string):
    if type_string == '':
        original_html_result_dir = ORIGINAL_HTML_RESULT
    else:
        original_html_result_dir = MANUAL_ORIGINAL_HTML_RESULT

    read_file_list = glob.glob(original_html_result_dir + os.sep + '*.html')

    for file in read_file_list:
        read_file = open(file, 'r')
        write_file = open(original_html_result_dir + os.sep + 'temp.html', 'w')

        line = read_file.readline()
        write_file.write(line)
        while len(line) != 0:
            line = read_file.readline()
            if '</head>' == line.strip('\n'):
                if 'Save-Miss' in file:
                    write_file.write(
                        '<style type="text/css">\n\ttd{word-break:break-all;word-wrap:break-word;max-width:200px;font-family:Calibri;font-size:14px}\n</style>\n</head>\n')
                else:
                    write_file.write(
                        '<style type="text/css">\n\ttd{word-break:break-all;word-wrap:break-word;max-width:400px;font-family:Calibri;font-size:14px}\n</style>\n</head>\n')
                continue
            write_file.write(line)
        read_file.close()
        write_file.close()
        os.remove(file)
        shutil.copy(original_html_result_dir + os.sep + 'temp.html', file)
        os.remove(original_html_result_dir + os.sep + 'temp.html')


# TODO 构造栈装饰器 2017-06-14
def error_tracking_decorator(logger, module_name, log_time):
    """
    错误信息的详细定位
    :param func:
    :return:
    """

    def out_layer_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)

            except:
                f = sys._getframe()
                # print f, f.f_back, f.f_back.f_code
                filename = f.f_back.f_code.co_filename
                lineno = f.f_back.f_lineno
                max_sep_num = max(len('caller filename is' + str(filename)), len('caller filename is' + str(lineno)),
                                  len('the passed args is'
                                      + ' '.join([str(arg) for arg in args]) + ' '.join(str(kwargs.keys()))))
                logger.print_message('#' * (max_sep_num + 10), module_name, ERROR)
                logger.print_message('caller filename is %s' % filename, module_name, ERROR)
                logger.print_message('caller lineno is %d' % lineno, module_name, ERROR)
                logger.print_message('the passed args is {0}, {1}'.format(args, kwargs), module_name, ERROR)
                logger.print_message('#' * (max_sep_num + 10), module_name, ERROR)

                # time_str = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
                traceback.print_exc(
                    file=open(MACHINE_LOG_DIR + os.sep + log_time + '_trackback_log.txt', 'w'))
                exc_type, exc_value, exc_tb = sys.exc_info()
                max_sep_num = max(len('the exc type is:' + str(exc_type)), len('the exc value is:' + str(exc_value)),
                                  len('the exc tb is:' + str(exc_tb)))

                logger.print_message('*' * (max_sep_num + 4), module_name, ERROR)
                logger.print_message('the exc type is: %s' % exc_type, module_name, ERROR)
                logger.print_message('the exc value is: %s' % exc_value, module_name, ERROR)
                logger.print_message('the exc tb is: %s' % exc_tb, module_name, ERROR)
                logger.print_message('*' * (max_sep_num + 4), module_name, ERROR)

        return wrapper

    return out_layer_wrapper




if __name__ == '__main__':
    start = time.time()
    print time.time() - start