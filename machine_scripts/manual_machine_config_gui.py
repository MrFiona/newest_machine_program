#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-07-12 14:28
# Author  : MrFiona
# File    : manual_machine_config_gui.py
# Software: PyCharm Community Edition

from __future__ import absolute_import


import os
import re
import ttk
from tkMessageBox import askyesno
from Tkinter import Tk, Button, Label, Entry, END, mainloop, StringVar
from tkFileDialog import askopenfilename
from tkMessageBox import showwarning

from machine_scripts.machine_config import MachineConfig
from setting_global_variable import MANUAL_CONFIG_FILE_PATH

chart_software_var, chart_new_var, chart_exist_var, chart_closed_var, chart_total_var, chart_save_test_var, chart_save_effort_var, \
chart_miss_var  = '', '', '', '', '', '', '', ''
chart_software_numberChosen1, chart_new_numberChosen2, chart_exist_numberChosen3, chart_closed_numberChosen4, chart_total_numberChosen5, \
chart_save_test_numberChosen6, chart_save_effort_numberChosen7, chart_miss_numberChosen8 = '', '', '', '', '', '', '', ''


# TODO 文件选择
def template_choose(template_file_path, week_choose):
    filename = askopenfilename(initialdir=os.getcwd(), filetypes=(("excel file", "*.xlsx;*.xls;*.csv"),))
    # TODO 此处不需要模板验证
    if len(filename) != 0:
        template_file_name = os.path.split(filename)[1]
        newest_week_string_list = template_file_name.split('_')
        if len(newest_week_string_list) < 11:
            week_choose.delete(0, END)
            template_file_path.delete(0, END)
            raise UserWarning("template's file name is illegal!!!")
        else:
            template_file_path.delete(0, END)
            template_file_path.insert(0, filename)
            week_choose.delete(0, END)
            week_choose.insert(0, newest_week_string_list[2])


# TODO 检查输入信息的有效性
def check_week_template_info(root, week_choose, template_file_path, email_server, email_send, email_receive):
    email_server_flag, email_send_flag, email_receive_flag, template_file_flag, week_info_flag = True, True, True, True, True
    email_compile = re.compile(pattern='\w+.@intel.com')
    email_server_address, email_send_address, email_receive_address = email_server.get(), email_send.get(), email_receive.get()

    if len(email_server_address.strip()) == 0 or not email_server_address.endswith('intel.com'):
        email_server_flag = False
        showwarning(title='email info check gui', message='The server address is illegal')

    if not re.search(email_compile, email_send_address.strip()) or not email_send_address.endswith('intel.com'):
        email_send_flag = False
        showwarning(title='email info check gui', message="The sender address is illegal")

    for receive_address in email_receive_address.strip().split(','):
        if not re.search(email_compile, receive_address.strip()) or not receive_address.endswith('intel.com'):
            email_receive_flag = False
            showwarning(title='email info check gui', message='The Recipient address is illegal')

    week_info = week_choose.get().strip()
    template_info = template_file_path.get()
    week_obj = re.match('\d{4}WW\d{2}', week_info)
    if not week_obj:
        week_choose.delete(0, END)
        showwarning(title='week info check gui', message='Please enter the correct week information format')
        week_info_flag = False
        # week_choose.insert(0, 'Input Format Example : 2017WW12')

    if not os.path.exists(template_info):
        showwarning(title='template info check gui', message='The template file path does not exist')
        template_file_flag = False
        template_file_path.delete(0, END)
    else:
        # TODO 判断是否是个文件
        if os.path.isfile(template_info):
            # TODO 当前目录下则填充全路径
            if template_info.strip() in os.listdir(os.path.split(os.getcwd())[0]):
                template_file_path.delete(0, END)
                template_file_path.insert(0, os.path.split(os.getcwd())[0] + os.sep + template_info.strip())
            template_file_flag = True
        else:
            showwarning(title='template info check gui', message='The path of the file you entered is a directory, not a file')
            template_file_flag = False
            template_file_path.delete(0, END)

    # TODO 保存到配置文件
    if email_server_flag and email_send_flag and email_receive_flag and template_file_flag and template_file_flag and week_info_flag:
        conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
        conf.modify_node_value('manual_machine_info', 'week_info', week_choose.get().strip())
        conf.modify_node_value('manual_machine_info', 'template_info', template_file_path.get().strip())
        conf.modify_node_value('server_address', 'server_address', email_server.get().strip())
        conf.modify_node_value('from_address', 'from_address', email_send.get().strip())
        conf.modify_node_value('receive_address', 'receive_address', email_receive.get().strip())
        root.destroy()


# TODO 加载配置里的图表参数值
def manual_load_default_chart_config():
    conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
    default_display_software = conf.get_node_info('manual_chart_config', 'display_software')
    default_display_new = conf.get_node_info('manual_chart_config', 'display_new')
    default_display_existing = conf.get_node_info('manual_chart_config', 'display_existing')
    default_display_closed = conf.get_node_info('manual_chart_config', 'display_closed')
    default_display_total = conf.get_node_info('manual_chart_config', 'display_total')
    default_display_save_test = conf.get_node_info('manual_chart_config', 'display_save_test')
    default_display_save_effort = conf.get_node_info('manual_chart_config', 'display_save_effort')
    default_display_miss = conf.get_node_info('manual_chart_config', 'display_miss')


    chart_software_numberChosen1.set('YES' if default_display_software == 'YES' else 'NO')
    chart_new_numberChosen2.set('YES' if default_display_new == 'YES' else 'NO')
    chart_exist_numberChosen3.set('YES' if default_display_existing == 'YES' else 'NO')
    chart_closed_numberChosen4.set('YES' if default_display_closed == 'YES' else 'NO')
    chart_total_numberChosen5.set('YES' if default_display_total == 'YES' else 'NO')
    chart_save_test_numberChosen6.set('YES' if default_display_save_test == 'YES' else 'NO')
    chart_save_effort_numberChosen7.set('YES' if default_display_save_effort == 'YES' else 'NO')
    chart_miss_numberChosen8.set('YES' if default_display_miss == 'YES' else 'NO')


# TODO 将当前界面的值保存为配置参数值功能函数
def manual_current_config_save_as_default():
    conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
    current_display_software = chart_software_var.get()
    current_display_new = chart_new_var.get()
    current_display_existing = chart_exist_var.get()
    current_display_closed = chart_closed_var.get()
    current_display_total = chart_total_var.get()
    current_display_save_test = chart_save_test_var.get()
    current_display_save_effort = chart_save_effort_var.get()
    current_display_miss = chart_miss_var.get()

    conf.modify_node_value('manual_chart_config', 'display_software', current_display_software)
    conf.modify_node_value('manual_chart_config', 'display_new', current_display_new)
    conf.modify_node_value('manual_chart_config', 'display_existing', current_display_existing)
    conf.modify_node_value('manual_chart_config', 'display_closed', current_display_closed)
    conf.modify_node_value('manual_chart_config', 'display_total', current_display_total)
    conf.modify_node_value('manual_chart_config', 'display_total', current_display_save_test)
    conf.modify_node_value('manual_chart_config', 'display_total', current_display_save_effort)
    conf.modify_node_value('manual_chart_config', 'display_total', current_display_miss)


# TODO 加载图表配置参数值
def manual_chart_load_default():
    default_load_flag = askyesno('Load the default chart configuration window',
                                 'Are you sure you need to load the default chart configuration?')
    if default_load_flag:
        manual_load_default_chart_config()


# TODO 将当前界面的值保存为配置参数值
def manual_chart_save_default():
    default_save_flag = askyesno('Save the default chart configuration window',
                                 'Are you sure you need to save the current chart configuration as the default chart configuration?')
    if default_save_flag:
        manual_current_config_save_as_default()


# TODO 图表配置界面
def manual_machine_chart_gui():
    chart_tk = Tk()
    chart_tk.title('manual chart config gui')
    conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
    current_display_software = conf.get_node_info('manual_chart_config', 'display_software')
    current_display_new = conf.get_node_info('manual_chart_config', 'display_new')
    current_display_existing = conf.get_node_info('manual_chart_config', 'display_existing')
    current_display_closed = conf.get_node_info('manual_chart_config', 'display_closed')
    current_display_total = conf.get_node_info('manual_chart_config', 'display_total')
    current_display_save_test = conf.get_node_info('manual_chart_config', 'display_save_test')
    current_display_save_effort = conf.get_node_info('manual_chart_config', 'display_save_effort')
    current_display_miss = conf.get_node_info('manual_chart_config', 'display_miss')

    label1 = Label(chart_tk, text="Software Change", font=("Calibri", 12), background='gray')
    label2 = Label(chart_tk, text="New Sighting", font=("Calibri", 12), background='gray')
    label3 = Label(chart_tk, text="Existing Sighting", font=("Calibri", 12), background='gray')
    label4 = Label(chart_tk, text="Closed Sighting", font=("Calibri", 12), background='gray')
    label5 = Label(chart_tk, text="Total Sighting", font=("Calibri", 12), background='gray')
    label6 = Label(chart_tk, text="Saved Test Case", font=("Calibri", 12), background='gray')
    label7 = Label(chart_tk, text="Saved Efforts", font=("Calibri", 12), background='gray')
    label8 = Label(chart_tk, text="Missed Sighting", font=("Calibri", 12), background='gray')

    label1.grid(row=1, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label2.grid(row=2, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label3.grid(row=3, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label4.grid(row=4, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label5.grid(row=5, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label6.grid(row=6, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label7.grid(row=7, column=0, columnspan=5, padx=20, pady=5, sticky='E')
    label8.grid(row=8, column=0, columnspan=5, padx=20, pady=5, sticky='E')

    global chart_software_var, chart_new_var, chart_exist_var, chart_closed_var, chart_total_var, chart_save_test_var, chart_save_effort_var, chart_miss_var
    global chart_software_numberChosen1, chart_new_numberChosen2, chart_exist_numberChosen3, chart_closed_numberChosen4, chart_total_numberChosen5, \
        chart_save_test_numberChosen6, chart_save_effort_numberChosen7, chart_miss_numberChosen8

    chart_software_var = StringVar()
    chart_new_var = StringVar()
    chart_exist_var = StringVar()
    chart_closed_var = StringVar()
    chart_total_var = StringVar()
    chart_save_test_var = StringVar()
    chart_save_effort_var = StringVar()
    chart_miss_var = StringVar()

    chart_software_numberChosen1 = ttk.Combobox(chart_tk, textvariable=chart_software_var, width=30, state='readonly')
    chart_new_numberChosen2 = ttk.Combobox(chart_tk, width=30, textvariable=chart_new_var, state='readonly')
    chart_exist_numberChosen3 = ttk.Combobox(chart_tk, width=30, textvariable=chart_exist_var, state='readonly')
    chart_closed_numberChosen4 = ttk.Combobox(chart_tk, width=30, textvariable=chart_closed_var, state='readonly')
    chart_total_numberChosen5 = ttk.Combobox(chart_tk, width=30, textvariable=chart_total_var, state='readonly')
    chart_save_test_numberChosen6 = ttk.Combobox(chart_tk, width=30, textvariable=chart_save_test_var, state='readonly')
    chart_save_effort_numberChosen7 = ttk.Combobox(chart_tk, width=30, textvariable=chart_save_effort_var, state='readonly')
    chart_miss_numberChosen8 = ttk.Combobox(chart_tk, width=30, textvariable=chart_miss_var, state='readonly')

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

    button1 = Button(chart_tk, text='Load Default', font=("Calibri", 12), width=14, background='peru',
                     command=manual_chart_load_default, activeforeground='blue', activebackground='turquoise')
    button2 = Button(chart_tk, text='Save Default', font=("Calibri", 12), width=14, background='green',
                     command=manual_chart_save_default, activeforeground='blue', activebackground='palegreen')
    button1.grid(row=9, column=0, padx=20, pady=15, sticky='W')
    button2.grid(row=9, column=6, padx=20, pady=15, sticky='E')

    mainloop()


# TODO 手动配置界面主程序
def manual_machine_config_gui_main():
    manual_tk = Tk()
    manual_tk.title('manual machine gui')
    week_label = Label(manual_tk, text='week choose', font=("Calibri", 12),background='turquoise')
    week_label.grid(row=5, column=0, columnspan=5, padx=20, pady=15, sticky='E')
    week_choose = Entry(manual_tk, font=("Calibri", 12), width=40)
    week_choose.grid(row=5, column=5, columnspan=5, padx=20, pady=15, sticky='E')
    # week_choose.insert(0, 'Input Format Example : 2017WW12')

    template_file_path = Entry(manual_tk, font=("Calibri", 12), width=40)
    template_file_path.grid(row=4, column=5, columnspan=5, padx=20, pady=15, sticky='E')
    # template_file_path.insert(0, 'Choose Select the appropriate excel template file')
    template_button = Button(manual_tk, text='Excel Template', font=("Calibri", 12), background='seashell',
                             command=lambda : template_choose(template_file_path, week_choose))
    template_button.grid(row=4, column=0, columnspan=5, padx=20, pady=15, sticky='E')

    label1 = Label(manual_tk, text="Mail Server", font=("Calibri", 12), background='beige')
    label2 = Label(manual_tk, text="Sender Email", font=("Calibri", 12), background='khaki')
    label3 = Label(manual_tk, text="Recipient Email", font=("Calibri", 12), background='palegreen')

    label1.grid(row=1, column=0, columnspan=5, padx=20, pady=15, sticky='E')
    label2.grid(row=2, column=0, columnspan=5, padx=20, pady=15, sticky='E')
    label3.grid(row=3, column=0, columnspan=5, padx=20, pady=15, sticky='E')

    email_server = Entry(manual_tk, font=("Calibri", 12), width=40)
    email_send = Entry(manual_tk, font=("Calibri", 12), width=40)
    email_receive = Entry(manual_tk, font=("Calibri", 12), width=40)

    email_server.grid(row=1, column=5, columnspan=5, padx=20, pady=15)
    email_send.grid(row=2, column=5, columnspan=5, padx=20, pady=15)
    email_receive.grid(row=3, column=5, columnspan=5, padx=20, pady=15)

    # TODO 邮件默认加载当前配置信息
    conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
    default_email_send = conf.get_node_info('from_address', 'from_address')
    default_email_receive = conf.get_node_info('receive_address', 'receive_address')

    email_server.insert(0, 'smtp.intel.com')
    email_send.insert(0, default_email_send)
    email_receive.insert(0, default_email_receive)

    manual_tk.protocol("WM_DELETE_WINDOW", lambda x=email_server, y=email_send, z=email_receive:
                            check_week_template_info(manual_tk, week_choose, template_file_path, email_server, email_send, email_receive))
    mainloop()

    # TODO 图表配置界面
    manual_machine_chart_gui()



if __name__ == '__main__':
    manual_machine_config_gui_main()