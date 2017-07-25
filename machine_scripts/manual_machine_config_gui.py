#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-07-12 14:28
# Author  : MrFiona
# File    : manual_machine_config_gui.py
# Software: PyCharm Community Edition


import os
import re
from Tkinter import Tk, Button, Label, Entry, END, mainloop
from tkFileDialog import askopenfilename
from tkMessageBox import showwarning

from machine_config import MachineConfig
from setting_global_variable import MANUAL_CONFIG_FILE_PATH


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


if __name__ == '__main__':
    manual_machine_config_gui_main()