#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-07-26 15:11
# Author  : MrFiona
# File    : common_interface_func.py
# Software: PyCharm Community Edition

import re
import os
import sys
import glob
import time
import shutil
from logging import ERROR
from setting_global_variable import (SRC_EXCEL_DIR, SRC_SAVE_MISS_WEEK_DIR, MACHINE_LOG_DIR,
    BACKUP_PRESERVE_TABLE_CHART_DIR, PRESERVE_TABLE_CHART_DIR, BACKUP_CACHE_DIR, SRC_CACHE_DIR,
    BACKUP_EXCEL_DIR, CONFIG_FILE_PATH, DO_PROF)
from machine_scripts.machine_config import MachineConfig
from machine_scripts.public_use_function import judge_get_config, get_interface_config


_file_name = os.path.split(__file__)[1]



# TODO 验证url的有效性
def verify_validity_url(url, logger):
    import urllib2
    logger.print_message('Verifying url %s Start' % (url), _file_name)
    try:
        response = urllib2.urlopen(url)
    # TODO HTTPError是URLError的子类，在产生URLError时也会触发产生HTTPError。因此需注意应该先处理HTTPError
    except urllib2.URLError, e:
        if hasattr(e, 'code'):  # stands for HTTPError
            logger.print_message(msg="find http error, writing... [ %s ]" % e.code, logger_name=_file_name,
                                 definition_log_level=ERROR)
            return False
        elif hasattr(e, 'reason'):  # stands for URLError
            logger.print_message(msg="can not reach a server,writing... [ %s ]" % e.reason, logger_name=_file_name,
                                 definition_log_level=ERROR)
            return False
        else:  # stands for unknown error
            logger.print_message(msg="unknown error, writing...", logger_name=_file_name, definition_log_level=ERROR)
            return False
    else:
        # print "url is reachable!"
        # else 中不用再判断 response.code 是否等于200,若没有抛出异常，肯定返回200,直接关闭即可
        response.close()
        return True
    finally:
        logger.print_message('Verifying url %s End' % (url), _file_name)


# TODO 隐藏表列  sub_signal_width新增少隐藏多少周
def hidden_data_by_column(sheet_name, url_list, multiple, sub_signal_width):
    conf = MachineConfig(CONFIG_FILE_PATH)
    purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')
    hidden_length = int(judge_get_config('week_num', purl_bak_string)) - len(url_list) - sub_signal_width
    sheet_name.set_column(0, multiple * hidden_length - 1, options={'hidden': True})


# TODO 返回新产生的excel表里实际周数据
def return_actual_week_list(logger, rename_log):
    if not rename_log:
        logger.print_message("SRC_SAVE_MISS_WEEK_DIR:\t%s" % SRC_SAVE_MISS_WEEK_DIR, _file_name)
    with open(SRC_SAVE_MISS_WEEK_DIR + os.sep + 'actually_week_info.txt', 'r') as f:
        week_actual_info_strings = f.readline()

    week_actual_info_list = week_actual_info_strings.split(' ')
    week_actual_info_list.sort(reverse=True)
    # print week_actual_info_list
    return week_actual_info_list


# TODO 更改excel名称并且修改日志名与excel同名  更改名称以excel save-miss周为准
def rename_log_file_name(logger, purl_bak_string, Silver_url_list, newest_week_type_string_list, log_time, rename_log=False):
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
            logger.print_message("Changing the excel file [ %s ]  name successfully!!!" % actual_excel_file, _file_name)
        except EOFError:
            logger.print_message("Changing the excel file [ %s ]  name failed!!!" % actual_excel_file, _file_name, ERROR)
    # TODO 修改log日志名
    else:
        actual_log_file = ''
        for ele_name in glob.glob(MACHINE_LOG_DIR + os.sep + '*machine_log.txt'):
            if log_time in ele_name:
                actual_log_file = ele_name
        try:
            os.rename(actual_log_file, MACHINE_LOG_DIR + os.sep + purl_bak_string + '_' + str(week_num) + '_' + link_WW_week_string + '_' +
                      str(len(Silver_url_list)) + '_' + week_type_string +'_' + log_time + '_log.txt')
            print "The log file [ %s ] was modified to excel's file name successfully!!!" % actual_log_file
        except:
            print "The log file [ %s ] was modified to excel's file name failed!!!" % actual_log_file


# TODO 获取对应项目最近日期的文件
def get_project_newest_file(purl_bak_string, logger):
    file_list = [ele for ele in glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx') if purl_bak_string in ele]
    file_list.sort(reverse=True)

    if file_list:
        template_file = file_list[0]
    else:
        pwd_file_list = [ele for ele in glob.glob(os.getcwd() + os.sep + '*.xlsx') if purl_bak_string in ele]
        if pwd_file_list:
            template_file = pwd_file_list[0]
        else:
            logger.print_message('The template file is not detected', _file_name, 30)
            logger.file_close()
            sys.exit(1)

    logger.print_message('newest template file:\t%s' % template_file, _file_name)
    return template_file


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
    label_temporary = Label(tk, font=("Calibri", 12), text='The current memory %dM is insufficient,\n less than 2000M! '
            'It may cause the program to be\n interrupted abnormally. Please choose to continue or stop?' % (available_memory_size))
    but_continue = Button(tk, text='continue', font=("Calibri", 12), width=20, command=lambda: response_button_continue_func(tk),
            activeforeground='blue', activebackground='turquoise', background='green')
    but_stop = Button(tk, text='stop', font=("Calibri", 12), width=20, command=lambda: response_button_stop_func(tk),
            activeforeground='blue', activebackground='palevioletred', background='red')

    but_continue.grid(row=2, padx=15, pady=10)
    but_stop.grid(row=3, padx=15, pady=10)
    label_temporary.grid(row=1, padx=15, pady=10)

    mainloop()


# TODO 性能分析装饰器
def performance_analysis_decorator(filename):
    """
    Decorator for function profiling.
    """
    import pstats
    import cProfile
    import functools

    def wrapper(func):
        @functools.wraps(func)
        def profiled_func(*args, **kwargs):
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


# TODO 检测内存使用情况，防止发生内存错误
def detect_memory_usage(logger, cycle_times=5):
    import psutil

    cpu_value_list = []
    buffers_value_list = []
    cached_value_list = []
    phy_percent_value_list = []
    phy_free_value_list = []
    phy_total_value_list = []

    def get_memory_state():
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
        memory_info = get_memory_state()
        logger.print_message('The %d time:\t' % (
        cycle_times - detect_time + 1) + time.asctime() + " | " + cpu_info + " | " + memory_info, _file_name)
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
        '%.1f' % cpu_percent + "%" + " | " + line, _file_name)
    # TODO 低于2000M则弹出提示窗口
    if available_memory_size < 2000:
        response_detect_memory_gui(available_memory_size)


# TODO 去除特殊字符策略函数
def remove_non_alphanumeric_characters(object_string_list):
    # TODO 对提取的字符串列表进行清洗，统一组合格式：空格分隔
    for ele in range(len(object_string_list)):
        object_string_list[ele] = re.sub('[\s]', 'MrFiona', object_string_list[ele])
        object_string_list[ele] = re.sub('[^\w\"\'\.\_\-\>\[\]\(\)\@\~\/\*]', '', object_string_list[ele])
        temp_ele_list = re.split('MrFiona', object_string_list[ele])
        ele_list = [effective for effective in temp_ele_list if len(effective) != 0]
        object_string_list[ele] = ' '.join(ele_list)
    return object_string_list


# TODO 去除特殊字符策略函数 NFVi
def NFVi_remove_non_alphanumeric_characters(object_string_list):
    for ele in range(len(object_string_list)):
        object_string_list[ele] = re.sub('[\s]', 'MrFiona', object_string_list[ele])
        object_string_list[ele] = re.sub('[^\w\"\'\.\_\-\>\[\]\(\)\@\~\/\*!+,;]', '', object_string_list[ele])
        temp_ele_list = re.split('MrFiona', object_string_list[ele])
        ele_list = [effective for effective in temp_ele_list if len(effective) != 0]
        object_string_list[ele] = ' '.join(ele_list)
    return object_string_list


# TODO 当程序发生中断时强制清理文件
def interrupt_clear_excel_file(log_time, logger):
    remove_success_flag = False
    is_contain_object_file = False
    while True:
        if remove_success_flag:
            break
        file_list = glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx')
        logger.print_message('file_list:\t%s' % file_list, _file_name, ERROR)
        logger.print_message('log_time:\t%s' % log_time, _file_name, ERROR)
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
                        logger.print_message('Start cleaning up the file:\t%s' % file_name, _file_name)
                        os.system('taskkill /F /IM excel.exe')
                        os.system('attrib -s -h /s %s' % file_name)
                        os.remove(file_name)
                        remove_success_flag = True
                        is_contain_object_file = True
                        logger.print_message('delete %s sucessfully!!!' % file_name, _file_name)
                        break
                    except:
                        logger.print_message('error return', _file_name, ERROR)
            else:
                continue
        else:
            if not remove_success_flag:
                is_contain_object_file = True

            if is_contain_object_file:
                remove_success_flag = True
                logger.print_message('The files that need to be deleted are not detected', _file_name)


# TODO 中断错误类
class InterruptError(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self, msg)


# TODO 获取windows进程名, 进程Id元组的列表
def get_win_process_ids():
    import win32pdh
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


# TODO 自动打开excel确认----可以修改
def confirm_result_excel(purl_bak_string, link_WW_week_string, Silver_url_list, logger, log_time):
    purl_bak_string = get_interface_config('default_purl_bak_string', purl_bak_string)
    file_path = SRC_EXCEL_DIR + os.sep + '{0}_{1}_{2}_{3}_{4}.xlsx'.format(purl_bak_string, judge_get_config('week_num', purl_bak_string),
                                link_WW_week_string, len(Silver_url_list), log_time)
    # todo 目标文件不存在
    while (not os.path.exists(file_path)):
        logger.print_message("Please wait until %s is created" % (file_path), _file_name)
        time.sleep(1)

    modify_time = time.ctime(os.path.getmtime(file_path))
    os.system('start excel.exe %s' % file_path)

    logger.print_message("Please make sure %s is opened, review it, save and close.\nLast modified : %s" % (file_path, modify_time), _file_name)
    max_waiting_time = int(judge_get_config('max_waiting_time', purl_bak_string))
    total_time = 0

    while (not os.path.exists(file_path) or modify_time == time.ctime(os.path.getmtime(file_path))):
        logger.print_message('The modification time is %d seconds left.......' % (max_waiting_time * 60 - total_time), _file_name)
        time.sleep(1)
        total_time += 1
        if total_time == max_waiting_time * 60:
            break

    logger.print_message("\n%s is closed.\nLast modified : %s" % (file_path, time.ctime(os.path.getmtime(file_path))), _file_name)


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
            if purl_bak_string in file_name and log_time in file_name:
                continue
            os.remove(file_name)
        except (WindowsError, IOError):
            pass


# TODO 删除原始缓存文件----默认保留1000个文件
def backup_cache(purl_bak_string, reserve_file_max_num=1000):
    # TODO 1、原始数据源
    backup_name = BACKUP_CACHE_DIR + os.sep + 'backup_' + purl_bak_string + '_' + time.strftime('%Y_%m_%d_%H_%M_%S',
                    time.localtime(time.time())) + os.sep + purl_bak_string

    # TODO 原始备份目录不存在则跳过备份
    if not os.path.exists(SRC_CACHE_DIR):
        return

    if os.path.exists(SRC_CACHE_DIR):
        if not os.path.exists(BACKUP_CACHE_DIR):
            os.makedirs(BACKUP_CACHE_DIR)

        backup_file_list, file_num = os.listdir(BACKUP_CACHE_DIR), len(os.listdir(BACKUP_CACHE_DIR))
        if file_num >= reserve_file_max_num:
            backup_file_list.sort()
            # TODO 删除时间最久的目录
            shutil.rmtree(BACKUP_CACHE_DIR + os.sep + backup_file_list[0])

    list_dir_list_1 = os.listdir(SRC_CACHE_DIR)
    if purl_bak_string in list_dir_list_1 and os.path.exists(SRC_CACHE_DIR + os.sep + purl_bak_string):
        shutil.copytree(SRC_CACHE_DIR + os.sep + purl_bak_string, backup_name)
        shutil.rmtree(SRC_CACHE_DIR + os.sep + purl_bak_string)


# TODO 备份Excel文件----默认保留2000个文件 在自动模式下，要求excel_dir目录下始终保存各个项目
# TODO 最新的结果文件以完成迭代(执行对应项目的第二次)，否则可能会重新迭代
def backup_excel_file(logger, reserve_file_max_num=2000, log_time=None, link_WW_week_string=None, Silver_url_list=None,
                      auto_iteration_flag=False):
    backup_name = BACKUP_EXCEL_DIR + os.sep + 'backup_excel_' + time.strftime('%Y_%m_%d_%H_%M_%S',
                                time.localtime(time.time()))
    # todo 原始备份目录不存在则跳过备份
    if not os.path.exists(SRC_EXCEL_DIR):
        return

    original_file_list = glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx')

    if os.path.exists(SRC_EXCEL_DIR):
        if not os.path.exists(BACKUP_EXCEL_DIR):
            os.makedirs(BACKUP_EXCEL_DIR)

        backup_file_list, file_num = os.listdir(BACKUP_EXCEL_DIR), len(os.listdir(BACKUP_EXCEL_DIR))
        if file_num >= reserve_file_max_num:
            backup_file_list.sort()
            # todo 删除时间最久的目录以及文件
            for file in os.listdir(BACKUP_EXCEL_DIR + os.sep + backup_file_list[0]):
                os.remove(BACKUP_EXCEL_DIR + os.sep + backup_file_list[0] + os.sep + file)
            os.rmdir(BACKUP_EXCEL_DIR + os.sep + backup_file_list[0])

        if not os.path.exists(backup_name):
            os.makedirs(backup_name)

        conf = MachineConfig(CONFIG_FILE_PATH)
        purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')
        # todo 正常模式备份 只保留该项目当前产生的excel
        if not auto_iteration_flag:
            for file_name in original_file_list:
                try:
                    shutil.copy2(file_name, backup_name)
                    if SRC_EXCEL_DIR + os.sep + purl_bak_string + '_' + judge_get_config('week_num', purl_bak_string) + '_' + \
                            link_WW_week_string + '_' + str(len(Silver_url_list)) + '_%s.xlsx' % log_time == file_name:
                        continue
                    os.remove(file_name)
                except (WindowsError, IOError):
                    pass
        # todo 自动模式备份 保留三个项目最新的excel
        else:
            Bak_excel_list = [ name for name in original_file_list if 'Bakerville' in name ]
            NFVi_excel_list = [ name for name in original_file_list if 'NFVi' in name ]
            FPGA_excel_list = [ name for name in original_file_list if 'Purley-FPGA' in name ]
            # todo 每个项目仅按照时间排序 保留最新的
            Bak_excel_list.sort(key=lambda x: x.split('_')[-6:])
            NFVi_excel_list.sort(key=lambda x: x.split('_')[-6:])
            FPGA_excel_list.sort(key=lambda x: x.split('_')[-6:])
            preserve_project_excel_list = []
            if Bak_excel_list:
                preserve_project_excel_list.append(Bak_excel_list[-1])
            if NFVi_excel_list:
                preserve_project_excel_list.append(NFVi_excel_list[-1])
            if FPGA_excel_list:
                preserve_project_excel_list.append(FPGA_excel_list[-1])
            logger.print_message('preserve_project_excel_list:\t%s' % preserve_project_excel_list, _file_name)

            for file_name in original_file_list:
                try:
                    shutil.copy2(file_name, backup_name)
                    if file_name in preserve_project_excel_list:
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
        import HTMLParser

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



if __name__ == '__main__':
    pass





