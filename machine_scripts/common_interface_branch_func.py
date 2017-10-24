#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-08-03 14:19
# Author  : MrFiona
# File    : common_interface_branch_func.py
# Software: PyCharm Community Edition


import os
import traceback

_file_name = os.path.split(__file__)[1]


def analysis_url_address_string(original_url_list):
    result_url_sep_list = []
    for url in original_url_list:
        url_split_string = str(url).split('/')[-2]
        week_string = url_split_string[-4:]
        year_string = url_split_string.split('%')[0]
        object_string = ''.join([year_string, week_string])
        result_url_sep_list.append(object_string)

    return result_url_sep_list

#todo 括号分离合并处理
def extract_sw_data_deal_bracket(pending_deal_list):
    #todo 括号分离合并处理
    separate_temp_list = []
    left_index_exist_flag = False
    right_index_exist_flag = False
    left_index, right_index = 0, -1
    if '(' in pending_deal_list:
        for temp_ele in pending_deal_list:
            if temp_ele.startswith('('):
                left_index = pending_deal_list.index(temp_ele)
                left_index_exist_flag = True
            if temp_ele.endswith(')'):
                right_index = pending_deal_list.index(temp_ele)
                right_index_exist_flag = True

    if left_index_exist_flag and right_index_exist_flag:
        to_deal_ele_list = pending_deal_list[left_index:right_index + 1]
        if to_deal_ele_list:
            separate_temp_list.extend(pending_deal_list[:left_index])
            separate_temp_list.append(''.join(to_deal_ele_list))
            separate_temp_list.extend(pending_deal_list[right_index + 1:])
        if separate_temp_list:
            return separate_temp_list
    else:
        return pending_deal_list


#todo 获取项目前缀
def obtain_prefix_project_name(project_name):
    #TODO classify 项目配置前缀
    if project_name == 'Purley-FPGA':
        project_string_sep = 'FPGA'
    elif project_name == 'Bakerville':
        project_string_sep = 'Bak'
    elif project_name == 'Purley-Crystal-Ridge':
        project_string_sep = 'Purley-Crystal-Ridge'
    else:
        project_string_sep = 'NFV'

    return project_string_sep


#todo 错误异常信息
def traceback_print_info(logger):
    logger.print_message('Error#####################################################Error', _file_name, 50)
    logger.print_message('traceback.format_exc():\n%s' % traceback.format_exc(), _file_name, 50)
    logger.print_message('Error#####################################################Error', _file_name, 50)
