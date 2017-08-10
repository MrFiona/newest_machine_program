#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-06-21 11:07
# Author  : MrFiona
# File    : temp.py
# Software: PyCharm Comm|unity Edition

from __future__ import absolute_import

import Tkinter
import os
import re
import ttk
from Tkinter import (StringVar, Tk, END, IntVar, Label, Entry, Button, LabelFrame, Frame, X,
                     SE, RIGHT, Scrollbar, HORIZONTAL, VERTICAL, Text, BOTTOM, N, LEFT, SEL, Y, S, E, W, INSERT)
from tkFileDialog import askopenfilename
from tkMessageBox import askokcancel, askyesno

from machine_scripts.get_all_html import GetUrlFromHtml
from machine_scripts.machine_config import MachineConfig
from machine_scripts.public_use_function import get_interface_config, judge_get_config, get_url_list_by_keyword
from setting_global_variable import CONFIG_FILE_PATH, SRC_WEEK_DIR
from machine_scripts.common_interface_branch_func import obtain_prefix_project_name

# TODO Global Variable start
template_file_path, on_off_var, choose_weeks_var, on_off_numberChosen1, choose_weeks_numberChosen1 = '', '', '', '', ''
chart_software_numberChosen1, chart_new_numberChosen2, chart_exist_numberChosen3, chart_closed_numberChosen4, chart_total_numberChosen5, \
chart_save_test_numberChosen6, chart_save_effort_numberChosen7, chart_miss_numberChosen8 = '', '', '', '', '', '', '', ''
file_reacquire_data_var, check_file_var, file_max_time, file_reacquire_numberChosen1, file_check_numberChosen2 = '', '', '', '', ''
email_server, email_send, email_receive, email_send_email_flag = '', '', '', ''
chart_software_var, chart_new_var, chart_exist_var, chart_closed_var, chart_total_var, chart_save_test_var, chart_save_effort_var, \
chart_miss_var  = '', '', '', '', '', '', '', ''
load_default_var, load_default_flag = '', ''
# todo 是否发送邮件标记   True：不对邮件地址检查  False: 正常流程
global_check_email_address_vality = True

week_input_string_list = []

close_windows_update_config_flag = False
_file_name = os.path.split(__file__)[1]
type_color_dict = {'Purley-FPGA': 'green', 'Bakerville': 'yellow', 'NFVi': 'peru'}
# TODO Global Variable end


# TODO 调整界面大小函数
def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


# todo 预留函数 为显示参数用
def print_var(var):
    print var


# TODO 将当前的邮件或者文件配置信息保存到文件  新增默认保存标记 default_save_flag: True则当前配置保存为默认配置
def rewrite_config_file(purl_bak_string, default_save_flag=False, current_save_falg=False):
    conf = MachineConfig(CONFIG_FILE_PATH)
    project_name_sep = obtain_prefix_project_name(purl_bak_string)

    # TODO 接收邮件地址去重
    final_receive_list = []; index = 0; receive_address_list = []
    temp_receive_list = email_receive.get().strip().split(',')

    for receive_add in temp_receive_list:
        final_receive_list.insert(index, receive_add)
        index += 1
    for i in range(len(final_receive_list)):
        final_receive_list[i] = re.sub('[ ]', '', final_receive_list[i].strip())
    for address in final_receive_list:
        if address not in receive_address_list:
            receive_address_list.append(address)
    receive_address_string = ','.join(receive_address_list)
    # TODO 将当前的配置更新为默认配置
    if default_save_flag:
        conf.modify_node_value(project_name_sep + '_other_config', 'reacquire_data_flag', file_reacquire_data_var.get())
        conf.modify_node_value(project_name_sep + '_other_config', 'verify_file_flag', check_file_var.get())
        conf.modify_node_value(project_name_sep + '_other_config', 'max_waiting_time', file_max_time.get())
        conf.modify_node_value(project_name_sep + '_other_config', 'week_num', '100')

        conf.modify_node_value(project_name_sep + '_server', 'server_address', email_server.get() if len(email_server.get().strip()) != 0 else 'smtp.intel.com')
        conf.modify_node_value(project_name_sep + '_from_address', 'from_address', email_send.get())
        conf.modify_node_value(project_name_sep + '_receive_address', 'receive_address',receive_address_string)
        conf.modify_node_value(project_name_sep + '_other_config', 'send_email_flag', email_send_email_flag.get())
        conf.modify_node_value(project_name_sep + '_other_config', 'keep_continuous', choose_weeks_var.get())

        conf.modify_node_value(project_name_sep + '_other_config', 'on_off_line_save_flag', on_off_var.get())

    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_reacquire_data_flag', file_reacquire_data_var.get())
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_verify_file_flag', check_file_var.get())
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_max_waiting_time', file_max_time.get())
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_choose_week_num', '100')

    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_server_address', email_server.get() if len(email_server.get().strip()) != 0 else 'smtp.intel.com')
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_send_address', email_send.get())

    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_receive_address', receive_address_string)
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_send_email_flag', email_send_email_flag.get())
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_keep_continuous', choose_weeks_var.get())
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_on_off_line_save_flag', on_off_var.get())

    conf.modify_node_value(project_name_sep + '_other_config', 'template_file', template_file_path.get())

    conf.modify_node_value(project_name_sep + '_other_config', 'display_software', chart_software_var.get())
    conf.modify_node_value(project_name_sep + '_other_config', 'display_new', chart_new_var.get())
    conf.modify_node_value(project_name_sep + '_other_config', 'display_existing', chart_exist_var.get())
    conf.modify_node_value(project_name_sep + '_other_config', 'display_closed', chart_closed_var.get())
    conf.modify_node_value(project_name_sep + '_other_config', 'display_total', chart_total_var.get())
    conf.modify_node_value(project_name_sep + '_other_config', 'display_total', chart_save_test_var.get())
    conf.modify_node_value(project_name_sep + '_other_config', 'display_total', chart_save_effort_var.get())
    conf.modify_node_value(project_name_sep + '_other_config', 'display_total', chart_miss_var.get())

    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_get_default_flag', load_default_var)


# TODO 刷新界面参数相关子函数
def update_parameter_value(node, value):
    node.delete(0, END)
    node.insert(0, value)


#TODO 文件相关参数配置界面
def file_config(name, tab2, logger):
    conf = MachineConfig(CONFIG_FILE_PATH)
    current_reacquire_data_flag = conf.get_node_info(name + '_real-time_control_parameter_value', 'default_reacquire_data_flag')
    current_verify_file_flag = conf.get_node_info(name + '_real-time_control_parameter_value', 'default_verify_file_flag')
    current_max_waiting_time = conf.get_node_info(name + '_real-time_control_parameter_value', 'default_max_waiting_time')

    monty = ttk.LabelFrame(tab2, text='File config')
    monty.grid()

    global file_reacquire_data_var, check_file_var, file_max_time

    file_reacquire_data_var = StringVar()
    check_file_var = StringVar()

    label1 = Label(monty, text="Retrieve Data", font=("Calibri", 12), background='seashell')
    label2 = Label(monty, text="Verify Excel File", font=("Calibri", 12), background='skyblue')
    label3 = Label(monty, text='Maximum Time', font=("Calibri", 12), background='yellowgreen')
    label4 = Label(monty, text='minute(s)', font=("Calibri", 12))
    file_max_time = Entry(monty, borderwidth=2, width=25, font=("Calibri", 12))

    label1.grid(row=1, column=0, padx=20, pady=15, sticky='E')
    label2.grid(row=2, column=0, padx=20, pady=15, sticky='E')
    label3.grid(row=3, column=0, padx=20, pady=15, sticky='E')
    label4.grid(row=3, column=2, pady=15, sticky='W')
    file_max_time.grid(row=3, column=1, padx=10, pady=15, sticky='W')

    global file_reacquire_numberChosen1, file_check_numberChosen2

    file_reacquire_numberChosen1 = ttk.Combobox(monty, width=30, textvariable=file_reacquire_data_var, state='readonly')
    file_check_numberChosen2 = ttk.Combobox(monty, width=30, textvariable=check_file_var, state='readonly')

    file_reacquire_numberChosen1['values'] = ('YES', 'NO')
    file_check_numberChosen2['values'] = ('YES', 'NO')

    file_reacquire_numberChosen1.grid(column=1, row=1, columnspan=2, padx=10, sticky='W')
    file_check_numberChosen2.grid(column=1, row=2, columnspan=2, padx=10, sticky='W')

    file_reacquire_numberChosen1.set('YES' if current_reacquire_data_flag != '' else 'NO')
    file_check_numberChosen2.set('YES' if current_verify_file_flag != '' else 'NO')
    file_max_time.insert(0, current_max_waiting_time if current_max_waiting_time != '' else '30')

    # GUI Callback function
    def checkCallback():
        # only enable one checkbutton
        if check_file_var.get() == 'NO':
            file_max_time.delete(0, END)
            file_max_time.configure(state='disabled')
        else:
            file_max_time.configure(state='normal')

    # trace the state of the checkbutton
    check_file_var.trace('w', lambda unused0, unused1, unused2: checkCallback())


#TODO 邮件配置界面
def email_config(name, tab1, logger):
    conf = MachineConfig(CONFIG_FILE_PATH)
    current_server_address = conf.get_node_info(name + '_real-time_control_parameter_value', 'default_server_address')
    current_send_address = conf.get_node_info(name + '_real-time_control_parameter_value', 'default_send_address')
    current_receive_address = conf.get_node_info(name + '_real-time_control_parameter_value', 'default_receive_address')
    current_send_email_flag = conf.get_node_info(name + '_real-time_control_parameter_value', 'default_send_email_flag')

    monty = ttk.LabelFrame(tab1, text="Email config")
    monty.grid()

    label1 = Label(monty, text="Mail Server", font=("Calibri", 12), background='beige')
    label2 = Label(monty, text="Sender Email", font=("Calibri", 12), background='khaki')
    label3 = Label(monty, text="Recipient Email", font=("Calibri", 12), background='palegreen')
    label4 = Label(monty, text="Send Email", font=("Calibri", 12), background='sandybrown')

    label1.grid(row=1, column=0, columnspan=5, padx=20, pady=15, sticky='E')
    label2.grid(row=2, column=0, columnspan=5, padx=20, pady=15, sticky='E')
    label3.grid(row=3, column=0, columnspan=5, padx=20, pady=15, sticky='E')
    label4.grid(row=4, column=0, columnspan=5, padx=20, pady=15, sticky='E')

    global email_server, email_send, email_receive, email_send_email_flag

    email_server = Entry(monty, font=("Calibri", 12), width=27)
    email_send = Entry(monty, font=("Calibri", 12), width=27)
    email_receive = Entry(monty, font=("Calibri", 12), width=27)

    email_server.grid(row=1, column=5, columnspan=5, padx=20, pady=15)
    email_send.grid(row=2, column=5, columnspan=5, padx=20, pady=15)
    email_receive.grid(row=3, column=5, columnspan=5, padx=20, pady=15)

    email_send_email_flag = StringVar()

    def checkEmailSendCallback():
        if email_send_email_flag.get() == 'NO':
            email_server.configure(state='disabled')
            email_send.configure(state='disabled')
            email_receive.configure(state='disabled')
            # todo 邮件地址检查标记置为 False
            global global_check_email_address_vality
            global_check_email_address_vality = False
        else:
            email_server.configure(state='normal')
            email_send.configure(state='normal')
            email_receive.configure(state='normal')

    send_email_check_numberChosen2 = ttk.Combobox(monty, width=33, textvariable=email_send_email_flag, state='readonly')
    send_email_check_numberChosen2['values'] = ('YES', 'NO')
    send_email_check_numberChosen2.grid(column=5, row=4, columnspan=5, padx=20, pady=15, sticky='W')
    send_email_check_numberChosen2.set('YES' if current_send_email_flag == 'YES' else 'NO')
    email_send_email_flag.trace('w', lambda unused0, unused1, unused2: checkEmailSendCallback())

    email_server.insert(0, current_server_address.strip() if current_server_address.strip() else 'smtp.intel.com')
    email_send.insert(0, current_send_address)
    email_receive.insert(0, current_receive_address)


# TODO 图表配置界面
def chart_config(name, tab4, logger):
    current_display_software = get_interface_config('display_software', name)
    current_display_new = get_interface_config('display_new', name)
    current_display_existing = get_interface_config('display_existing', name)
    current_display_closed = get_interface_config('display_closed', name)
    current_display_total = get_interface_config('display_total', name)
    current_display_save_test = get_interface_config('display_save_test', name)
    current_display_save_effort = get_interface_config('display_save_effort', name)
    current_display_miss = get_interface_config('display_miss', name)

    monty = ttk.LabelFrame(tab4, text='Chart config')
    monty.grid()

    label1 = Label(monty, text="Software Change", font=("Calibri", 12), background='gray')
    label2 = Label(monty, text="New Sighting", font=("Calibri", 12), background='gray')
    label3 = Label(monty, text="Existing Sighting", font=("Calibri", 12), background='gray')
    label4 = Label(monty, text="Closed Sighting", font=("Calibri", 12), background='gray')
    label5 = Label(monty, text="Total Sighting", font=("Calibri", 12), background='gray')
    label6 = Label(monty, text="Saved Test Case", font=("Calibri", 12), background='gray')
    label7 = Label(monty, text="Saved Efforts", font=("Calibri", 12), background='gray')
    label8 = Label(monty, text="Missed Sighting", font=("Calibri", 12), background='gray')

    label1.grid(row=1, column=0, columnspan=5,padx=20, pady=5, sticky='E')
    label2.grid(row=2, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label3.grid(row=3, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label4.grid(row=4, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label5.grid(row=5, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label6.grid(row=6, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label7.grid(row=7, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label8.grid(row=8, column=0, columnspan=5, padx=20, pady=5, sticky='E')

    global chart_software_var, chart_new_var, chart_exist_var, chart_closed_var, chart_total_var, chart_save_test_var, chart_save_effort_var, chart_miss_var
    global chart_software_numberChosen1, chart_new_numberChosen2, chart_exist_numberChosen3, chart_closed_numberChosen4, chart_total_numberChosen5,\
        chart_save_test_numberChosen6, chart_save_effort_numberChosen7, chart_miss_numberChosen8

    chart_software_var = StringVar()
    chart_new_var = StringVar()
    chart_exist_var = StringVar()
    chart_closed_var = StringVar()
    chart_total_var = StringVar()
    chart_save_test_var = StringVar()
    chart_save_effort_var = StringVar()
    chart_miss_var = StringVar()

    # todo Add "Saved Test Case (%)", "Saved Efforts (%)", "Missed Sighting (%)" in Trend chart.  For example: if it is 50%, then the value is 50.

    chart_software_numberChosen1 = ttk.Combobox(monty, textvariable=chart_software_var, width=30, state='readonly')
    chart_new_numberChosen2 = ttk.Combobox(monty, width=30, textvariable=chart_new_var, state='readonly')
    chart_exist_numberChosen3 = ttk.Combobox(monty, width=30, textvariable=chart_exist_var, state='readonly')
    chart_closed_numberChosen4 = ttk.Combobox(monty, width=30, textvariable=chart_closed_var, state='readonly')
    chart_total_numberChosen5 = ttk.Combobox(monty, width=30, textvariable=chart_total_var, state='readonly')
    chart_save_test_numberChosen6 = ttk.Combobox(monty, width=30, textvariable=chart_save_test_var, state='readonly')
    chart_save_effort_numberChosen7 = ttk.Combobox(monty, width=30, textvariable=chart_save_effort_var, state='readonly')
    chart_miss_numberChosen8 = ttk.Combobox(monty, width=30, textvariable=chart_miss_var, state='readonly')

    chart_software_numberChosen1['values'] = ('YES', 'NO')
    chart_new_numberChosen2['values'] = ('YES', 'NO')
    chart_exist_numberChosen3['values'] = ('YES', 'NO')
    chart_closed_numberChosen4['values'] = ('YES', 'NO')
    chart_total_numberChosen5['values'] = ('YES', 'NO')
    chart_save_test_numberChosen6['values'] = ('YES', 'NO')
    chart_save_effort_numberChosen7['values'] = ('YES', 'NO')
    chart_miss_numberChosen8['values'] = ('YES', 'NO')

    chart_software_numberChosen1.grid(column=6, row=1, padx=10)
    chart_new_numberChosen2.grid(column=6, row=2, padx=10)
    chart_exist_numberChosen3.grid(column=6, row=3, padx=10)
    chart_closed_numberChosen4.grid(column=6, row=4, padx=10)
    chart_total_numberChosen5.grid(column=6, row=5, padx=10)
    chart_save_test_numberChosen6.grid(column=6, row=6, padx=10)
    chart_save_effort_numberChosen7.grid(column=6, row=7, padx=10)
    chart_miss_numberChosen8.grid(column=6, row=8, padx=10)

    chart_software_numberChosen1.current(0 if current_display_software == 'YES' else 1)
    chart_new_numberChosen2.current(0 if current_display_new == 'YES' else 1)
    chart_exist_numberChosen3.current(0 if current_display_existing == 'YES' else 1)
    chart_closed_numberChosen4.current(0 if current_display_closed == 'YES' else 1)
    chart_total_numberChosen5.current(0 if current_display_total == 'YES' else 1)
    chart_save_test_numberChosen6.current(0 if current_display_save_test == 'YES' else 1)
    chart_save_effort_numberChosen7.current(0 if current_display_save_effort == 'YES' else 1)
    chart_miss_numberChosen8.current(0 if current_display_miss == 'YES' else 1)


# TODO 验证时间参数的有效性
def verify_time_parameter(e_time):
    if len(e_time.get()) == 0 or e_time.get().isdigit() == False:
        askokcancel(title="verify time parameter", message="Please confirm that the data is an integer")
        e_time.delete(0, END)
        return False
    elif e_time.get().isdigit() == True:
        return True


# TODO 保存默认配置
def save_default(purl_bak_string):
    default_save_flag = askyesno('Save the %s default configuration window' % purl_bak_string,
                                 'Are you sure you need to save the current %s configuration as the default configuration?' % purl_bak_string)
    rewrite_config_file(purl_bak_string, default_save_flag=default_save_flag)


# TODO 加载默认配置为当前配置
def load_default_as_current(purl_bak_string):
    conf = MachineConfig(CONFIG_FILE_PATH)
    project_name_sep = obtain_prefix_project_name(purl_bak_string)

    week_num = conf.get_node_info(project_name_sep + '_other_config', 'week_num')
    reacquire_data_flag = conf.get_node_info(project_name_sep + '_other_config', 'reacquire_data_flag')
    verify_file_flag = conf.get_node_info(project_name_sep + '_other_config', 'verify_file_flag')
    max_waiting_time = conf.get_node_info(project_name_sep + '_other_config', 'max_waiting_time')
    on_off_line_save_flag = conf.get_node_info(project_name_sep + '_other_config', 'on_off_line_save_flag')
    send_email_flag = conf.get_node_info(project_name_sep + '_other_config', 'send_email_flag')
    keep_continuous = conf.get_node_info(project_name_sep + '_other_config', 'keep_continuous')

    server_address = conf.get_node_info(project_name_sep + '_server', 'server_address')
    from_address = conf.get_node_info(project_name_sep + '_from_address', 'from_address')
    receive_address = conf.get_node_info(project_name_sep + '_receive_address', 'receive_address')

    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_choose_week_num',
                           week_num if len(week_num.strip()) != 0 else '100')
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_reacquire_data_flag',
                           'YES' if reacquire_data_flag.strip() == 'YES' else 'NO')
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_verify_file_flag',
                           'YES' if verify_file_flag.strip() == 'YES' else 'NO')
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_max_waiting_time',
                           max_waiting_time if len(max_waiting_time.strip()) != 0 else '120')
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_on_off_line_save_flag',
                           'online' if on_off_line_save_flag.strip() == 'online' else 'offline')
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_send_email_flag',
                           'YES' if send_email_flag.strip() == 'YES' else 'NO')
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_keep_continuous',
                           'YES' if keep_continuous.strip() == 'YES' else 'NO')

    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_server_address', server_address)
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_send_address', from_address)
    conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_receive_address', receive_address)


# TODO 加载默认配置
def load_default(purl_bak_string):
    default_load_flag = askyesno('Load the %s default configuration window' % purl_bak_string,
                                 'Are you sure you need to load the %s default configuration?' % purl_bak_string)
    global load_default_var
    global load_default_flag
    # global close_windows_update_config_flag
    load_default_flag = True
    # close_windows_update_config_flag = True
    load_default_var = 'NO'
    conf = MachineConfig(CONFIG_FILE_PATH)

    if default_load_flag:
        load_default_var = 'YES'
        # TODO 修改加载默认配置参数标记
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_get_default_flag', load_default_var)
        # TODO 加载默认配置的时候将默认值配置值更新到当前配置
        load_default_as_current(purl_bak_string)


# TODO 载入默认邮件和文件参数配置  置 get_default_flag标记为 : YES
def load_default_configuration_info(name, tab6, logger):
    monty = ttk.LabelFrame(tab6, text='Default config')
    monty.grid()

    button1 = Button(monty, text='Load Default', font=("Calibri", 12), width=14, background='peru',
                command=lambda x=name: load_default(name), activeforeground='blue', activebackground='turquoise')
    button2 = Button(monty, text='Save Default', font=("Calibri", 12), width=14, background='green',
                command=lambda x=name: save_default(name), activeforeground='blue', activebackground='palegreen')

    # TODO 刷新配置界面参数 Save Default按钮按下时触发
    def update_config_value(event):
        conf = MachineConfig(CONFIG_FILE_PATH)
        project_name_sep = obtain_prefix_project_name(name)

        reacquire_data_flag = conf.get_node_info(project_name_sep + '_other_config', 'reacquire_data_flag')
        verify_file_flag = conf.get_node_info(project_name_sep + '_other_config', 'verify_file_flag')
        max_waiting_time = conf.get_node_info(project_name_sep + '_other_config', 'max_waiting_time')
        on_off_line_save_flag = conf.get_node_info(project_name_sep + '_other_config', 'on_off_line_save_flag')
        send_email_flag = conf.get_node_info(project_name_sep + '_other_config', 'send_email_flag')

        template_file = conf.get_node_info(project_name_sep + '_other_config', 'template_file')
        choose_week_flag = conf.get_node_info(project_name_sep + '_other_config', 'keep_continuous')

        server_address = conf.get_node_info(project_name_sep + '_server', 'server_address')
        from_address = conf.get_node_info(project_name_sep + '_from_address', 'from_address')
        receive_address = conf.get_node_info(project_name_sep + '_receive_address', 'receive_address')

        software_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_software')
        new_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_new')
        exist_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_existing')
        close_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_closed')
        total_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_total')
        save_test_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_save_test')
        save_effort_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_save_effort')
        miss_flag = conf.get_node_info(project_name_sep + '_other_config', 'display_miss')

        # TODO 关闭窗口需要保存当前配置
        global close_windows_update_config_flag

        close_windows_update_config_flag = False

        # TODO 更新界面参数值 刷新界面
        update_parameter_value(email_server, server_address)
        update_parameter_value(email_send, from_address.strip())
        update_parameter_value(template_file_path, template_file.strip())

        # TODO 接收邮件地址去重
        final_receive_list = []; index = 0; receive_address_list = []
        temp_receive_list = receive_address.strip().split(',')
        for receive_add in temp_receive_list:
            final_receive_list.insert(index, receive_add)
            index += 1
        for i in range(len(final_receive_list)):
            final_receive_list[i] = re.sub('[ ]', '', final_receive_list[i].strip())

        for address in final_receive_list:
            if address not in receive_address_list:
                receive_address_list.append(address)

        receive_address_string = ','.join(receive_address_list)
        update_parameter_value(email_receive, receive_address_string)

        file_reacquire_numberChosen1.set('YES' if reacquire_data_flag.strip() == 'YES' else 'NO')
        file_check_numberChosen2.set('YES' if verify_file_flag.strip() == 'YES' else 'NO')

        update_parameter_value(file_max_time, max_waiting_time if len(max_waiting_time.strip()) != 0 else '120')
        on_off_numberChosen1.set('YES' if on_off_line_save_flag.strip() == 'YES' else 'NO')
        email_send_email_flag.set('YES' if send_email_flag.strip() == 'YES' else 'NO')

        choose_weeks_numberChosen1.set('YES' if choose_week_flag.strip() == 'YES' else 'NO')
        chart_software_numberChosen1.set('YES' if software_flag.strip() == 'YES' else 'NO')
        chart_new_numberChosen2.set('YES' if new_flag.strip() == 'YES' else 'NO')
        chart_exist_numberChosen3.set('YES' if exist_flag.strip() == 'YES' else 'NO')
        chart_closed_numberChosen4.set('YES' if close_flag.strip() == 'YES' else 'NO')
        chart_total_numberChosen5.set('YES' if total_flag.strip() == 'YES' else 'NO')
        chart_save_test_numberChosen6.set('YES' if save_test_flag.strip() == 'YES' else 'NO')
        chart_save_effort_numberChosen7.set('YES' if save_effort_flag.strip() == 'YES' else 'NO')
        chart_miss_numberChosen8.set('YES' if miss_flag.strip() == 'YES' else 'NO')

    # TODO 绑定按钮事件实现实时更新界面参数值
    button1.bind('<Button-1>', update_config_value)
    button1.grid(row=6, column=0, padx=20, pady=15, sticky='W')
    button2.grid(row=6, column=6, padx=20, pady=15, sticky='E')


#TODO 配置参数完成后显示各项参数
def display_config_info(logger, purl_bak_string):
    file_logger_name = os.path.split(__file__)[1]

    from_address = judge_get_config('from_address', purl_bak_string)
    receive_address = judge_get_config('receive_address', purl_bak_string)
    server_address = judge_get_config('server_address', purl_bak_string)

    week_num = judge_get_config('week_num', purl_bak_string)
    reacquire_data_flag = judge_get_config('reacquire_data_flag', purl_bak_string)
    verify_file_flag = judge_get_config('verify_file_flag', purl_bak_string)
    max_waiting_time = judge_get_config('max_waiting_time', purl_bak_string)
    on_off_line_save_flag = judge_get_config('on_off_line_save_flag', purl_bak_string)
    keep_continuous = judge_get_config('keep_continuous', purl_bak_string)
    send_email_flag = judge_get_config('send_email_flag', purl_bak_string)
    template_file = get_interface_config('template_file', purl_bak_string)
    get_default_flag = get_interface_config('default_get_default_flag', purl_bak_string)

    display_software = get_interface_config('display_software', purl_bak_string)
    display_new = get_interface_config('display_new', purl_bak_string)
    display_existing = get_interface_config('display_existing', purl_bak_string)
    display_closed = get_interface_config('display_closed', purl_bak_string)
    display_total = get_interface_config('display_total', purl_bak_string)
    display_save_test = get_interface_config('display_save_test', purl_bak_string)
    display_save_effort = get_interface_config('display_save_effort', purl_bak_string)
    display_miss = get_interface_config('display_miss', purl_bak_string)

    # TODO 检测是否有空值，有则添加默认值 2017-06-02
    conf = MachineConfig(CONFIG_FILE_PATH)
    if get_default_flag == 'YES' or len(get_default_flag.strip()) == 0:
        project_name_sep = obtain_prefix_project_name(purl_bak_string)

        if len(week_num.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'week_num', '100')
        if len(reacquire_data_flag.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'reacquire_data_flag', 'YES')
        if len(verify_file_flag.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'verify_file_flag', 'NO')
        if len(max_waiting_time.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'max_waiting_time', '30min')
        if len(on_off_line_save_flag.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'on_off_line_save_flag', 'online')
        if len(send_email_flag.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'send_email_flag', 'YES')

        if len(display_software.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_software', 'YES')
        if len(display_new.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_new', 'YES')
        if len(display_existing.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_existing', 'YES')
        if len(display_closed.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_closed', 'YES')
        if len(display_total.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_total', 'YES')
        if len(display_save_test.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_save_test', 'YES')
        if len(display_save_effort.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_save_effort', 'YES')
        if len(display_miss.strip()) == 0:
            conf.modify_node_value(project_name_sep + '_other_config', 'display_miss', 'YES')

    if len(week_num.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_choose_week_num', '100')
    if len(reacquire_data_flag.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_reacquire_data_flag', 'YES')
    if len(verify_file_flag.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_verify_file_flag', 'NO')
    if len(max_waiting_time.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_max_waiting_time', '30min')
    if len(on_off_line_save_flag.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_on_off_line_save_flag', 'online')
    if len(send_email_flag.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_send_email_flag', 'YES')

    # TODO 以下参数必须非空
    if len(from_address.strip()) == 0:
        logger.print_message('The sender email address is null!!!', _file_name, 30)
        raise UserWarning('The sender email address is null!!!')
    if len(receive_address.strip()) == 0:
        logger.print_message('The recipient email address is null!!!', _file_name, 30)
        raise UserWarning('The recipient email address is null!!!')
    if len(server_address.strip()) == 0:
        logger.print_message('The server email address is null!!!', _file_name, 30)
        raise UserWarning('The server email address is null!!!')
    if len(template_file.strip()) == 0:
        logger.print_message('The template file path is null!!!', _file_name, 30)
        raise UserWarning('The template file path is null!!!')

    from_address = judge_get_config('from_address', purl_bak_string)
    receive_address = judge_get_config('receive_address', purl_bak_string)
    server_address = judge_get_config('server_address', purl_bak_string)

    week_num = judge_get_config('week_num', purl_bak_string)
    reacquire_data_flag = judge_get_config('reacquire_data_flag', purl_bak_string)
    verify_file_flag = judge_get_config('verify_file_flag', purl_bak_string)
    max_waiting_time = judge_get_config('max_waiting_time', purl_bak_string)
    on_off_line_save_flag = judge_get_config('on_off_line_save_flag', purl_bak_string)
    send_email_flag = judge_get_config('send_email_flag', purl_bak_string)
    template_file = get_interface_config('template_file', purl_bak_string)
    get_default_flag = get_interface_config('default_get_default_flag', purl_bak_string)

    display_software = get_interface_config('display_software', purl_bak_string)
    display_new = get_interface_config('display_new', purl_bak_string)
    display_existing = get_interface_config('display_existing', purl_bak_string)
    display_closed = get_interface_config('display_closed', purl_bak_string)
    display_total = get_interface_config('display_total', purl_bak_string)
    display_save_test = get_interface_config('display_save_test', purl_bak_string)
    display_save_effort = get_interface_config('display_save_effort', purl_bak_string)
    display_miss = get_interface_config('display_miss', purl_bak_string)

    logger.print_message('purl_bak_string:%s%s' % (' ' * (10 + 19 - len('purl_bak_string')), purl_bak_string), file_logger_name)

    logger.print_message('from_address:%s%s' % (' ' * (10 + 19 - len('from_address')), from_address), file_logger_name)
    logger.print_message('receive_address:%s%s' % (' ' * (10 + 19 - len('receive_address')), receive_address), file_logger_name)
    logger.print_message('server_address:%s%s' % (' ' * (10 + 19 - len('server_address')), server_address), file_logger_name)

    logger.print_message('week_num:%s%s' % (' ' * (10 + 19 - len('week_num')), week_num), file_logger_name)
    logger.print_message('reacquire_data_flag:%s%s' % (' ' * (10 + 19 - len('reacquire_data_flag')), reacquire_data_flag), file_logger_name)
    logger.print_message('verify_file_flag:%s%s' % (' ' * (10 + 19 - len('verify_file_flag')), verify_file_flag), file_logger_name)
    logger.print_message('max_waiting_time:%s%s minute(s)' % (' ' * (10 + 19 - len('max_waiting_time')), max_waiting_time), file_logger_name)
    logger.print_message('on_off_line_save_flag:%s%s' % (' ' * (10 + 19 - len('on_off_line_save_flag')), on_off_line_save_flag), file_logger_name)
    logger.print_message('keep_continuous:%s%s' % (' ' * (10 + 19 - len('keep_continuous')), keep_continuous), file_logger_name)
    logger.print_message('send_email_flag:%s%s' % (' ' * (10 + 19 - len('send_email_flag')), send_email_flag), file_logger_name)
    logger.print_message('get_default_flag:%s%s' % (' ' * (10 + 19 - len('get_default_flag')), get_default_flag), file_logger_name)

    logger.print_message('display_software:%s%s' % (' ' * (10 + 19 - len('display_software')), display_software), file_logger_name)
    logger.print_message('display_new:%s%s' % (' ' * (10 + 19 - len('display_new')), display_new), file_logger_name)
    logger.print_message('display_existing:%s%s' % (' ' * (10 + 19 - len('display_existing')), display_existing), file_logger_name)
    logger.print_message('display_closed:%s%s' % (' ' * (10 + 19 - len('display_closed')), display_closed), file_logger_name)
    logger.print_message('display_total:%s%s' % (' ' * (10 + 19 - len('display_total')), display_total), file_logger_name)
    logger.print_message('display_save_test:%s%s' % (' ' * (10 + 19 - len('display_save_test')), display_save_test), file_logger_name)
    logger.print_message('display_save_effort:%s%s' % (' ' * (10 + 19 - len('display_save_effort')), display_save_effort), file_logger_name)
    logger.print_message('display_miss:%s%s' % (' ' * (10 + 19 - len('display_miss')), display_miss), file_logger_name)
    logger.print_message('template_file:%s%s' % (' ' * (10 + 19 - len('template_file')), template_file),  file_logger_name)
    logger.print_message('week_input_string_list:%s%s' % (' ' * (10 + 19 - len('week_input_string_list')), week_input_string_list),  file_logger_name)


# TODO excel模板文件配置回调函数
def file_choose(e):
    filename = askopenfilename(initialdir=os.getcwd(), filetypes=(("excel file", "*.xlsx;*.xls;*.csv"),))
    e.delete(0, END); e.insert(0, filename)
    return filename


# TODO excel模板文件配置界面
def template_file_choose(name, tab3):
    current_template_file = get_interface_config('template_file', name)
    monty = ttk.LabelFrame(tab3, text='Template config')
    monty.grid()

    global template_file_path
    template_file_path = Entry(monty, font=("Calibri", 12), width=40)
    template_file_path.grid(row=1, column=2, columnspan=2, padx=20, pady=15)
    template_file_path.insert(0, current_template_file)
    button1 = Button(monty, text="Excel Template", font=("Calibri", 12), background='yellow', command=lambda y=template_file_path: file_choose(template_file_path))
    button1.grid(row=1, column=0, columnspan=2, padx=20, pady=15)


# TODO 检查参数的安全性 配置界面关闭时触发
def check_gui_parameter_validity(logger):
    current_email_server, current_email_send, current_email_receive = email_server.get(), email_send.get(), email_receive.get()
    current_template_file_path = template_file_path.get()

    email_compile = re.compile(pattern='\w+.@intel.com')

    # TODO 不发生邮件时不做检查
    if global_check_email_address_vality:
        if len(current_email_server.strip()) == 0 or not current_email_server.endswith('intel.com'):
            logger.print_message('The email server address is illegal!!!', _file_name, 30)
            raise UserWarning('The email server address is illegal!!!')

        if not re.search(email_compile, current_email_send.strip()) or not current_email_send.endswith('intel.com'):
            logger.print_message('email sender address is illegal!!!', _file_name, 30)
            raise UserWarning('The email sender address is illegal!!!')

        for receive_address in current_email_receive.strip().split(','):
            if not re.search(email_compile, receive_address.strip()) or not receive_address.endswith('intel.com'):
                logger.print_message('email recipient address is illegal!!!', _file_name, 30)
                raise UserWarning('The email recipient address is illegal!!!')

    if not os.path.exists(current_template_file_path.strip()):
        logger.print_message('The template file path does not exist', _file_name, 30)
        template_file_path.delete(0, END)
        raise UserWarning('The template file path does not exist')
    else:
        # TODO 判断是否是个文件
        if os.path.isfile(current_template_file_path.strip()):
            # TODO 当前目录下则填充全路径
            if current_template_file_path.strip() in os.listdir(os.getcwd()):
                template_file_path.delete(0, END)
                template_file_path.insert(0, os.getcwd() + os.sep + current_template_file_path.strip())
        else:
            logger.print_message('The path of the file you entered is a directory, not a file', _file_name, 30)
            template_file_path.delete(0, END)
            raise UserWarning('The path of the file you entered is a directory, not a file')


# TODO 检测窗口是否关闭 关闭则保存当前配置
def callback(win, purl_bak_string, logger):
    # TODO 如果未按任何的按钮直接关闭窗口则重置重载默认配置标记为NO
    if not load_default_flag:
        conf = MachineConfig(CONFIG_FILE_PATH)
        # TODO 修改加载默认配置参数标记
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_get_default_flag', 'NO')
        rewrite_config_file(purl_bak_string, default_save_flag=False, current_save_falg=True)

    if not close_windows_update_config_flag:
        # TODO 检查参数的有效性已经非空性
        check_gui_parameter_validity(logger)
        rewrite_config_file(purl_bak_string)

    win.eval('::ttk::CancelRepeat')
    win.destroy()
    logger.print_message('The main windows of configuration is closed!', _file_name, 20)


# TODO 项目类型配置界面
def sub_main(name, top, logger):
    top.destroy()
    # TODO 检测是否有空值，有则添加默认值 2017-06-09
    conf = MachineConfig(CONFIG_FILE_PATH)
    conf.modify_node_value('real-time_control_parameter_value', 'default_purl_bak_string', name)

    win = Tk()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    win.title("%s User configuration interface" % name)
    tabControl = ttk.Notebook(win)  # Create Tab Control
    center_window(root=win, height=(screen_width - screen_height)/2 - 20, width=(screen_width - screen_height)/2 + 250)

    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab4 = ttk.Frame(tabControl)
    tab5 = ttk.Frame(tabControl)
    tab6 = ttk.Frame(tabControl)

    tabControl.add(tab1, text=' Email ')
    tabControl.add(tab2, text=' Retrieve/Review ')
    tabControl.add(tab3, text=' Template ')
    tabControl.add(tab4, text=' Chart ')
    tabControl.add(tab5, text=' Other config')
    tabControl.add(tab6, text=' Default ')

    tabControl.pack(expand=1, fill="both")

    email_config(name, tab1, logger)
    file_config(name, tab2, logger)
    template_file_choose(name, tab3)
    chart_config(name, tab4, logger)
    online_or_offline_interface(name, tab5)
    load_default_configuration_info(name, tab6, logger)

    # make Esc exit the program
    win.protocol("WM_DELETE_WINDOW", lambda x=win: callback(win, name, logger))
    # create a menu bar with an Exit command
    win.bind('<Escape>', lambda e: win.destroy())

    win.mainloop()


# TODO 主程序
def main(logger):
    top = Tk()
    top.rowconfigure(1, weight=1)
    top.columnconfigure(1, weight=1)
    top.title('Configuration GUI')

    button_color_1 = type_color_dict['NFVi']; button_color_2 = type_color_dict['Bakerville']
    button_color_3 = type_color_dict['Purley-FPGA']
    var_50_100 = IntVar(); var_50_100.set(5)

    e1 = Button(top, text="NFVi", font=("Calibri", 16), command=lambda x=top, y=logger: sub_main('NFVi', top, logger), background=button_color_1, width=20, activeforeground='blue', activebackground='turquoise')
    e2 = Button(top, text="Bakerville", font=("Calibri", 16), command=lambda x=top, y=logger: sub_main('Bakerville', top, logger), background=button_color_2, width=20, activeforeground='blue', activebackground='palegreen')
    e3 = Button(top, text="Purley-FPGA", font=("Calibri", 16), command=lambda x=top, y=logger: sub_main('Purley-FPGA', top, logger), background=button_color_3, width=20, activeforeground='blue', activebackground='palevioletred')

    e1.grid(row=1, columnspan=2, column=1, padx=25, pady=20, sticky=Tkinter.W + Tkinter.E + Tkinter.N + Tkinter.S)
    e2.grid(row=2, columnspan=2, column=1, padx=25, pady=20, sticky=Tkinter.W + Tkinter.E + Tkinter.N + Tkinter.S)
    e3.grid(row=3, columnspan=2, column=1, padx=25, pady=20, sticky=Tkinter.W + Tkinter.E + Tkinter.N + Tkinter.S)

    top.mainloop()
    # TODO 类型: Bakerville or Purley-FPGA
    conf = MachineConfig(CONFIG_FILE_PATH)
    purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')

    # TODO choose_weeks_var如果为YES则弹出配置周数界面
    if choose_weeks_var.get() == 'YES':
        week_gui_config(purl_bak_string=purl_bak_string, logger=logger)

    display_config_info(logger=logger, purl_bak_string=purl_bak_string)

    return purl_bak_string


#TODO 配置离线以及控制周数据界面变量的界面
def online_or_offline_interface(purl_bak_string, tab5):
    current_on_off_line_save_flag = judge_get_config('on_off_line_save_flag', purl_bak_string)
    current_keep_continuous = judge_get_config('keep_continuous', purl_bak_string)

    monty = ttk.LabelFrame(tab5, text='Other config')
    monty.grid()

    label1 = Label(monty, text="Offline mode settings", font=("Calibri", 12), background='khaki')
    label2 = Label(monty, text="Choose weeks", font=("Calibri", 12), background='palegreen')
    label1.grid(row=1, column=0, columnspan=5, padx=20, pady=10, sticky='E')
    label2.grid(row=2, column=0, columnspan=5, padx=20, pady=10, sticky='E')

    global on_off_var, choose_weeks_var, on_off_numberChosen1, choose_weeks_numberChosen1

    on_off_var = StringVar()
    choose_weeks_var = StringVar()

    on_off_numberChosen1 = ttk.Combobox(monty, width=30, textvariable=on_off_var, state='readonly')
    choose_weeks_numberChosen1 = ttk.Combobox(monty, width=30, textvariable=choose_weeks_var, state='readonly')
    on_off_numberChosen1['values'] = ('online', 'offline')
    choose_weeks_numberChosen1['values'] = ('YES', 'NO')
    on_off_numberChosen1.grid(column=6, row=1, padx=10, pady=10)
    choose_weeks_numberChosen1.grid(column=6, row=2, padx=10, pady=10)

    # TODO 数字代表选择: 0代表第一个
    on_off_numberChosen1.current(0 if current_on_off_line_save_flag == 'online' else 1)
    choose_weeks_numberChosen1.current(0 if current_keep_continuous == 'YES' else 1)


# TODO 滚动条Scrollbar与文本框Text组合
class MainFrame(Frame):
    def __init__(self, master=None, week_info_list=None, step_length=5, entry=None):
        Frame.__init__(self, master)
        self.week_info_list = week_info_list
        self.step_length = step_length
        self.entry = entry
        self.grid(row=0, column=0, sticky="nsew")
        self.CreateScrollbar()

    def CreateScrollbar(self):
        label_frame = LabelFrame(self)
        label_frame.pack(fill=X)

        self.label_frame_1 = LabelFrame(label_frame)
        self.label_frame_1.pack(fill=X)

        self.button_clear = Button(self.label_frame_1, text="clear", width=8, height=1, command=self.clear_info)
        self.button_enable = Button(self.label_frame_1, text="display", width=8, height=1, command=self.show_info)
        self.button_clear.pack(expand=0, side=RIGHT, anchor=SE)
        self.button_enable.pack(expand=0, side=LEFT, anchor=SE)

        self.scrollbar_x = Scrollbar(self.label_frame_1, orient=HORIZONTAL)  # 水平滚动条
        self.scrollbar_y = Scrollbar(self.label_frame_1, orient=VERTICAL)  # 竖向滚动条
        self.text = Text(self.label_frame_1, height=20, yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set, wrap=None)  # 文本框
        # 滚动事件
        self.scrollbar_x.config(command=self.text.xview)
        self.scrollbar_y.config(command=self.text.yview)
        # 布局
        self.scrollbar_x.pack(fill=X, side=BOTTOM, anchor=N)
        self.scrollbar_y.pack(fill=Y, side=RIGHT, anchor=N)
        self.text.pack(fill=X, expand=1, side=LEFT)
        # 绑定事件
        self.text.bind('<Control-Key-a>', self.selectText)
        self.text.bind('<Control-Key-A>', self.selectText)

    def selectText(self, event):
        self.text.tag_add(SEL, '1.0', END)
        return 'break'

    def clear_info(self):
        self.text.delete('0.0', END)

    def show_info(self):
       display_text_info(self.text, self.entry, self.week_info_list, self.step_length)
    
    def return_text_variable(self):
        return self.text


# TODO 实时显示相关组件数据
def display_text_info(text, entry, week_info_list, step_length):
    text.delete(0.0, END)
    for index in range(len(week_info_list) / step_length + 2):
        if index == 0:
            text.insert(INSERT, '\n' + ' '.join(week_info_list[0:(index + 1) * step_length]))
        else:
            text.insert(INSERT, '\n' + ' '.join(
                week_info_list[index * step_length:(index + 1) * step_length]))

    entry_input_string_list = entry.get().strip().split(',')
    entry_input_string_list = [ele for ele in entry_input_string_list if len(ele) != 0]

    if len(entry_input_string_list) == 0:
        text.insert(END, '\n' + 'You are not choose any week num!!!\n')
    else:
        for index in range(len(entry_input_string_list) / step_length + 2):
            if index == 0:
                text.insert(END, '\n' + 'Your choose as the following:\n' + ' '.join(
                    entry_input_string_list[0:(index + 1) * step_length]))
            else:
                text.insert(END, '\n' + ' '.join(
                    entry_input_string_list[index * step_length:(index + 1) * step_length]))


# TODO  检测所填入的数据的有效性 格式检查以及值有效检查
def check_week_valid(week_info_list, url_info_list, logger):
    # TODO 如果选择的周不在所有的周里面说明是不合法的周数据  无效值url信息集合judge_set
    judge_set = set(week_info_list) - set(url_info_list)

    if judge_set:
        logger.print_message('The invalid url info list is:\t%s' % list(judge_set), _file_name)
        [ week_info_list.remove(url) for url in judge_set ]

    week_compile = re.compile('\d+W{2}\d+')
    week_compile_object_list = [ re.search(week_compile, week) for  week in week_info_list ]
    week_length_list = [ len(week) for week in week_info_list ]

    # TODO 若数据有效则返回, 否则去除无效的数据，返回有效的数据
    if week_compile_object_list and all(week_compile_object_list) and week_length_list.count(week_length_list[0]) == len(week_length_list) and week_length_list[0] == 8:
        return week_info_list
    else:
        return [ week for week in week_info_list if re.search(week_compile, week) and len(week) == 8 ]


# TODO 检测日期周配置窗口是否关闭 关闭则保存当前日期周配置
def week_callback(win, entry_input_string_list, logger):
    logger.print_message('entry_input_string_list:\t%s' % entry_input_string_list, _file_name)
    # TODO 保存日期值
    if not os.path.exists(SRC_WEEK_DIR):
        os.makedirs(SRC_WEEK_DIR)
    with open(SRC_WEEK_DIR + os.sep + 'week_info.txt', 'w') as f:
        if entry_input_string_list:
            f.write(','.join(entry_input_string_list))
        else:
            f.write('')

    win.eval('::ttk::CancelRepeat')
    win.destroy()
    logger.print_message('The week windows of configuration is closed!', _file_name)


# TODO 配置周数据界面 choose_weeks_var为YES时触发
def week_gui_config(purl_bak_string, logger):
    # TODO 获取对应周url信息时需要更新url列表
    logger.print_message('>>>>>>>>>> Update [ %s ] Html url info Start <<<<<<<<<<' % purl_bak_string, _file_name)
    get_url_object = GetUrlFromHtml(html_url_pre='https://dcg-oss.intel.com/ossreport/auto/', logger=logger)
    get_url_object.get_all_type_data(purl_bak_string, get_only_department=True)
    logger.print_message('>>>>>>>>>> Update [ %s ] Html url info Finished <<<<<<<<<<' % purl_bak_string, _file_name)

    url_list = get_url_list_by_keyword(purl_bak_string, 'Silver')
    effective_week_info_list = []
    for url in url_list:
        url_sep_list = url.split('/')
        week_info = url_sep_list[-2]
        effective_week_info = week_info.replace('%20', '')
        effective_week_info_list.append(effective_week_info)

    effective_week_info_list.sort(reverse=True)
    week_list_length = len(effective_week_info_list)

    tk = Tk()
    step_length = 5

    if week_list_length >= 40:
        step_length = 6

    label_choose = Label(tk, text='Select the number of weeks', font=("Calibri", 12))
    label_choose.grid(row=week_list_length / step_length + 2, column=0, columnspan=2)
    entry = Entry(tk, width=90, font=("Calibri", 10))

    frame = MainFrame(tk, week_info_list=effective_week_info_list, entry=entry)
    frame.grid(row=week_list_length / step_length + 3, column=0, columnspan=step_length, sticky=N + S + E + W)
    # TODO 返回Text以便实时显示数据
    frame_text = frame.return_text_variable()

    # TODO 获取所有的url信息列表
    all_url_list = get_url_list_by_keyword(purl_bak_string=purl_bak_string, back_keyword='Silver')
    url_info_list = [re.split('\D+', url.split('/')[-2])[0] + 'WW' + re.split('\D+', url.split('/')[-2])[-1] for url in all_url_list]

    # TODO 多个数据之间自动填充分隔符
    def auto_func(event):
        data = entry.get()
        if len(data.strip()) != 0:
            entry.delete(0, END)
            data_list = re.split('\W+', data)
            data_list = [ ele for ele in data_list if len(ele) != 0 ]
            data_list = list(set(data_list))

            global week_input_string_list
            week_input_string_list = data_list

            # TODO  检测所填入的数据的有效性, 并返回有效的周列表
            week_input_string_list = check_week_valid(data_list, url_info_list, logger)
            if data_list and cmp(week_input_string_list, data_list) != 0:
                # TODO 去除无效的数据 显示有效的数据 默认倒序排序
                insert_week_string = ','.join(sorted(week_input_string_list, reverse=True))
                if insert_week_string:
                    entry.insert(0, insert_week_string + ',')
                    # raise ValueError('Please check if the week information you choose is valid!!!')
            elif data_list and cmp(week_input_string_list, data_list) == 0:
                data_list.sort(reverse=True)
                entry.insert(0, ','.join(data_list) + ',')
            else:
                entry.insert(0, '')

        # TODO 捕捉事件实时显示数据
        display_text_info(frame_text, entry, url_info_list, step_length)

    # TODO 绑定失去鼠标离开焦点事件
    entry.bind("<Leave>", auto_func)
    entry.grid(row=week_list_length / step_length + 2, column=2, columnspan=2)

    tk.protocol("WM_DELETE_WINDOW", lambda x=tk: week_callback(tk, week_input_string_list, logger))
    tk.bind('<Escape>', lambda e: tk.destroy())

    tk.mainloop()


if __name__ == '__main__':
    # TODO 类型: Bakerville or Purley-FPGA
    from machine_scripts.custom_log import WorkLogger
    import time

    log_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
    _logger = WorkLogger('create_gui_log', log_time=log_time)
    purl_bak_string = main(_logger)
    # week_gui_config('Purley-FPGA')
    print purl_bak_string

    # flat, groove, raised, ridge, solid, or sunken  控制按钮的形态  relief

    # beige, khaki, palegreen, palevioletred, turquoise, plum, sandybrown,   seashell, skyblue, yellowgreen, yellow, green, peru
    # color_list = ['beige', 'khaki', 'palegreen', 'palevioletred', 'turquoise', 'plum', 'sandybrown', 'seashell',
    #               'skyblue',
    #               'yellowgreen', 'yellow', 'green', 'peru', 'pink', 'grey', 'orange', ]



# TODO      1、周日期配置界面显示问题 上面应该显示全部  Done
# TODO      2、关掉周日期配置界面自动保存             Done
# TODO      3、邮件地址出现乱码 增加格式控制          Done
# TODO      4、配置文件当前配置按项目分开，每次加载当前项目对应的配置 Done

# TODO      5、mapping和save-miss表日期对齐          Done
# TODO      6、发送邮件时不对邮件地址检查但是会保存邮件地址 Done
# TODO      7、更改excel文件名 在名称中加入最新日期以及最新日期的index信息 Done
# TODO      8、在选择周日期时增加选择Silver、Gold以及BKC三种类型的功能 Done
