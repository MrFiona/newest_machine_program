#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-25 14:55
# Author  : MrFiona
# File    : public_use_function.py
# Software: PyCharm Community Edition

import re
import os
import sys
import copy
import glob
import time
import shutil
import pstats
import urllib2
import cProfile
import traceback
import functools
import HTMLParser
import win32com.client
import win32pdh, string, win32api
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
from machine_scripts.machine_config import MachineConfig
from setting_global_variable import DO_PROF, BACKUP_EXCEL_DIR, CONFIG_FILE_PATH, BACKUP_cache_DIR, \
    SRC_CACHE_DIR, MANUAL_CONFIG_FILE_PATH, MANUAL_SRC_SAVE_MISS_WEEK_DIR, REPORT_HTML_DIR, \
    SRC_SAVE_MISS_WEEK_DIR, IMAGE_ORIGINAL_RESULT, MANUAL_IMAGE_ORIGINAL_RESULT, ORIGINAL_HTML_RESULT, SRC_EXCEL_DIR, \
    MACHINE_LOG_DIR, PRESERVE_TABLE_CHART_DIR, BACKUP_PRESERVE_TABLE_CHART_DIR, MANUAL_ORIGINAL_HTML_RESULT


# TODO 获取手动执行配置参数
def get_manual_config_info(para_name):
    # TODO 读取配置参数值
    conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
    if para_name == 'week_info':
        week_info = conf.get_node_info('manual_machine_info', 'week_info')
        return week_info
    elif para_name == 'template_info':
        template_info = conf.get_node_info('manual_machine_info', 'template_info')
        return template_info


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
def get_url_list_by_keyword(pre_keyword, back_keyword, key_url_list=None, reserve_url_num=50, pre_url_list=None):
    if not key_url_list:
        key_url_list = []

    with open(REPORT_HTML_DIR + os.sep + 'url_info.txt', 'r') as f:
        for line in f:
            if not pre_url_list:
                if pre_keyword in line and back_keyword in line:
                    key_url_list.append(line.strip('\n'))
            else:
                compare_url_string = line.strip('\n').split('/')[-2]
                if pre_keyword in line and back_keyword in line and compare_url_string + '/' in pre_url_list:
                    key_url_list.append(line.strip('\n'))
        key_url_list = key_url_list[:reserve_url_num]
        if pre_url_list:
            pass
            # print 'key_url_list1:\t', key_url_list, len(key_url_list)
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


# TODO 验证url的有效性
def verify_validity_url(url, logger):
    file_name = os.path.split(__file__)[1]
    logger.print_message('Verifying url %s Start' % (url), file_name)
    try:
        response = urllib2.urlopen(url)
    # TODO HTTPError是URLError的子类，在产生URLError时也会触发产生HTTPError。因此需注意应该先处理HTTPError
    except urllib2.URLError, e:
        if hasattr(e, 'code'):  # stands for HTTPError
            logger.print_message(msg="find http error, writing... [ %s ]" % e.code, logger_name=file_name,
                                 definition_log_level=ERROR)
            return False
        elif hasattr(e, 'reason'):  # stands for URLError
            logger.print_message(msg="can not reach a server,writing... [ %s ]" % e.reason, logger_name=file_name,
                                 definition_log_level=ERROR)
            return False
        else:  # stands for unknown error
            logger.print_message(msg="unknown error, writing...", logger_name=file_name, definition_log_level=ERROR)
            return False
    else:
        # print "url is reachable!"
        # else 中不用再判断 response.code 是否等于200,若没有抛出异常，肯定返回200,直接关闭即可
        response.close()
        return True
    finally:
        logger.print_message('Verifying url %s End' % (url), os.path.split(__file__)[1])


# TODO 返回字母组合列表
def return_label_num_list(alp_label_list):
    # 写入多个周的数据
    for i in range(24):
        # i为偶数
        if i & 1 == 0:
            if i < 2:
                x = ['D', 'Q']
            elif i >= 2:
                prefix = chr(ord('A') + (i - 2) / 2)
                x = [prefix + 'D', prefix + 'Q']
        elif i & 1 == 1:
            if i < 3:
                x = ['Q', 'AD']
            elif i > 3:
                prefix_font = chr(ord('A') + (i - 3) / 2)
                prefix_behind = chr(ord('A') + (i - 3) / 2 + 1)
                x = [prefix_font + 'Q', prefix_behind + 'D']
            elif i == 3:
                x = ['AQ', 'BD']
        try:
            alp_label_list.append(x)
        except:
            pass


# TODO 返回字母组合序列表
def generate_column_alp_list():
    big_list = [];
    alp_label_list = [];
    effective_alp_list = []
    # 将首字母对转化为字母对列表,此处要用深拷贝
    first_alp = copy.deepcopy(alp_label_list)
    alp_pair_list = copy.deepcopy(alp_label_list)
    big_list.append(first_alp)
    # 循环执行10次，生成10个列对应的字母标记
    for nu in range(9):
        for label in range(len(alp_pair_list)):
            for i in range(len(alp_pair_list[label])):
                ele = alp_pair_list[label][i]
                if len(ele) == 1:
                    alp_pair_list[label][i] = chr(ord(alp_pair_list[label][i]) + 1)
                elif len(ele) == 2:
                    alp_pair_list[label][i] = alp_pair_list[label][i][0] + chr(ord(alp_pair_list[label][i][1]) + 1)
        # 深拷贝
        k = copy.deepcopy(alp_pair_list)
        big_list.append(k)

    # 每次新增空列表从后插值
    for i in range(24):
        effective_alp_list.append([])
        for alp in big_list:
            effective_alp_list[-1].append(alp[i])


# TODO 判断字母有效性并返回有效字母串
def translate_test(num_total):
    # print 'num_total: ', num_total
    integer_num_alp = num_total - 65
    if integer_num_alp >= 0:
        # print 'integer_num_alp: ', integer_num_alp
        thousand_bit_num = integer_num_alp / (26 ** 4)
        remainder_thousand_bit_num = integer_num_alp % (26 ** 4)
        hundred_bit_num = remainder_thousand_bit_num / (26 ** 3)
        remainder_hundred_bit_num = remainder_thousand_bit_num % (26 ** 3)
        ten_bit_num = remainder_hundred_bit_num / (26 ** 2)
        remainder_ten_bit_num = remainder_hundred_bit_num % (26 ** 2)
        bit_num = remainder_ten_bit_num / 26
        remainder_bit_num = remainder_ten_bit_num % 26
        if thousand_bit_num > 26:
            raise UserWarning('Only supported in the 456976 column range!!!')

        object_alp = (chr(ord('A') + thousand_bit_num - 1) if thousand_bit_num else '') + (
            chr(ord('A') + hundred_bit_num - 1) if hundred_bit_num else '') + \
                     (chr(ord('A') + ten_bit_num - 1) if ten_bit_num else '') + (
                         chr(ord('A') + bit_num - 1) if bit_num else '') + \
                     (chr(ord('A') + remainder_bit_num))
        return object_alp


# TODO 隐藏表列  sub_signal_width新增少隐藏多少周
def hidden_data_by_column(sheet_name, url_list, multiple, sub_signal_width):
    conf = MachineConfig(CONFIG_FILE_PATH)
    purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')
    hidden_length = int(judge_get_config('week_num', purl_bak_string)) - len(url_list) - sub_signal_width
    # hidden_length = 50 - len(url_list)
    sheet_name.set_column(0, multiple * hidden_length - 1, options={'hidden': True})


# TODO 性能分析装饰器
def performance_analysis_decorator(filename):
    """
    Decorator for function profiling.
    """

    def wrapper(func):
        def profiled_func(*args, **kwargs):
            # Flag for do profiling or not.
            if DO_PROF:
                profile = cProfile.Profile()
                profile.enable()
                result = func(*args, **kwargs)
                profile.disable()
                # Sort stat by internal time.
                sortby = "tottime"
                ps = pstats.Stats(profile).sort_stats(sortby)
                ps.dump_stats(filename)
            else:
                result = func(*args, **kwargs)
            return result

        return profiled_func

    return wrapper


# TODO 备份Excel文件----默认保留20个文件
def backup_excel_file(src_dir=SRC_EXCEL_DIR, backup_dir=BACKUP_EXCEL_DIR, reserve_file_max_num=20000, log_time=None,
                      link_WW_week_string=None, Silver_url_list=None):
    backup_name = backup_dir + os.sep + 'backup_excel_' + time.strftime('%Y_%m_%d_%H_%M_%S',
                                time.localtime(time.time()))
    # 原始备份目录不存在则跳过备份
    if not os.path.exists(src_dir):
        return

    # check excel file num default max=20
    original_file_list = glob.glob(src_dir + os.sep + '*.xlsx')

    if os.path.exists(src_dir):
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        backup_file_list, file_num = os.listdir(backup_dir), len(os.listdir(backup_dir))
        if file_num >= reserve_file_max_num:
            backup_file_list.sort()
            # 删除时间最久的目录以及文件
            for file in os.listdir(backup_dir + os.sep + backup_file_list[0]):
                os.remove(backup_dir + os.sep + backup_file_list[0] + os.sep + file)
            os.rmdir(backup_dir + os.sep + backup_file_list[0])

        if not os.path.exists(backup_name):
            os.makedirs(backup_name)

        # 去掉新产生的excel，只备份历史excel文件
        # TODO 类型: Bakerville or Purley-FPGA
        conf = MachineConfig(CONFIG_FILE_PATH)
        purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')
        for file_name in original_file_list:
            # print 'orignal_file:\t', src_dir + os.sep + purl_bak_string + '_' + str(judge_get_config('week_num', purl_bak_string)) + '_report_result_%s.xlsx' %setting_gloab_variable.FILE_CREATED_TIME
            # print 'file:\t', file
            try:
                shutil.copy2(file_name, backup_name)
                if src_dir + os.sep + purl_bak_string + '_' + judge_get_config('week_num', purl_bak_string) + '_' + \
                        link_WW_week_string + '_' + str(len(Silver_url_list)) + '_%s.xlsx' % log_time == file_name:
                    continue
                os.remove(file_name)
            except (WindowsError, IOError):
                pass


# TODO 删除原始缓存文件----默认保留10个文件
def backup_cache(purl_bak_string, src_dir=SRC_CACHE_DIR, backup_dir=BACKUP_cache_DIR, reserve_file_max_num=10000):
    # TODO 1、原始数据源
    backup_name = backup_dir + os.sep + 'backup_' + purl_bak_string + '_' + time.strftime('%Y_%m_%d_%H_%M_%S',
                    time.localtime(time.time())) + os.sep + purl_bak_string

    # TODO 原始备份目录不存在则跳过备份
    if not os.path.exists(src_dir):
        return

    if os.path.exists(src_dir):
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        backup_file_list, file_num = os.listdir(backup_dir), len(os.listdir(backup_dir))
        if file_num >= reserve_file_max_num:
            backup_file_list.sort()
            # TODO 删除时间最久的目录
            shutil.rmtree(backup_dir + os.sep + backup_file_list[0])

    list_dir_list_1 = os.listdir(src_dir)
    if purl_bak_string in list_dir_list_1 and os.path.exists(src_dir + os.sep + purl_bak_string):
        shutil.copytree(src_dir + os.sep + purl_bak_string, backup_name)
        shutil.rmtree(src_dir + os.sep + purl_bak_string)


# TODO 备份图片目录
def backup_chart(purl_bak_string, log_time):
    backup_name = BACKUP_PRESERVE_TABLE_CHART_DIR + os.sep + 'backup_' + purl_bak_string + '_' + log_time
    # TODO 原始备份目录不存在则跳过备份
    if not os.path.exists(PRESERVE_TABLE_CHART_DIR):
        return
    original_file_list = glob.glob(PRESERVE_TABLE_CHART_DIR + os.sep + '*.png')
    if not os.path.exists(BACKUP_PRESERVE_TABLE_CHART_DIR):
        os.makedirs(BACKUP_PRESERVE_TABLE_CHART_DIR)
    if not os.path.exists(backup_name):
        os.makedirs(backup_name)
    # print 'original_file_list:\t', original_file_list
    for file_name in original_file_list:
        try:
            shutil.copy2(file_name, backup_name)
            if purl_bak_string + '_table_chart.png' in file_name:
                continue
            os.remove(file_name)
        except (WindowsError, IOError):
            pass


# TODO 处理html
class FilterTag(object):
    def filterHtmlTag(self, htmlStr):
        '''
        过滤html中的标签
        :param htmlStr:html字符串 或是网页源码
        '''
        self.htmlStr = htmlStr
        # print self.htmlStr
        # print len(self.htmlStr)
        # 先过滤CDATA
        re_cdata = re.compile('//<!--\[CDATA\[[^-->]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*? ?="">')  # 处理换行
        re_h = re.compile('<!--?\w+[^-->]*>')  # HTML标签
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        s = re_cdata.sub('', htmlStr)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        blank_line = re.compile('\n+')  # 去掉多余的空行
        s = blank_line.sub('\n', s)
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)  # 去掉HTML注释
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        filterTag = FilterTag()
        s = filterTag.replaceCharEntity(s)  # 替换实体
        # print len(s)
        s = self.replaceCharEntity(s)
        # print len(s)
        # print  s
        return s

    def replaceCharEntity(self, htmlStr):
        '''
        替换html中常用的字符实体
        使用正常的字符替换html中特殊的字符实体
        可以添加新的字符实体到CHAR_ENTITIES 中
    CHAR_ENTITIES是一个字典前面是特殊字符实体  后面是其对应的正常字符
        :param htmlStr:
        '''
        self.htmlStr = htmlStr
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }
        re_charEntity = re.compile(r'&#?(?P<name>\w+);?\s+?')
        sz = re_charEntity.search(htmlStr)
        while sz:
            entity = sz.group()  # entity全称，如>
            key = sz.group('name')  # 去除&;后的字符如（" "--->key = "nbsp"）    去除&;后entity,如>为gt
            try:
                htmlStr = re_charEntity.sub(CHAR_ENTITIES[key], htmlStr, 1)
                sz = re_charEntity.search(htmlStr)
            except KeyError:
                # 以空串代替
                htmlStr = re_charEntity.sub('', htmlStr, 1)
                sz = re_charEntity.search(htmlStr)
        # print htmlStr
        return htmlStr

    def replace(self, s, re_exp, repl_string):
        return re_exp.sub(repl_string)

    def strip_tags(self, htmlStr):
        '''
        使用HTMLParser进行html标签过滤
        :param htmlStr:
        '''

        self.htmlStr = htmlStr
        htmlStr = htmlStr.strip()
        htmlStr = htmlStr.strip("\n")
        result = []
        parser = HTMLParser.HTMLParser()
        parser.handle_data = result.append
        parser.feed(htmlStr)
        parser.close()
        return ''.join(result)

    def stripTagSimple(self, htmlStr):
        '''
        最简单的过滤html <>标签的方法    注意必须是<任意字符>  而不能单纯是<>
        :param htmlStr:
        '''
        print len(htmlStr)
        self.htmlStr = htmlStr
        #         dr =re.compile(r'<[^>]+>',re.S)
        dr = re.compile(r'<!--?\w+[^-->]*>', re.S)
        htmlStr = re.sub(dr, '', htmlStr)
        print len(htmlStr)
        return htmlStr


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

    # TODO 操作效率太低，不适合表过大的对象
    def setRangeCell(self, win_book, Silver_url_list):
        sht = self.xlBook.Worksheets('CaseResult')
        for i in range(len(Silver_url_list)):
            for row in range(7, 170 + 1):
                for col in range(canculate_head_num(Silver_url_list, 41, i, 36 + 11),
                                 canculate_head_num(Silver_url_list, 41, i, 36 + 11 + 4 - 1) + 1):
                    sht.Cells(row, col).Interior.ColorIndex = 2
                    sht.Cells(row, col).BorderAround(1, 3)

                    # win_book.save()
                    # win_book.close()

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
def get_report_data(sheet_name, win_book, purl_bak_string, Silver_url_list, WEEK_NUM, cell_data_list=None,
                    type_string=''):
    if type_string == '':
        actually_week_info_dir = SRC_SAVE_MISS_WEEK_DIR
    else:
        actually_week_info_dir = MANUAL_SRC_SAVE_MISS_WEEK_DIR

    WEEK_NUM = int(WEEK_NUM)
    if cell_data_list is None:
        cell_data_list = []

    # TODO 新增对周数进行统计 方便定位最新周的位置 最新周从后往前算
    if sheet_name == 'Save-Miss':
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

            for k in range(WEEK_NUM + 3 - len(Silver_url_list), WEEK_NUM + 4):
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
        for col in range(WEEK_NUM - len(Silver_url_list) + 3, WEEK_NUM + 3):
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
        for i in range(3, 200):
            temp_cell_list = []
            # NewSi和existingSi用上一周的
            for j in range((WEEK_NUM - len(Silver_url_list) + 1) * 13 + 3,
                           (WEEK_NUM - len(Silver_url_list) + 1) * 13 + 1 + 13):
                data = win_book.getCell(sheet=sheet_name, row=i, col=j)
                if j == ((WEEK_NUM - len(Silver_url_list) + 1) * 13 + 1 + 1) and not data:
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
        if type_string == '':
            write_file_dir = IMAGE_ORIGINAL_RESULT
        else:
            write_file_dir = MANUAL_IMAGE_ORIGINAL_RESULT

        if not os.path.exists(write_file_dir):
            os.makedirs(write_file_dir)
        write_file = open(write_file_dir + os.sep + purl_bak_string + '_image_data.txt', 'w')

        for i in range(1, len(Silver_url_list) + 2):
            temp_cell_list = []
            for j in range(1, 8):
                data = win_book.getCell(sheet=sheet_name, row=i, col=j)
                if isinstance(data, float):
                    data = int(data)
                temp_cell_list.append(str(data))

            write_data = '\t'.join(temp_cell_list)
            write_file.write(write_data + '\n')
            cell_data_list.append(temp_cell_list)

    else:
        fstop_flag = False
        m = (WEEK_NUM - len(Silver_url_list)) * 41 + 35 + 10 + 2
        for i in range(7, 400):
            temp_cell_list = []
            for j in range(m, m + 4):
                data = win_book.getCell(sheet=sheet_name, row=i, col=j)
                if data is None:
                    data = ''
                if (j == m + 1) and data == '':
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


# TODO 输出重定向到文件
class RedirectionOutput(object):
    def __init__(self):
        self.buff = ''
        self.__console__ = sys.stdout

    def write(self, output_stream):
        self.buff += output_stream

    def to_console(self):
        sys.stdout = self.__console__
        print self.buff

    def to_file(self, file_path):
        f = open(file_path, 'w')
        sys.stdout = f
        print self.buff
        f.close()

    def flush(self):
        self.buff = ''

    def reset(self):
        sys.stdout = self.__console__


# TODO 清理excel_dir目录
def remove_excel_dir():
    if os.path.exists(SRC_EXCEL_DIR):
        for file in glob.glob(SRC_EXCEL_DIR + os.sep + '*'):
            os.remove(file)
    os.removedirs(SRC_EXCEL_DIR)


# TODO 自动打开excel确认----可以修改
def confirm_result_excel(purl_bak_string, link_WW_week_string, Silver_url_list, logger, log_time):
    # TODO 类型: Bakerville or Purley-FPGA
    file_name = os.path.split(__file__)[1]
    purl_bak_string = get_interface_config('default_purl_bak_string', purl_bak_string)
    file_path = SRC_EXCEL_DIR + os.sep + '{0}_{1}_{2}_{3}_{4}.xlsx'.format(purl_bak_string, judge_get_config('week_num', purl_bak_string),
                                link_WW_week_string, len(Silver_url_list), log_time)
    # 自动用Windows Excel.exe打开前面准备好的excel文件，使其完成计算，并等待手动保存和关闭文件。此后Python就可以读excel文件里面formula产生的value了。
    while (not os.path.exists(file_path)):
        logger.print_message("Please wait until %s is created" % (file_path), file_name)
        time.sleep(1)

    mtime = time.ctime(os.path.getmtime(file_path))
    # ctime = time.ctime(os.path.getctime(f))
    os.system('start excel.exe %s' % file_path)

    logger.print_message(
        "Please make sure %s is opened, review it, save and close.\nLast modified : %s" % (file_path, mtime), file_name)
    max_waiting_time = int(judge_get_config('max_waiting_time', purl_bak_string))
    total_time = 0

    while (not os.path.exists(file_path) or mtime == time.ctime(os.path.getmtime(file_path))):
        logger.print_message('The modification time is %d seconds left.......' % (max_waiting_time * 60 - total_time),
                             file_name)
        time.sleep(1)
        total_time += 1
        if total_time == max_waiting_time * 60:
            break

    logger.print_message("\n%s is closed.\nLast modified : %s" % (file_path, time.ctime(os.path.getmtime(file_path))),
                         file_name)


# TODO 确认载入的配置信息的正确性
def set_email_file_config_info():
    pass


# TODO NFVi项目执行指定表
def remove_special_func(purl_bak_string, func_list=None):
    if purl_bak_string == 'NFVi':
        if not func_list:
            func_list = []
        # print 'func_list:\t', func_list, len(func_list)
        for nu in range(len(func_list)):
            if 'insert_IFWI_Orignal_data' == func_list[nu] or 'insert_IFWI_data' == func_list[nu] \
                    or 'insert_IFWIInfo' == func_list[nu]:
                func_list[nu] = 'delete'
        try:
            while 1:
                func_list.remove('delete')
        except ValueError:
            pass
    return func_list


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


# TODO 更改excel名称并且修改日志名与excel同名  更改名称以excel save-miss周为准
def rename_log_file_name(logger, purl_bak_string, Silver_url_list, newest_week_type_string_list,
                         log_time, rename_log=False):
    week_actual_list = return_actual_week_list(logger, rename_log)
    link_WW_week_string = week_actual_list[0]
    file_week_length = len(week_actual_list)

    week_type_string = 'unknown'
    week_num = int(judge_get_config('week_num', purl_bak_string))

    actual_excel_file = ''
    for ele_name in glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx'):
        if log_time in ele_name and purl_bak_string in ele_name and '~' not in ele_name:
            actual_excel_file = ele_name
    if 'BKC' in newest_week_type_string_list:
        week_type_string = 'BKC'
    elif 'Gold' in newest_week_type_string_list:
        week_type_string = 'Gold'
    elif 'Silver' in newest_week_type_string_list:
        week_type_string = 'Silver'

    # TODO 修改excel文件名
    if not rename_log:
        try:
            os.rename(actual_excel_file, SRC_EXCEL_DIR + os.sep + purl_bak_string + '_' + str(week_num) + '_' + link_WW_week_string + '_' +
                      str(file_week_length) + '_' + week_type_string + '_' + log_time + '.xlsx')
            logger.print_message("Changing the excel file [ %s ]  name successfully!!!" % actual_excel_file, os.path.split(__file__)[1])
        except EOFError:
            logger.print_message("Changing the excel file [ %s ]  name failed!!!" % actual_excel_file, os.path.split(__file__)[1], ERROR)
    # TODO 修改log日志名
    else:
        actual_log_file = ''
        for ele_name in glob.glob(MACHINE_LOG_DIR + os.sep + '*machine_log.txt'):
            if log_time in ele_name:
                actual_log_file = ele_name
        try:
            os.rename(actual_log_file, MACHINE_LOG_DIR + os.sep + purl_bak_string + '_' + str(week_num) + '_' + link_WW_week_string + '_' +
                      str(len(Silver_url_list)) + '_' + week_type_string +'_' + log_time + '_log.txt')
            # logger.print_message("The log file [ %s ] was modified to excel's file name successfully!!!" % actual_log_file, os.path.split(__file__)[1])
            print "The log file [ %s ] was modified to excel's file name successfully!!!" % actual_log_file
        except:
            # logger.print_message("The log file [ %s ] was modified to excel's file name failed!!!" % actual_log_file, os.path.split(__file__)[1], ERROR)
            print "The log file [ %s ] was modified to excel's file name failed!!!" % actual_log_file


# TODO 获取windows进程名, 进程Id元组的列表
def get_win_process_ids():
    # each instance is a process, you can have multiple processes w/same name
    junk, instances = win32pdh.EnumObjectItems(None, None, 'process', win32pdh.PERF_DETAIL_WIZARD)
    process_ids = []
    process_name_list = []
    process_dict = {}
    for instance in instances:
        if instance in process_dict:
            process_dict[instance] = process_dict[instance] + 1
        else:
            process_dict[instance] = 0
    for instance, max_instances in process_dict.items():
        for i_num in xrange(max_instances + 1):
            hq = win32pdh.OpenQuery()  # initializes the query handle
            path = win32pdh.MakeCounterPath((None, 'process', instance, None, i_num, 'ID Process'))
            counter_handle = win32pdh.AddCounter(hq, path)
            type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
            process_ids.append((instance, str(val)))
            process_name_list.append(instance)
            win32pdh.CloseQuery(hq)

    process_ids.sort()
    # print process_name_list, len(process_name_list)
    # print process_ids, len(process_ids)
    # print process_dict, len(process_dict)
    return process_ids, process_name_list


# TODO 中断错误类
class InterruptError(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self, msg)


# TODO 当程序发生中断时强制清理文件
def interrupt_clear_excel_file(log_time, logger):
    remove_success_flag = False
    is_contain_object_file = False
    while True:
        if remove_success_flag:
            break
        file_list = glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx')
        logger.print_message('file_list:\t%s' % file_list, os.path.split(__file__)[1], ERROR)
        logger.print_message('log_time:\t%s' % log_time, os.path.split(__file__)[1], ERROR)
        time.sleep(2)
        for file_name in file_list:
            if log_time in file_name:
                try:
                    os.remove(file_name)
                    remove_success_flag = True
                    is_contain_object_file = True
                    break
                except WindowsError:
                    try:
                        _logger.print_message('Start cleaning up the file:\t%s' % file_name, os.path.split(__file__)[1])
                        os.system('taskkill /F /IM excel.exe')
                        os.system('attrib -s -h /s %s' % file_name)
                        os.remove(file_name)
                        remove_success_flag = True
                        is_contain_object_file = True
                        logger.print_message('delete %s sucessfully!!!' % file_name, os.path.split(__file__)[1], INFO)
                        break
                    except:
                        logger.print_message('error return', os.path.split(__file__)[1], ERROR)
            else:
                continue
        else:
            if not remove_success_flag:
                is_contain_object_file = True

            if is_contain_object_file:
                remove_success_flag = True
                logger.print_message('The files that need to be deleted are not detected', os.path.split(__file__)[1],
                                     INFO)


# TODO 返回新产生的excel表里实际周数据
def return_actual_week_list(logger, rename_log):
    if not rename_log:
        logger.print_message("SRC_SAVE_MISS_WEEK_DIR:\t%s" % SRC_SAVE_MISS_WEEK_DIR, os.path.split(__file__)[1])
    with open(SRC_SAVE_MISS_WEEK_DIR + os.sep + 'actually_week_info.txt', 'r') as f:
        week_actual_info_strings = f.readline()

    week_actual_info_list = week_actual_info_strings.split(' ')
    week_actual_info_list.sort(reverse=True)
    # print week_actual_info_list
    return week_actual_info_list


# TODO 内存检测继续执行程序回调函数
def response_button_continue_func(tk):
    tk.destroy()


# TODO 内存检测终止程序回调函数
def response_button_stop_func(tk):
    tk.destroy()
    sys.exit(1)


# TODO 内存不足时弹出的提示窗口
def response_detect_memory_gui(available_memory_size):
    from Tkinter import Tk, Button, Label, mainloop
    tk = Tk()
    tk.title('Detect Memory Usage Gui')
    label_promot = Label(tk, font=("Calibri", 12), text='The current memory %dM is insufficient,\n less than 2000M! '
                                                        'It may cause the program to be\n interrupted abnormally. Please choose to continue or stop?' % (
                                                        available_memory_size))
    but_continue = Button(tk, text='continue', font=("Calibri", 12), width=20,
                          command=lambda: response_button_continue_func(tk),
                          activeforeground='blue', activebackground='turquoise', background='green')
    but_stop = Button(tk, text='stop', font=("Calibri", 12), width=20, command=lambda: response_button_stop_func(tk),
                      activeforeground='blue', activebackground='palevioletred', background='red')

    but_continue.grid(row=2, padx=15, pady=10)
    but_stop.grid(row=3, padx=15, pady=10)
    label_promot.grid(row=1, padx=15, pady=10)

    mainloop()


# TODO 检测内存使用情况，防止发生内存错误
def detect_memory_usage(logger, cycle_times=5):
    import psutil

    file_name = os.path.split(__file__)[1]
    cpu_value_list = []
    buffers_value_list = []
    cached_value_list = []
    phy_percent_value_list = []
    phy_free_value_list = []
    phy_total_value_list = []

    def getMemorystate():
        phymem = psutil.virtual_memory()
        buffers = getattr(psutil, 'phymem_buffers', lambda: 0)()
        cached = getattr(psutil, 'cached_phymem', lambda: 0)()
        used = phymem.total - (phymem.free + buffers + cached)

        buffers_value_list.append(buffers)
        cached_value_list.append(cached)
        phy_percent_value_list.append(phymem.percent)
        phy_total_value_list.append(phymem.total)
        phy_free_value_list.append(phymem.free)

        line = " Memory: %5s%% %6s/%s" % (
            phymem.percent,
            str(int(used / 1024 / 1024)) + "M",
            str(int(phymem.total / 1024 / 1024)) + "M"
        )
        return line

    def getCPUstate(interval=2):
        cpu_percent = psutil.cpu_percent(interval)
        cpu_value_list.append(cpu_percent)
        return " CPU: " + str(cpu_percent) + "%"

    detect_time = cycle_times

    while detect_time:
        cpu_info = getCPUstate()
        memory_info = getMemorystate()
        logger.print_message('The %d time:\t' % (
        cycle_times - detect_time + 1) + time.asctime() + " | " + cpu_info + " | " + memory_info, file_name)
        detect_time -= 1

    buffers = sum(buffers_value_list) / len(buffers_value_list)
    cached = sum(cached_value_list) / len(cached_value_list)
    phy_percent = sum(phy_percent_value_list) / len(phy_percent_value_list)
    phy_total = sum(phy_total_value_list) / len(phy_total_value_list)
    cpu_percent = sum(cpu_value_list) / len(cpu_value_list)
    phy_free = sum(phy_free_value_list) / len(phy_free_value_list)

    used = phy_total - (phy_free + buffers + cached)

    line = " Memory: %5s%% %6s/%s" % (
        phy_percent,
        str(int(used / 1024 / 1024)) + "M",
        str(int(phy_total / 1024 / 1024)) + "M"
    )

    # TODO 需达到预留2000M内存空间
    available_memory_size = int(phy_total / 1024 / 1024) - int(used / 1024 / 1024)
    logger.print_message(
        'Average:%s\t' % (' ' * (len('The %d time') - len('Average'))) + time.asctime() + " | " + " CPU: " +
        '%.1f' % cpu_percent + "%" + " | " + line, file_name)
    # TODO 低于2000M则弹出提示窗口
    if available_memory_size < 2000:
        response_detect_memory_gui(available_memory_size)


# TODO 获取对应项目最近日期的文件
def get_project_newest_file(purl_bak_string, logger):
    file_name = os.path.split(__file__)[1]
    file_list = [ele for ele in glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx') if purl_bak_string in ele]
    file_list.sort(reverse=True)

    if purl_bak_string == 'Bakerville':
        purl_bak_string = 'ITF_Skylake_DE'
    if purl_bak_string == 'Purley-FPGA':
        purl_bak_string = 'ITF_Skylake_FPGA'

    if file_list:
        template_file = file_list[0]
    else:
        pwd_file_list = [ele for ele in glob.glob(os.getcwd() + os.sep + '*.xlsx') if purl_bak_string in ele]
        if pwd_file_list:
            template_file = pwd_file_list[0]
        else:
            logger.print_message('The template file is not detected', file_name, 30)
            logger.close()
            sys.exit(1)

    logger.print_message('newest template file:\t%s' % template_file, file_name)
    return template_file


if __name__ == '__main__':
    start = time.time()
    # # TODO 执行之前安装所需模块
    # win_book = easyExcel(r'C:\Users\pengzh5x\Desktop\machine_scripts\excel_dir\Purley-FPGA_100_2017WW27_34_BKC_2017_07_24_08_12_42.xlsx')
    # # # TODO 类型: Bakerville or Purley-FPGA or NFVi
    # Silver_url_list = []
    # f = open(r'C:\Users\pengzh5x\Desktop\machine_scripts\report_html\url_info.txt', 'r')
    # for line in f:
    #         if 'Purley-FPGA' in line and 'Silver' in line:
    #             Silver_url_list.append(line.strip('\n'))
    # Silver_url_list = Silver_url_list[:50]
    # # cell_data_list = get_report_data('Save-Miss', win_book=win_book, purl_bak_string='Purley-FPGA', Silver_url_list=Silver_url_list, WEEK_NUM=100)
    # win_book.save()
    # win_book.close()
    # process_ids, process_name_list = get_win_process_ids()
    # print process_name_list
    print time.time() - start