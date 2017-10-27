#!/usr/bin/env python
# -*- coding: utf-8 -*-
# User    : apple
# File    : generate_chart.py
# Author  : MrFiona 一枚程序员
# Time     : 2017-05-24 13:01


import os
import re
import glob

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

from machine_scripts.custom_log import WorkLogger
from machine_scripts.machine_config import MachineConfig
from machine_scripts.public_use_function import get_interface_config, easyExcel
from setting_global_variable import CONFIG_FILE_PATH, SRC_EXCEL_DIR, MANUAL_CONFIG_FILE_PATH, \
    PRESERVE_TABLE_CHART_DIR, IMAGE_ORIGINAL_RESULT, MANUAL_IMAGE_ORIGINAL_RESULT

_file_name = os.path.split(__file__)[1]


def get_max_num(first_data, second_data, third_data, fourth_data, fifth_data,
                display_software, display_New, display_Existing, display_Closed, display_Total):
    negative_num_list, positive_num_list = [], []

    if display_software == 'YES':
        negative_first_data = [ abs(ele) for ele in first_data if ele < 0 ]
        negative_num_list.extend(negative_first_data)
        positive_first_data = [abs(ele) for ele in first_data if ele > 0]
        positive_num_list.extend(positive_first_data)
    if display_New == 'YES':
        negative_second_data = [ abs(ele) for ele in second_data if ele < 0 ]
        negative_num_list.extend(negative_second_data)
        positive_second_data = [abs(ele) for ele in second_data if ele > 0]
        positive_num_list.extend(positive_second_data)
    if display_Existing == 'YES':
        negative_third_data = [ abs(ele) for ele in third_data if ele < 0 ]
        negative_num_list.extend(negative_third_data)
        positive_third_data = [abs(ele) for ele in third_data if ele > 0]
        positive_num_list.extend(positive_third_data)
    if display_Closed == 'YES':
        negative_fourth_data = [ abs(ele) for ele in fourth_data if ele < 0 ]
        negative_num_list.extend(negative_fourth_data)
        positive_fourth_data = [abs(ele) for ele in fourth_data if ele > 0]
        positive_num_list.extend(positive_fourth_data)
    if display_Total == 'YES':
        negative_fifth_data = [ abs(ele) for ele in fifth_data if ele < 0 ]
        negative_num_list.extend(negative_fifth_data)
        positive_fifth_data = [abs(ele) for ele in fifth_data if ele > 0]
        positive_num_list.extend(positive_fifth_data)

    #TODO 负数和正数可能有一个不存在
    if negative_num_list:
        max_negative_num = max(negative_num_list)
    else:
        max_negative_num = 0

    if positive_num_list:
        max_positive_num = max(positive_num_list)
    else:
        max_positive_num = 0
    return max_negative_num, max_positive_num



def get_sighting_num(seven_data, eight_data, nine_data, display_save_test, display_save_effort, display_miss):
    positive_num_sighting_list = []
    if display_save_test == 'YES':
        positive_seven_data = [abs(ele) for ele in seven_data if ele > 0]
        positive_num_sighting_list.extend(positive_seven_data)
    if display_save_effort == 'YES':
        positive_eight_data = [abs(ele) for ele in eight_data if ele > 0]
        positive_num_sighting_list.extend(positive_eight_data)
    if display_miss == 'YES':
        positive_nine_data = [abs(ele) for ele in nine_data if ele > 0]
        positive_num_sighting_list.extend(positive_nine_data)

    if positive_num_sighting_list:
        max_positive_num = max(positive_num_sighting_list)
    else:
        max_positive_num = 0
    return max_positive_num



def generate_chart(purl_bak_string, log_time, logger, type_string='', auto_run_flag=False, predict_execute_flag=False, week_type_string='default'):
    file_list = glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx')
    object_excel_file = None
    if type_string == '':
        object_file_list = [ ele for ele in file_list if log_time in ele ]
        if object_file_list:
            object_excel_file = object_file_list[0]
            logger.print_message('object_excel_file:\t%s' % object_excel_file, _file_name)
    else:
        conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
        object_excel_file = conf.get_node_info('manual_machine_info', 'template_info')
        logger.print_message('object_excel_file:\t%s' % object_excel_file, _file_name)

    fig = plt.figure()
    fig.set_size_inches(w=15, h=8)

    if type_string == '':
        image_html_result = IMAGE_ORIGINAL_RESULT
        chart_link_string = ''
    else:
        image_html_result = MANUAL_IMAGE_ORIGINAL_RESULT
        chart_link_string = '_' + type_string

    if type_string == '':
        #TODO 获取代表是否显示五个表的参数
        display_software = get_interface_config('display_software', purl_bak_string)
        display_New = get_interface_config('display_new', purl_bak_string)
        display_Existing = get_interface_config('display_existing', purl_bak_string)
        display_Closed = get_interface_config('display_closed', purl_bak_string)
        display_Total = get_interface_config('display_total', purl_bak_string)
        display_save_test = get_interface_config('display_total', purl_bak_string)
        display_save_effort = get_interface_config('display_total', purl_bak_string)
        display_miss = get_interface_config('display_total', purl_bak_string)
    else:
        conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
        display_software = conf.get_node_info('manual_chart_config', 'display_software')
        display_New = conf.get_node_info('manual_chart_config', 'display_new')
        display_Existing = conf.get_node_info('manual_chart_config', 'display_existing')
        display_Closed = conf.get_node_info('manual_chart_config', 'display_closed')
        display_Total = conf.get_node_info('manual_chart_config', 'display_total')
        display_save_test = conf.get_node_info('manual_chart_config', 'display_save_test')
        display_save_effort = conf.get_node_info('manual_chart_config', 'display_save_effort')
        display_miss = conf.get_node_info('manual_chart_config', 'display_miss')

    header_display_string_list = ['Software Change' if display_software == 'YES' else '', 'New Sighting' if display_New == 'YES' else '',
                                  'Existing Sighting' if display_Existing == 'YES' else '', 'Closed Sighting' if display_Closed == 'YES' else '',
                                  'Total Sighting' if display_Total == 'YES' else '']

    header_display_string_list_sighting = ['Saved Test Case (%)' if display_save_test == 'YES' else '',
                                  'Saved Efforts (%)' if display_save_effort == 'YES' else '',
                                  'Missed Sighting (%)' if display_miss == 'YES' else '']

    header_display_string_list = [ header_data for header_data in header_display_string_list if len(header_data) != 0 ]
    header_display_string_list_sighting = [ header_data for header_data in header_display_string_list_sighting if len(header_data) != 0 ]

    weeks_list, first_data, second_data, third_data, fourth_data, fifth_data, seven_data, eight_data, nine_data = [], [], [], [], [], [], [], [], []

    read_file = open(image_html_result + os.sep + purl_bak_string + '_image_data.txt', 'r')

    for line in read_file:
        string_list = line.strip().split()
        if len(string_list) == 10 and re.search('\d+WW\d+', string_list[1]):
            weeks_list.append(string_list[1].strip('WW'))
            first_data.append(int(string_list[2])); second_data.append(int(string_list[3]))
            third_data.append(int(string_list[4])); fourth_data.append(int(string_list[5]))
            fifth_data.append(int(string_list[6]));seven_data.append(int(string_list[7].replace('%', '')))
            eight_data.append(int(string_list[8].replace('%', '')))
            nine_data.append(int(string_list[9].replace('%', '')))


    #TODO 时间日期加人年份 定制显示格式 2017-06-26 update
    for index in range(len(weeks_list)):
        weeks_list_ele_list = weeks_list[index].split('WW')
        weeks_list[index] = weeks_list_ele_list[0] + '\n' + 'WW' + weeks_list_ele_list[-1]

    if display_software == 'YES':
        logger.print_message('Software Change:\t%s\t%d' %(first_data, len(first_data)), _file_name)
    if display_New == 'YES':
        logger.print_message('New Sighting:\t%s\t%d' %(second_data, len(second_data)), _file_name)
    if display_Existing == 'YES':
        logger.print_message('Existing Sighting:\t%s\t%d' %(third_data, len(third_data)), _file_name)
    if display_Closed == 'YES':
        logger.print_message('Closed Sighting:\t%s\t%d' %(fourth_data, len(fourth_data)), _file_name)
    if display_Total == 'YES':
        logger.print_message('Total Sighting:\t%s\t%d' %(fifth_data, len(fifth_data)), _file_name)
    if display_save_test == 'YES':
        logger.print_message('Saved Test Case:\t%s\t%d' %(seven_data, len(seven_data)), _file_name)
    if display_save_effort == 'YES':
        logger.print_message('Saved Efforts:\t%s\t%d' %(eight_data, len(eight_data)), _file_name)
    if display_miss == 'YES':
        logger.print_message('Missed Sighting:\t%s\t%d' %(nine_data, len(nine_data)), _file_name)

    logger.print_message('weeks_list:\t%s\t%d' %(weeks_list, len(weeks_list)), _file_name)

    max_negative_num, max_positive_num = get_max_num(first_data, second_data, third_data, fourth_data, fifth_data,
                                                     display_software, display_New, display_Existing, display_Closed, display_Total)

    max_positive_num_sighting = get_sighting_num(seven_data, eight_data, nine_data, display_save_test, display_save_effort, display_miss)
    
    logger.print_message('max_negative_num:\t%d' %(max_negative_num), _file_name)
    logger.print_message('max_positive_num:\t%d' %(max_positive_num), _file_name)

    max_length = len(weeks_list);n_groups = len(weeks_list)
    index = np.arange(n_groups); bar_width = 0.60

    def autolabel(rects):
        i = 1
        for rect in rects:
            plt.text(i, rect, "%s" % int(rect))
            i += 1

    ax1 = plt.gca()
    plt.grid(color='peru', linestyle='--', ) #todo 开启网格
    #todo y轴主刻度最小单位设为1
    ax1.yaxis.set_major_locator( MultipleLocator(1) )

    if display_software == 'YES':
        plt.plot(range(1,max_length + 1), first_data, 'o--b', linewidth=2)
        autolabel(first_data)
    if display_New == 'YES':
        plt.plot(range(1,max_length + 1), second_data, 'o--m', linewidth=2)
        autolabel(second_data)
    if display_Existing == 'YES':
        plt.plot(range(1,max_length + 1), third_data, 'o--g', linewidth=2)
        autolabel(third_data)
    if display_Closed == 'YES':
        plt.plot(range(1,max_length + 1), fourth_data, 'o--r', linewidth=2)
        autolabel(fourth_data)
    if display_Total == 'YES':
        plt.plot(range(1,max_length + 1), fifth_data, 'o--c', linewidth=2)
        autolabel(fifth_data)

    if predict_execute_flag:
        candidate_string = 'Candidate_'
    else:
        candidate_string = ''

    plt.xlabel(u"Week", fontsize=18,  color='blue')
    plt.ylabel(u"Value", fontsize=18,  color='blue')
    plt.title(u"%s %s %s Trend" % (purl_bak_string, candidate_string.replace('_', ''), week_type_string), fontsize=22,  color='red')

    plt.xticks(index - 0.2 + 2 * bar_width, weeks_list, fontsize = 10, rotation=-45)
    plt.yticks(fontsize=12)  # change the num axis size
    plt.axis([0, n_groups + 1, - max_negative_num - 1, max_positive_num + 1])
    plt.legend(header_display_string_list, fontsize=14)
    plt.tight_layout()
    foo_fig = plt.gcf()  #'get current figure'

    if not os.path.exists(PRESERVE_TABLE_CHART_DIR):
        os.makedirs(PRESERVE_TABLE_CHART_DIR)

    foo_fig.savefig(PRESERVE_TABLE_CHART_DIR + os.sep + purl_bak_string + chart_link_string + '_table_chart_1_' +
                    candidate_string + log_time + '.png', format='png', dpi=fig.dpi)

    # TODO 存在excel文件则填入图表
    if object_excel_file:
        excel_obj = easyExcel(filename=object_excel_file)
        excel_obj.addPicture('Trend', pictureName=PRESERVE_TABLE_CHART_DIR + os.sep + purl_bak_string + chart_link_string + '_table_chart_1_' +
                    candidate_string + log_time + '.png', Left=500, Top=150, Width=1500, Height=800)

    #TODO 自动运行则不开启
    if not auto_run_flag:
        plt.show()
    fig.clear()

    #TODO 生成另一张图
    fig_sighting = plt.figure()
    fig_sighting.set_size_inches(w=15, h=8)
    ax1_sighting = plt.gca()
    plt.grid(color='peru', linestyle='--', )  #todo 开启网格

    #todo y轴主刻度最小单位设为1
    ax1_sighting.yaxis.set_major_locator(MultipleLocator(5))
    #TODO '%1.1f%%'
    # ax1_sighting.yaxis.set_major_formatter(FormatStrFormatter())

    if display_save_test == 'YES':
        plt.plot(range(1,max_length + 1), seven_data, 'o--c', linewidth=2)
        autolabel(seven_data)
    if display_save_effort == 'YES':
        plt.plot(range(1,max_length + 1), eight_data, 'o--m', linewidth=2)
        autolabel(eight_data)
    if display_miss == 'YES':
        plt.plot(range(1,max_length + 1), nine_data, 'o--r', linewidth=2)
        autolabel(nine_data)

    plt.xlabel(u"Week", fontsize=18, color='blue')
    plt.ylabel(u"Value", fontsize=18, color='blue')
    plt.title(u"%s %s %s Trend" % (purl_bak_string, candidate_string.replace('_', ''), week_type_string), fontsize=22, color='red')

    plt.xticks(index - 0.2 + 2 * bar_width, weeks_list, fontsize=10, rotation=-45)
    plt.yticks(fontsize=12)  #todo change the num axis size
    
    plt.axis([0, n_groups + 1, 0, max_positive_num_sighting + 10])

    plt.legend(header_display_string_list_sighting, fontsize=14)

    plt.tight_layout()
    foo_fig_sighting = plt.gcf()  #todo 'get current figure'
    foo_fig_sighting.savefig(PRESERVE_TABLE_CHART_DIR + os.sep + purl_bak_string + chart_link_string + '_table_chart_2_' +
                    candidate_string + log_time + '.png', format='png', dpi=fig.dpi)

    # TODO 存在excel文件则填入图表
    if object_excel_file:
        excel_obj.addPicture('Trend', pictureName=PRESERVE_TABLE_CHART_DIR + os.sep + purl_bak_string + chart_link_string + '_table_chart_2_' +
                    candidate_string + log_time + '.png', Left=500, Top=1100, Width=1500, Height=800)
        excel_obj.save()
        excel_obj.close()
        os.system('taskkill /F /IM excel.exe')

    #TODO 自动运行则不开启
    if not auto_run_flag:
        plt.show()
    fig_sighting.clear()




if __name__ == '__main__':
    import time
    start = time.time()
    import os
    os.chdir('..')
    _logger = WorkLogger('machine_log', create_log_flag=False)
    conf = MachineConfig(CONFIG_FILE_PATH)
    purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')
    #TODO 类型: Bakerville or Purley-FPGA
    purl_bak_string = get_interface_config('default_purl_bak_string', purl_bak_string)
    object_file = None
    file_list = glob.glob(SRC_EXCEL_DIR + os.sep + '*.xlsx')
    if file_list:
        file_list.sort(reverse=True)
        object_file = file_list[0]
    if object_file:
        print object_file
        generate_chart(purl_bak_string=purl_bak_string, log_time='2017_08_10_15_24_16', logger=_logger)
        # generate_sighing_chart(purl_bak_string=purl_bak_string, log_time='2017_08_10_15_24_16', logger=_logger)
    print time.time() - start


    #generate_chart(purl_bak_string, log_time, logger, type_string='', auto_run_flag=False, predict_execute_flag=False, week_type_string='default')