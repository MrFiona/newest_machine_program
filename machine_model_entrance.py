#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-12 17:28
# Author  : MrFiona
# File    : machine_model_entrance.py
# Software: PyCharm Community Edition


import os
import re
import sys
import time
from logging import CRITICAL
from machine_scripts.custom_log import WorkLogger

log_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
_logger = WorkLogger(log_filename='machine_log', log_time=log_time)

try:
    from machine_scripts.get_all_html import GetUrlFromHtml
    from machine_scripts.insert_excel_old import InsertDataIntoExcel
    from machine_scripts.public_use_function import (get_url_list_by_keyword, judge_get_config,
        easyExcel, error_tracking_decorator)
    from machine_scripts.common_interface_func import (get_project_newest_file, detect_memory_usage,
        rename_log_file_name, interrupt_clear_excel_file, InterruptError, get_win_process_ids,
        confirm_result_excel, backup_chart, backup_excel_file, backup_cache, performance_analysis_decorator)
    from machine_scripts.common_interface_branch_func import (traceback_print_info, obtain_prefix_project_name,
                                                              HPQC_function)
    from machine_scripts.cache_mechanism import DiskCache
    from machine_scripts.send_email import SendEmail
    from machine_scripts.create_email_html import create_save_miss_html
    from machine_scripts.wxpython_gui import gui_main,display_config_info
    from machine_scripts.generate_chart import generate_chart
    from setting_global_variable import SRC_WEEK_DIR, type_sheet_name_list, SRC_EXCEL_DIR
    from HPQC.create_session import Session
    from HPQC.hpqc_query import HPQCQuery
    from HPQC.hpqc_main_entrance import HPQC_main_entrance

except ImportError:
    _logger.print_message('Please check whether the requirements.txt file is in the current directory or no network state '
                          'but the installation module is missing', os.path.split(__file__)[1], CRITICAL)

#TODO 控制相应的位置发生错误是否清理excel文件
INTERRUPTED_CLEAR_FILE_CONDITION_FLAG = True
WIN_BOOK_CLOSE_FLAG = False
AUTO_RUN_FLAG = False
PURL_BAK_STRING = ''
LOGGER_CLOSE_FLAG = False


#TODO 模型执行入口函数
def machine_model_entrance(session, query, purl_bak_string, _logger, file_name, on_off_line_save_flag, auto_run_flag):
    if on_off_line_save_flag == 'offline':
        _logger.print_message('Program Offline Run Mode Switch is on', file_name)
    #TODO 是否重新获取数据标记  开启:YES   关闭:NO
    reacquire_data_flag = judge_get_config('reacquire_data_flag', purl_bak_string)
    #TODO 获取week周覆盖标记 YES：部分周覆盖
    keep_continuous = judge_get_config('keep_continuous', purl_bak_string)
    #TODO 正常流程
    if reacquire_data_flag == 'YES' and keep_continuous != 'YES':
        #TODO 获取之前需清理缓存，存在url更新的情况
        backup_cache(purl_bak_string)

    get_url_object = GetUrlFromHtml(html_url_pre='https://dcg-oss.intel.com/ossreport/auto/', logger=_logger)
    #todo 只有在在线并且抓取数据标志开启才重新抓取数据
    if reacquire_data_flag == 'YES' and on_off_line_save_flag == 'online' and keep_continuous != 'YES':
        _logger.print_message('>>>>>>>>>> Please Wait .... The program is getting Html Data <<<<<<<<<<', file_name)
        #TODO 获取html并保存到文件
        get_url_object.get_all_type_data(purl_bak_string, get_only_department=True)
        #TODO keep_continuous='NO':重新获取整周项目数据  keep_continuous:YES 只更新相应周数据文件
        get_url_object.write_all_html_by_multi_thread(purl_bak_string)
        _logger.print_message('>>>>>>>>>> Get Html Data Finished <<<<<<<<<<', file_name)

    Silver_url_list = get_url_list_by_keyword(purl_bak_string, 'Silver')
    # Silver_url_list = ['https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW52/17139_Silver.html',
    #                    'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW50/16051_Silver.html']
    print '\033[31mSilver_url_list:\t\033[0m', Silver_url_list
    cache = DiskCache(purl_bak_string)

    #TODO 默认以实际最新周开始
    link_WW_week_string = 'Default'
    if Silver_url_list:
        WW_week_info_string = re.split('\D+', Silver_url_list[0].split('/')[-2])
        link_WW_week_string = WW_week_info_string[0] + 'WW' + WW_week_info_string[-1]

    section_Silver_url_list = []
    if on_off_line_save_flag == 'online' and keep_continuous == 'YES':
        #TODO 更新对应周缓存
        effective_week_string_list = get_url_object.write_section_html_by_multi_thread(purl_bak_string)
        #TODO 获取对应周url列表
        section_Silver_url_list = get_url_list_by_keyword(purl_bak_string, 'Silver', None, 100, effective_week_string_list)
    #TODO verify_flag_flag改为了True，兼容新加的功能 提取最新周的类型 : Silver、Gold、BKC
    insert_object = InsertDataIntoExcel(session, query, Silver_url_list, section_Silver_url_list, link_WW_week_string,
                                        True, purl_bak_string, cache, _logger, log_time, keep_continuous)
    predict_execute_flag = insert_object.return_predict_execute_flag()
    _logger.print_message('predict_execute_flag:\t%s' % predict_execute_flag, file_name)
    #todo 返回candidate日期字符串，没有candidate则默认：default_bkc_string
    predict_newest_insert_bkc_string = insert_object.return_predict_bkc_string()
    _logger.print_message('predict_newest_insert_bkc_string:\t%s' % predict_newest_insert_bkc_string, file_name)
    func_name_list = insert_object.return_name().keys()
    call_func_list = [ func for func in func_name_list if func.startswith('insert') ]
    if 'insert_CaseResult' in call_func_list:
        call_func_list.remove('insert_CaseResult')
        call_func_list.append('insert_CaseResult')
    _logger.print_message('call_func_list:\t%s' % call_func_list, file_name)

    #TODO 将数据插入excel
    _logger.print_message('>>>>>>>>>> Please Wait .... The program is inserting Excel Data <<<<<<<<<<', file_name)
    try:
        for func in call_func_list:
            getattr(insert_object, func)()
        contain_candidate_week = insert_object.return_contain_candidate_week()
        _logger.print_message('contain_candidate_week:\t%s' % contain_candidate_week, file_name)
        #todo 存在candidate则插入candidate数据  正常模式下：有candidate则插入数据；自定义选周模式下，必须用户选择了candidate周才执行
        if (predict_execute_flag and keep_continuous != 'YES') or contain_candidate_week:
            predict_call_func_list = [func for func in func_name_list if func.startswith('predict_insert')]
            for func in predict_call_func_list:
                getattr(insert_object, func)()
        #todo 在CaseResult表里插入HPQC test-plan对应项目的test-case信息
        insert_object._insert_test_case_info_into_excel()
    except:
        traceback_print_info(logger=_logger)
        insert_object.close_workbook()
        raise InterruptError('Interrupt Error occurred!!!')

    #todo 返回日期类型字符串列表，不包括candidate
    newest_week_type_string_list = insert_object.return_newest_week_type_string_list()
    insert_object.close_workbook()
    _logger.print_message('newest_week_type_string_list:\t%s' % newest_week_type_string_list, file_name)
    _logger.print_message('>>>>>>>>>> Inserting Excel Data Finished <<<<<<<<<<', file_name)

    global INTERRUPTED_CLEAR_FILE_CONDITION_FLAG
    #TODO 插入表格已经完成置错误清理标记为False
    INTERRUPTED_CLEAR_FILE_CONDITION_FLAG = False

    #TODO 是否验证excel  开启:YES   关闭:NO
    start = time.time()
    verify_file_flag = judge_get_config('verify_file_flag', purl_bak_string)
    if verify_file_flag == 'YES':
        #TODO 完成excel操作后，打开结果excel文件确认
        _logger.print_message('>>>>>>>>>> Please Wait .... The program begins to confirm the generated Excel File <<<<<<<<<<', file_name)
        confirm_result_excel(purl_bak_string, link_WW_week_string, Silver_url_list, _logger, log_time)
        _logger.print_message('>>>>>>>>>> Comfirm the Excel File Finished <<<<<<<<<<', file_name)
    else:
        os.system('taskkill /F /IM excel.exe')

    confirm_excel_time = time.time() - start

    #TODO 生成html
    _logger.print_message('>>>>>>>>>> Please Wait .... the program is generating Html File <<<<<<<<<<', file_name)
    failed_sheet_name_list = []
    WEEK_NUM = judge_get_config('week_num', purl_bak_string)
    _logger.print_message(log_time, file_name)
    _logger.print_message(os.getcwd(), file_name)
    win_book = easyExcel(SRC_EXCEL_DIR + os.sep + purl_bak_string + '_%s_%s_%d_%s.xlsx'
                         % (WEEK_NUM, link_WW_week_string, len(Silver_url_list), log_time))

    type_sheet_name_list.remove('Trend')
    type_sheet_name_list.insert(0, 'Trend')
    for type_name in type_sheet_name_list:
        try:
            create_save_miss_html(type_name, Silver_url_list, purl_bak_string, win_book, WEEK_NUM, _logger,
                                  predict_execute_flag, '', keep_continuous)
            _logger.print_message('Excel table [ %s ] data html has been generated' % type_name, file_name)
        #TODO 异常关闭文件
        except:
            traceback_print_info(_logger)
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

    #TODO 是否发送邮件标记  开启:YES   关闭:NO
    start = time.time()
    send_email_flag = judge_get_config('send_email_flag', purl_bak_string)
    if send_email_flag == 'YES':
        try:
            #TODO 发送email
            _logger.print_message('>>>>>>>>>> Please Wait .... The program starts sending Email <<<<<<<<<<', file_name)
            SendEmail(purl_bak_string, _logger, '', predict_newest_insert_bkc_string, section_Silver_url_list,
                      keep_continuous, newest_week_type_string_list, None, contain_candidate_week)
            _logger.print_message('>>>>>>>>>> Send the Email Finished <<<<<<<<<<', file_name)
        except:
            traceback_print_info(_logger)

    #TODO 备份excel文件
    _logger.print_message('>>>>>>>>>> Please Wait .... The program is backing up the Excel File <<<<<<<<<<', file_name)
    backup_excel_file(_logger, 2000, log_time, link_WW_week_string, Silver_url_list,
                      auto_run_flag, predict_execute_flag, keep_continuous, contain_candidate_week)
    _logger.print_message('>>>>>>>>>> Backing up Excel File Finished <<<<<<<<<<', file_name)
    send_backup_time = time.time() - start
    return  confirm_excel_time, send_backup_time, newest_week_type_string_list, link_WW_week_string, Silver_url_list, \
            predict_execute_flag, predict_newest_insert_bkc_string, contain_candidate_week, keep_continuous


# @performance_analysis_decorator('mkm_run.prof')
@error_tracking_decorator(_logger, os.path.split(__file__)[1], log_time)
def machine_main():
    file_name = os.path.split(__file__)[1]
    try:
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
            #TODO 内存空间检测
            _logger.print_message('>>>>>>>>>> Please Wait .... The program is detecting memory <<<<<<<<<<', file_name)
            detect_memory_usage(_logger)
            _logger.print_message('>>>>>>>>>> Memory detection Finished <<<<<<<<<<', file_name)
            #TODO 界面控制
            purl_bak_string = gui_main(_logger)

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
            #TODO classify 项目配置前缀
            project_name_sep = obtain_prefix_project_name(purl_bak_string)

            TEMPLATE_FILE = get_project_newest_file(purl_bak_string, _logger)
            conf.modify_node_value(project_name_sep + '_other_config', 'template_file', TEMPLATE_FILE)
            _logger.print_message('modify successfully!!!!', file_name)
            display_config_info(_logger, purl_bak_string)

        start_time = time.time()
        #todo HPQC变量初始化
        host = r'https://hpalm.intel.com'
        session = Session(host, 'pengzh5x', 'QQ@08061635')
        query = HPQCQuery('DCG', 'BKC')

        #todo 如果检测到HPQC模式被打开则跳过后续部分
        HPQC_mode = judge_get_config('hpqc_mode', purl_bak_string)
        _logger.print_message('HPQC Mode state is [ %s ]!!!!' % HPQC_mode, file_name)

        #todo 开启HPQC模式，系统仅执行HOQC功能
        if HPQC_mode == 'YES':
            HPQC_function(_logger, query, session, purl_bak_string)
            end_time = time.time()
            _logger.print_message('Program Run Total Time:\t%.5f' % (end_time - start_time), file_name)
        else:
            #TODO 是否离线标记获取
            on_off_line_save_flag = judge_get_config('on_off_line_save_flag', purl_bak_string)
            confirm_excel_time, send_backup_time, newest_week_type_string_list, link_WW_week_string, Silver_url_list, predict_execute_flag,\
            predict_newest_insert_bkc_string, contain_candidate_week, keep_continuous = \
                machine_model_entrance(session, query, purl_bak_string, _logger, file_name, on_off_line_save_flag, AUTO_RUN_FLAG)

            #TODO 生成趋势图
            chart_start = time.time()
            _logger.print_message('>>>>>>>>>> Please Wait .... The program is generating the Image File <<<<<<<<<<', file_name)
            generate_chart(purl_bak_string, log_time, _logger, '', AUTO_RUN_FLAG, predict_execute_flag,
                           newest_week_type_string_list[0] if newest_week_type_string_list else 'default',
                           keep_continuous, contain_candidate_week)
            _logger.print_message('>>>>>>>>>> generating the Image File Finished <<<<<<<<<<', file_name)
            chart_time = time.time() - chart_start
            #TODO 备份图片
            _logger.print_message('>>>>>>>>>> Please Wait .... The program is backing up the Image File <<<<<<<<<<', file_name)
            backup_chart(purl_bak_string, log_time, predict_execute_flag, keep_continuous, contain_candidate_week)
            _logger.print_message('>>>>>>>>>> Backing up Image File Finished <<<<<<<<<<', file_name)
            #TODO 更改excel名称
            _logger.print_message('>>>>>>>>>> Please Wait .... The program is Renaming the Excel File <<<<<<<<<<', file_name)
            rename_log_file_name(_logger, purl_bak_string, Silver_url_list, newest_week_type_string_list, log_time, False,
                                 predict_execute_flag, keep_continuous, contain_candidate_week)
            _logger.print_message('>>>>>>>>>> Renaming the Excel File Finished <<<<<<<<<<', file_name)

            global LOGGER_CLOSE_FLAG
            LOGGER_CLOSE_FLAG = True

            #todo 上传test_case到项目指定目录下
            _logger.print_message('开始上传test-case', file_name)
            HPQC_main_entrance(_logger, query, session, purl_bak_string)
            _logger.print_message('结束上传test-case', file_name)

            end_time = time.time()
            _logger.print_message('Send Excel and Backup Excel Time:\t%.5f' % send_backup_time, file_name)
            _logger.print_message('Confirm Excel Time:\t%.5f' % confirm_excel_time, file_name)
            _logger.print_message('Image shows waiting Time:\t%.5f' % chart_time, file_name)
            _logger.print_message('Program Run Total Time:\t%.5f' % (end_time - start_time - chart_time - confirm_excel_time), file_name)

            _logger.file_close()

            #TODO 修改日志名与excel同名
            rename_log_file_name(None, purl_bak_string, Silver_url_list, newest_week_type_string_list, log_time,
                                 True, predict_execute_flag, keep_continuous, contain_candidate_week)

    except InterruptError:
        _logger.print_message('Insert the data exception caused by the exit', file_name, 50)
        #TODO 程序中断清理文件
        if not LOGGER_CLOSE_FLAG:
            _logger.print_message('The cleanup file tag is already open:\t%s' % INTERRUPTED_CLEAR_FILE_CONDITION_FLAG, file_name, 50)
        if INTERRUPTED_CLEAR_FILE_CONDITION_FLAG:
            interrupt_clear_excel_file(log_time, _logger)
    except KeyboardInterrupt:
        _logger.print_message('Abort by user request!!!', file_name, 50)
        #TODO 程序中断清理文件
        if not LOGGER_CLOSE_FLAG:
            _logger.print_message('The cleanup file tag is already open:\t%s' % INTERRUPTED_CLEAR_FILE_CONDITION_FLAG,
                                  file_name, 50)
        if INTERRUPTED_CLEAR_FILE_CONDITION_FLAG:
            interrupt_clear_excel_file(log_time, _logger)
    #todo 内存异常时选择终止程序
    except SystemExit:
        if not LOGGER_CLOSE_FLAG:
            _logger.print_message('Check out insufficient memory to exit', file_name, 50)
        else:
            pass



if __name__ == '__main__':
    machine_main()
