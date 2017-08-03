#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-08-03 14:19
# Author  : MrFiona
# File    : common_interface_branch_func.py
# Software: PyCharm Community Edition



def analysis_url_address_string(original_url_list):
    result_url_sep_list = []
    for url in original_url_list:
        url_split_string = str(url).split('/')[-2]
        week_string = url_split_string[-4:]
        year_string = url_split_string.split('%')[0]
        object_string = ''.join([year_string, week_string])
        result_url_sep_list.append(object_string)

    return result_url_sep_list