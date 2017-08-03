#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-12 17:28
# Author  : MrFiona
# File    : machine_model_entrance.py
# Software: PyCharm Community Edition

from __future__ import absolute_import

import os
import re
import sys
import time
# TODO 执行之前安装所需模块
from machine_scripts.install_module import install_module;install_module()
from machine_scripts.custom_log import WorkLogger
log_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
_logger = WorkLogger(log_filename='machine_log', log_time=log_time)
from machine_scripts.get_all_html import GetUrlFromHtml
from machine_scripts.insert_excel import InsertDataIntoExcel
from machine_scripts.public_use_function import (get_url_list_by_keyword, judge_get_config,
    easyExcel, error_tracking_decorator)
from machine_scripts.common_interface_func import (get_project_newest_file, detect_memory_usage,
    rename_log_file_name, interrupt_clear_excel_file, InterruptError, get_win_process_ids,
    confirm_result_excel, backup_chart, backup_excel_file, backup_cache, performance_analysis_decorator)
from setting_global_variable import type_sheet_name_list
from machine_scripts.cache_mechanism import DiskCache
from machine_scripts.send_email import SendEmail
from machine_scripts.create_email_html import create_save_miss_html
from machine_scripts.machine_config_gui import main, display_config_info
from machine_scripts.generate_chart import generate_chart


# TODO 控制相应的位置发生错误是否清理excel文件
INTERRUPTED_CLEAR_FILE_CONDITION_FLAG = True
WIN_BOOK_CLOSE_FLAG = False
AUTO_RUN_FLAG = False
PURL_BAK_STRING = ''
LOGGER_CLOSE_FLAG = False


# TODO 模型执行入口函数
def machine_model_entrance(purl_bak_string, _logger, file_name, on_off_line_save_flag, auto_run_flag):
    if on_off_line_save_flag == 'offline':
        _logger.print_message('Program Offline Run Mode Switch is on', file_name)
    # TODO 是否重新获取数据标记  开启:YES   关闭:NO
    reacquire_data_flag = judge_get_config('reacquire_data_flag', purl_bak_string)

    # TODO 获取week周覆盖标记 YES：部分周覆盖
    keep_continuous = judge_get_config('keep_continuous', purl_bak_string)

    _logger.print_message('>>>>>>>>>> Please Wait .... The program is getting Html Data <<<<<<<<<<', file_name)
    # TODO 正常流程
    if reacquire_data_flag == 'YES' and keep_continuous != 'YES':
        # TODO 获取之前需清理缓存，存在url更新的情况
        backup_cache(purl_bak_string)
    get_url_object = GetUrlFromHtml(html_url_pre='https://dcg-oss.intel.com/ossreport/auto/', logger=_logger)
    # TODO 获取html
    get_url_object.get_all_type_data(purl_bak_string, get_only_department=True)
    # TODO keep_continuous:YES 则更新相应周缓存
    get_url_object.write_html_by_multi_thread(purl_bak_string, keep_continuous='NO')
    _logger.print_message('>>>>>>>>>> Get Html Data Finished <<<<<<<<<<', file_name)

    cache = DiskCache(purl_bak_string)
    Silver_url_list = get_url_list_by_keyword(purl_bak_string, 'Silver')

    # TODO 默认以实际最新周开始
    link_WW_week_string = 'Default'
    if Silver_url_list:
        WW_week_info_string = re.split('\D+', Silver_url_list[0].split('/')[-2])
        link_WW_week_string = WW_week_info_string[0] + 'WW' + WW_week_info_string[-1]

    # TODO 将数据插入excel
    _logger.print_message('>>>>>>>>>> Please Wait .... The program is inserting Excel Data <<<<<<<<<<', file_name)
    section_Silver_url_list = []
    if keep_continuous == 'YES':
        # TODO 获取对应周信息列表并且删除相应缓存
        effective_week_string_list = get_url_object.get_week_info_by_flag(purl_bak_string, delete_cache_flag=True)
        # TODO 更新对应周缓存
        get_url_object.write_html_by_multi_thread(purl_bak_string, keep_continuous='YES')
        # TODO 获取对应周url列表
        section_Silver_url_list = get_url_list_by_keyword(purl_bak_string, 'Silver', pre_url_list=effective_week_string_list)

    # TODO verify_flag_flag改为了True，兼容新加的功能 提取最新周的类型 : Silver、Gold、BKC
    insert_object = InsertDataIntoExcel(verify_flag=True, purl_bak_string=purl_bak_string, link_WW_week_string=link_WW_week_string, cache=cache,
                        silver_url_list=Silver_url_list, section_Silver_url_list=section_Silver_url_list, logger=_logger, log_time=log_time,
                        keep_continuous=keep_continuous)
    func_name_list = insert_object.return_name().keys()
    call_func_list = [ func for func in func_name_list if func.startswith('insert') ]
    predict_call_func_list = [func for func in func_name_list if func.startswith('predict_insert')]
    if 'insert_CaseResult' in call_func_list:
        call_func_list.remove('insert_CaseResult')
        call_func_list.append('insert_CaseResult')
    _logger.print_message('call_func_list:\t%s' % call_func_list, file_name)

    try:
        for func in call_func_list:
            getattr(insert_object, func)()
        for func in predict_call_func_list:
            getattr(insert_object, func)()
    except:
        insert_object.close_workbook()
        raise InterruptError('Interrupt Error occurred!!!')

    insert_object.close_workbook()
    newest_week_type_string_list = insert_object.return_newest_week_type_string_list()
    _logger.print_message('newest_week_type_string_list:\t%s' % newest_week_type_string_list, file_name)
    _logger.print_message('>>>>>>>>>> Inserting Excel Data Finished <<<<<<<<<<', file_name)

    global INTERRUPTED_CLEAR_FILE_CONDITION_FLAG
    # TODO 插入表格已经完成置错误清理标记为False
    INTERRUPTED_CLEAR_FILE_CONDITION_FLAG = False

    # TODO 是否验证excel  开启:YES   关闭:NO
    verify_file_flag = judge_get_config('verify_file_flag', purl_bak_string)

    if verify_file_flag == 'YES':
        # TODO 完成excel操作后，打开结果excel文件确认
        _logger.print_message(
            '>>>>>>>>>> Please Wait .... The program begins to confirm the generated Excel File <<<<<<<<<<', file_name)
        confirm_result_excel(purl_bak_string, link_WW_week_string, Silver_url_list, _logger, log_time)
        _logger.print_message('>>>>>>>>>> Comfirm the Excel File Finished <<<<<<<<<<', file_name)
    else:
        os.system('taskkill /F /IM excel.exe')

    # TODO 生成html
    _logger.print_message('>>>>>>>>>> Please Wait .... the program is generating Html File <<<<<<<<<<', file_name)
    failed_sheet_name_list = []
    WEEK_NUM = judge_get_config('week_num', purl_bak_string)

    _logger.print_message(log_time, file_name)

    win_book = easyExcel(os.getcwd() + os.sep + 'excel_dir' + os.sep + purl_bak_string + '_%s_%s_%d_%s.xlsx' % (WEEK_NUM, link_WW_week_string, len(Silver_url_list), log_time))

    for type_name in type_sheet_name_list:
        try:
            create_save_miss_html(sheet_name=type_name, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list, win_book=win_book, WEEK_NUM=WEEK_NUM)
            _logger.print_message('Excel table [ %s ] data html has been generated' % type_name, file_name)
        # TODO 异常关闭文件
        except:
            failed_sheet_name_list.append(type_name)
            global WIN_BOOK_CLOSE_FLAG
            WIN_BOOK_CLOSE_FLAG = True
            win_book.close()
    else:
        if not WIN_BOOK_CLOSE_FLAG:
            start_time = time.time()
            _logger.print_message('Start setting the caseresult table data format' , file_name)
            win_book.close()
            _logger.print_message('End Sets the caseresult table data format' , file_name)
            _logger.print_message('Set the format time-consuming:\t%s' % (time.time() - start_time), file_name)

    _logger.print_message('>>>>>>>>>> Generating Html File Finished <<<<<<<<<<', file_name)
    _logger.print_message('failed_sheet_name_list:%s\t' % failed_sheet_name_list, file_name)

    # TODO 是否发送邮件标记  开启:YES   关闭:NO
    send_email_flag = judge_get_config('send_email_flag', purl_bak_string)
    start = time.time()
    if send_email_flag == 'YES':
        try:
            # TODO 发送email
            _logger.print_message('>>>>>>>>>> Please Wait .... The program starts sending Email <<<<<<<<<<', file_name)
            SendEmail(purl_bak_string, _logger)
            _logger.print_message('>>>>>>>>>> Send the Email Finished <<<<<<<<<<', file_name)
        except:
            pass

    # TODO 备份excel文件
    _logger.print_message('>>>>>>>>>> Please Wait .... The program is backing up the Excel File <<<<<<<<<<', file_name)
    backup_excel_file(logger=_logger, log_time=log_time, link_WW_week_string=link_WW_week_string, Silver_url_list=Silver_url_list,
                      auto_iteration_flag=auto_run_flag)
    _logger.print_message('>>>>>>>>>> Backing up Excel File Finished <<<<<<<<<<', file_name)
    confirm_time = time.time() - start
    return  confirm_time, newest_week_type_string_list, link_WW_week_string, Silver_url_list


@performance_analysis_decorator('mkm_run.prof')
@error_tracking_decorator(_logger, os.path.split(__file__)[1], log_time)
def machine_main():
    try:
        file_name = os.path.split(__file__)[1]
        _logger.print_message('sys.argv:\t%s' % sys.argv, file_name)
        if 'auto' in sys.argv:
            global AUTO_RUN_FLAG
            AUTO_RUN_FLAG = True
            if len(sys.argv) == 3:
                global PURL_BAK_STRING
                PURL_BAK_STRING = sys.argv[-1]

        process_info_list, process_name_list = get_win_process_ids()
        if 'EXCEL' in process_name_list:
            os.system('taskkill /F /IM excel.exe')

        file_name = os.path.split(__file__)[1]
        if not AUTO_RUN_FLAG:
            # TODO 内存空间检测
            _logger.print_message('>>>>>>>>>> Please Wait .... The program is detecting memory <<<<<<<<<<', file_name)
            detect_memory_usage(logger=_logger)
            _logger.print_message('>>>>>>>>>> Memory detection Finished <<<<<<<<<<', file_name)
            # TODO 界面控制
            purl_bak_string = main(logger=_logger)
        else:
            purl_bak_string = PURL_BAK_STRING
            _logger.print_message('purl_bak_string:\t%s' % purl_bak_string, file_name)
            from machine_scripts.machine_config import MachineConfig
            from setting_global_variable import CONFIG_FILE_PATH
            conf = MachineConfig(CONFIG_FILE_PATH)
            conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_on_off_line_save_flag', 'online')
            conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_reacquire_data_flag', 'YES')
            conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_keep_continuous', 'no')
            conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_verify_file_flag', 'NO')
            conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_send_email_flag', 'YES')
            conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_get_default_flag', 'NO')
            # TODO classify 项目配置前缀
            if purl_bak_string == 'Purley-FPGA':
                string_sep = 'FPGA'
            elif purl_bak_string == 'Bakerville':
                string_sep = 'Bak'
            else:
                string_sep = 'NFV'

            TEMPLATE_FILE = get_project_newest_file(purl_bak_string, _logger)
            conf.modify_node_value(string_sep + '_other_config', 'template_file', TEMPLATE_FILE)
            _logger.print_message('modify successfully!!!!', file_name)
            display_config_info(logger=_logger, purl_bak_string=purl_bak_string)

        start_time = time.time()
        # TODO 是否离线标记获取
        on_off_line_save_flag = judge_get_config('on_off_line_save_flag', purl_bak_string)
        confirm_time, newest_week_type_string_list, link_WW_week_string, Silver_url_list = \
            machine_model_entrance(purl_bak_string, _logger, file_name, on_off_line_save_flag, AUTO_RUN_FLAG)

        # TODO 生成趋势图
        chart_start = time.time()
        _logger.print_message('>>>>>>>>>> Please Wait .... The program is generating the Image File <<<<<<<<<<', file_name)
        generate_chart(purl_bak_string=purl_bak_string, log_time=log_time, logger=_logger, auto_run_flag=AUTO_RUN_FLAG)
        _logger.print_message('>>>>>>>>>> generating the Image File Finished <<<<<<<<<<', file_name)
        chart_time = time.time() - chart_start
        # TODO 备份图片
        _logger.print_message('>>>>>>>>>> Please Wait .... The program is backing up the Image File <<<<<<<<<<', file_name)
        backup_chart(purl_bak_string, log_time)
        _logger.print_message('>>>>>>>>>> Backing up Image File Finished <<<<<<<<<<', file_name)
        # TODO 更改excel名称
        _logger.print_message('>>>>>>>>>> Please Wait .... The program is Renaming the Excel File <<<<<<<<<<', file_name)
        rename_log_file_name(logger=_logger, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list,
                             newest_week_type_string_list=newest_week_type_string_list, log_time=log_time)
        _logger.print_message('>>>>>>>>>> Renaming the Excel File Finished <<<<<<<<<<', file_name)
        end_time = time.time()
        _logger.print_message('Confirm Excel and Send Email Time:\t%.5f' % confirm_time, file_name)
        _logger.print_message('Image shows waiting Time:\t%.5f' % chart_time, file_name)
        _logger.print_message('Program Run Total Time:\t%.5f' % (end_time - start_time - chart_time), file_name)

        global LOGGER_CLOSE_FLAG
        LOGGER_CLOSE_FLAG = True
        _logger.file_close()

        # TODO 修改日志名与excel同名
        rename_log_file_name(logger=None, purl_bak_string=purl_bak_string, Silver_url_list=Silver_url_list,
                             newest_week_type_string_list=newest_week_type_string_list, log_time=log_time, rename_log=True)
    except (InterruptError, KeyboardInterrupt):
        # TODO 程序中断清理文件
        if not LOGGER_CLOSE_FLAG:
            _logger.print_message('The cleanup file tag is already open:\t%s' % INTERRUPTED_CLEAR_FILE_CONDITION_FLAG, os.path.split(__file__)[1], 30)
        if INTERRUPTED_CLEAR_FILE_CONDITION_FLAG:
            interrupt_clear_excel_file(log_time, _logger)
    # todo 内存异常时选择终止程序
    except SystemExit:
        if not LOGGER_CLOSE_FLAG:
            _logger.print_message('Check out insufficient memory to exit', os.path.split(__file__)[1], 30)
        else:
            pass


if __name__ == '__main__':
    machine_main()
