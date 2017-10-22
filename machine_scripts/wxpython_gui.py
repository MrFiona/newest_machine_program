#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-10-20 13:17
# Author  : MrFiona
# File    : wxpython_gui.py
# Software: PyCharm Community Edition


import os
import re
import wx
from machine_scripts.machine_config import MachineConfig
from setting_global_variable import CONFIG_FILE_PATH, SRC_WEEK_DIR
from machine_scripts.get_all_html import GetUrlFromHtml
from machine_scripts.public_use_function import get_interface_config, get_url_list_by_keyword, judge_get_config
from machine_scripts.common_interface_branch_func import obtain_prefix_project_name
_file_name = os.path.split(__file__)[1]



#TODO 实时显示相关组件数据
def display_text_info(text, entry, week_info_list, step_length):
    text.Clear()
    for index in range(len(week_info_list) / step_length + 2):
        if index == 0:
            text.WriteText('\n' + ' '.join(week_info_list[0:(index + 1) * step_length]))
        else:
            text.WriteText('\n' + ' '.join(
                week_info_list[index * step_length:(index + 1) * step_length]))

    entry_input_string_list = entry.GetValue().strip().split(',')
    entry_input_string_list = [ele for ele in entry_input_string_list if len(ele) != 0]

    if len(entry_input_string_list) == 0:
        text.AppendText('\n' + 'You are not choose any week num!!!\n')
    else:
        for index in range(len(entry_input_string_list) / step_length + 2):
            if index == 0:
                text.AppendText('\n' + 'Your choose as the following:\n' + ' '.join(
                    entry_input_string_list[0:(index + 1) * step_length]))
            else:
                text.AppendText('\n' + ' '.join(
                    entry_input_string_list[index * step_length:(index + 1) * step_length]))

#TODO  检测所填入的数据的有效性 格式检查以及值有效检查
def check_week_valid(week_info_list, url_info_list, logger):
    #TODO 如果选择的周不在所有的周里面说明是不合法的周数据  无效值url信息集合judge_set
    judge_set = set(week_info_list) - set(url_info_list)

    if judge_set:
        logger.print_message('The invalid url info list is:\t%s' % list(judge_set), _file_name)
        [week_info_list.remove(url) for url in judge_set]

    week_compile = re.compile('\d+W{2}\d+')
    week_compile_object_list = [re.search(week_compile, week) for week in week_info_list]
    week_length_list = [len(week) for week in week_info_list]

    #TODO 若数据有效则返回, 否则去除无效的数据，返回有效的数据
    if week_compile_object_list and all(week_compile_object_list) and week_length_list.count(
            week_length_list[0]) == len(week_length_list) and week_length_list[0] == 8:
        return week_info_list
    else:
        return [week for week in week_info_list if re.search(week_compile, week) and len(week) == 8]


class UserWeekSelectGui(wx.Frame):
    def __init__(self, purl_bak_string, logger, week_info_list=None, step_length=5):
        self.week_info_list = week_info_list
        self.step_length = step_length
        self.purl_bak_string = purl_bak_string
        self.logger = logger
        self.url_info_list = []
        self.week_input_string_list = []

        if len(self.week_info_list) >= 40:
            self.step_length = 6

        wx.Frame.__init__(self, None, wx.ID_ANY, "%s User Configuration Gui Interface" % self.purl_bak_string, size=(900, 535))
        panel = wx.Panel(self, wx.ID_ANY)

        self.get_week_string_list()

        self.wx_font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.select_week_label = wx.StaticText(panel, wx.ID_ANY, label='select the number of week', pos=(10, 10))
        self.select_week_label.SetFont(self.wx_font)

        self.select_week_text = wx.TextCtrl(panel, pos=(230, 7), size=(645, -1))
        self.select_week_text.SetBackgroundColour('turquoise')

        self.Contents = wx.TextCtrl(panel, pos=(10, 40), size=(865, 410), style=wx.TE_MULTILINE | wx.HSCROLL)
        self.Contents.Bind(wx.EVT_LEAVE_WINDOW, self.sort_input_week_string_event)

        self.display_button = wx.Button(panel, wx.ID_ANY, label='Display', pos=(9, 460), size=(70, 30))
        self.clear_button = wx.Button(panel, wx.ID_ANY, label='Clear', pos=(806, 460), size=(70, 30))

        self.display_button.SetForegroundColour('red')
        self.clear_button.SetForegroundColour('blue')

        self.display_button.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        self.clear_button.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        self.display_button.SetToolTip("显示最新的项目周数")
        self.clear_button.SetToolTip("清除界面项目周数")
        self.display_button.Bind(wx.EVT_BUTTON, self.show_info)
        self.clear_button.Bind(wx.EVT_BUTTON, self.clear_info)

        self.Bind(wx.EVT_WINDOW_DESTROY, self.window_close_save_week_info_event)

        #todo 显示界面
        self.Centre()
        self.Layout()
        self.Show()

    def clear_info(self, event):
        self.Contents.Clear()

    def show_info(self, event):
        display_text_info(self.Contents, self.select_week_text, self.week_info_list, self.step_length)

    def window_close_save_week_info_event(self, event):
        self.logger.print_message('week_input_string_list:\t%s' % self.week_input_string_list, _file_name)
        #TODO 保存日期值
        if not os.path.exists(SRC_WEEK_DIR):
            os.makedirs(SRC_WEEK_DIR)
        with open(SRC_WEEK_DIR + os.sep + 'week_info.txt', 'w') as f:
            if self.week_input_string_list:
                f.write(','.join(self.week_input_string_list))
            else:
                f.write('')

        self.Destroy()

    def sort_input_week_string_event(self, event):
        data = self.select_week_text.GetValue()
        if len(data.strip()) != 0:
            self.select_week_text.Clear()
            data_list = re.split('\W+', data)
            data_list = [ele for ele in data_list if len(ele) != 0]
            data_list = list(set(data_list))

            self.week_input_string_list = data_list

            #TODO  检测所填入的数据的有效性, 并返回有效的周列表
            week_input_string_list = check_week_valid(data_list, self.url_info_list, self.logger)
            if data_list and cmp(week_input_string_list, data_list) != 0:
                # TODO 去除无效的数据 显示有效的数据 默认倒序排序
                insert_week_string = ','.join(sorted(week_input_string_list, reverse=True))
                if insert_week_string:
                    self.select_week_text.WriteText(insert_week_string + ',')
            elif data_list and cmp(week_input_string_list, data_list) == 0:
                data_list.sort(reverse=True)
                self.select_week_text.WriteText(','.join(data_list) + ',')
            else:
                self.select_week_text.WriteText('')

        #TODO 捕捉事件实时显示数据
        display_text_info(self.Contents, self.select_week_text, self.url_info_list, self.step_length)

    def return_text_variable(self):
        return self.Contents

    def get_week_string_list(self):
        #TODO 获取所有的url信息列表
        all_url_list = get_url_list_by_keyword(purl_bak_string=self.purl_bak_string, back_keyword='Silver')
        self.url_info_list = [re.split('\D+', url.split('/')[-2])[0] + 'WW' + re.split('\D+', url.split('/')[-2])[-1] for url in all_url_list]


#TODO 配置周数据界面 choose_weeks_var为YES时触发
def week_gui_config(main_window, purl_bak_string, logger):
    #TODO 获取对应周url信息时需要更新url列表
    logger.print_message('>>>>>>>>>> Generates the latest selectable week list info for the [ %s ] Start <<<<<<<<<<' % purl_bak_string, _file_name)
    get_url_object = GetUrlFromHtml(html_url_pre='https://dcg-oss.intel.com/ossreport/auto/', logger=logger)
    get_url_object.get_all_type_data(purl_bak_string, get_only_department=True)
    logger.print_message('>>>>>>>>>> Generates the latest selectable week list info for the [ %s ] Finished <<<<<<<<<<' % purl_bak_string, _file_name)

    url_list = get_url_list_by_keyword(purl_bak_string, 'Silver')
    effective_week_info_list = []
    for url in url_list:
        url_sep_list = url.split('/')
        week_info = url_sep_list[-2]
        effective_week_info = week_info.replace('%20', '')
        effective_week_info_list.append(effective_week_info)

    effective_week_info_list.sort(reverse=True)

    app = wx.App()
    UserWeekSelectGui(purl_bak_string, logger, week_info_list=effective_week_info_list)
    app.MainLoop()

#todo 项目配置主界面
class ProjectConfigParameterGui(wx.Frame):
    def __init__(self, name, logger):
        wx.Frame.__init__(self, None, wx.ID_ANY,"%s User Configuration Gui Interface" % name, size=(930,700))
        self.name = name
        self.logger = logger

        #todo 获取初始化界面配置参数
        self.get_init_config_info('current')
        #todo 界面配置函数
        self.program_parameter_interface()
        # todo 加载初始化界面配置参数
        self.load_init_config_info()

        #todo 显示界面
        self.Centre()
        self.Layout()
        self.Show()

    #todo 界面配置函数
    def program_parameter_interface(self):
        self.sampleList = ['YES', 'NO']
        self.mode_value_list = ['online', 'offline']
        wx_font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        wx_font1 = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        #todo 设置鼠标指针的形式
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        #todo 邮件配置部分
        box_email = wx.StaticBox(self, -1, label='Email Config', pos=(10, -1), size=(390, 220))
        box_email.SetFont(wx_font1)
        box_email.SetForegroundColour('orange')

        self.mail_server_label = wx.StaticText(self, label='Mail Server', pos=(30, 30), size=(-1, -1))
        self.mail_server_label.SetFont(wx_font)
        self.mail_server_text = wx.TextCtrl(self, pos=(180, 30), size=(200, -1))
        self.mail_server_text.SetBackgroundColour('turquoise')

        self.sender_email_label = wx.StaticText(self, label='Sender Email', pos=(30, 80))
        self.sender_email_label.SetFont(wx_font)
        self.sender_email_text = wx.TextCtrl(self, pos=(180, 80), size=(200, -1))
        self.sender_email_text.SetBackgroundColour('turquoise')

        self.receive_email_label = wx.StaticText(self, label='Recipient Email', pos=(30, 130))
        self.receive_email_label.SetFont(wx_font)
        self.receive_email_text = wx.TextCtrl(self, pos=(180, 130), size=(200, -1))
        self.receive_email_text.SetBackgroundColour('turquoise')

        self.send_email_flag_label = wx.StaticText(self, label='Send Email', pos=(30, 180))
        self.send_email_flag_label.SetFont(wx_font)
        self.send_email_flag_text = wx.ComboBox(self, pos=(180, 180), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.send_email_flag_text.SetBackgroundColour('wheat')

        #todo 文件配置部分
        box_file = wx.StaticBox(self, -1, label='File Config', pos=(430, -1), size=(470, 220))
        box_file.SetFont(wx_font1)
        box_file.SetForegroundColour('orange')

        self.reacquire_data_label = wx.StaticText(self, label='Retrieve Data', pos=(450, 30))
        self.reacquire_data_label.SetFont(wx_font)
        self.reacquire_data_choose = wx.ComboBox(self, pos=(610, 30), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.reacquire_data_choose.SetBackgroundColour('wheat')

        self.review_file_label = wx.StaticText(self, label='Review Excel File', pos=(450, 80))
        self.review_file_label.SetFont(wx_font)
        self.review_file_choose = wx.ComboBox(self, pos=(610, 80), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.review_file_choose.SetBackgroundColour('wheat')

        self.max_time_label = wx.StaticText(self, label='Maximum Time', pos=(450, 130))
        self.max_time_label.SetFont(wx_font)
        self.max_time_text = wx.TextCtrl(self, pos=(610, 130), size=(200, -1))
        self.max_time_text.SetBackgroundColour('turquoise')
        self.time_sep_text_label = wx.StaticText(self, label='minute(s)', pos=(815, 130))
        self.time_sep_text_label.SetFont(wx_font)

        #todo 图标配置部分
        box_chart = wx.StaticBox(self, -1, label='Chart Config', pos=(10, 230), size=(390, 420))
        box_chart.SetFont(wx_font1)
        box_chart.SetForegroundColour('orange')

        self.software_change_label = wx.StaticText(self, label='Software Change', pos=(30, 260))
        self.software_change_label.SetFont(wx_font)
        self.software_change_choose = wx.ComboBox(self, pos=(180, 260), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.software_change_choose.SetBackgroundColour('wheat')

        self.new_sighting_label = wx.StaticText(self, label='New Sighting', pos=(30, 310))
        self.new_sighting_label.SetFont(wx_font)
        self.new_sighting_choose = wx.ComboBox(self, pos=(180, 310), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.new_sighting_choose.SetBackgroundColour('wheat')

        self.exist_sighting_label = wx.StaticText(self, label='Existing Sighting', pos=(30, 360))
        self.exist_sighting_label.SetFont(wx_font)
        self.exist_sighting_choose = wx.ComboBox(self, pos=(180, 360), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.exist_sighting_choose.SetBackgroundColour('wheat')

        self.closed_sighting_label = wx.StaticText(self, label='Closed Sighting', pos=(30, 410))
        self.closed_sighting_label.SetFont(wx_font)
        self.closed_sighting_choose = wx.ComboBox(self, pos=(180, 410), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.closed_sighting_choose.SetBackgroundColour('wheat')

        self.total_sighting_label = wx.StaticText(self, label='Total Sighting', pos=(30, 460))
        self.total_sighting_label.SetFont(wx_font)
        self.total_sighting_choose = wx.ComboBox(self, pos=(180, 460), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.total_sighting_choose.SetBackgroundColour('wheat')

        self.save_test_case_label = wx.StaticText(self, label='Saved Test Case', pos=(30, 510))
        self.save_test_case_label.SetFont(wx_font)
        self.save_test_case_choose = wx.ComboBox(self, pos=(180, 510), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.save_test_case_choose.SetBackgroundColour('wheat')

        self.save_efforts_label = wx.StaticText(self, label='Saved Efforts', pos=(30, 560))
        self.save_efforts_label.SetFont(wx_font)
        self.save_efforts_choose = wx.ComboBox(self, pos=(180, 560), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.save_efforts_choose.SetBackgroundColour('wheat')

        self.miss_sighting_label = wx.StaticText(self, label='Missed Sighting', pos=(30, 610))
        self.miss_sighting_label.SetFont(wx_font)
        self.miss_sighting_choose = wx.ComboBox(self, pos=(180, 610), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.miss_sighting_choose.SetBackgroundColour('wheat')

        #todo Excel模板配置
        box_template = wx.StaticBox(self, -1, label='Template Config', pos=(430, 230), size=(470, 100))
        box_template.SetFont(wx_font1)
        box_template.SetForegroundColour('orange')

        self.excel_template_button = wx.Button(self, -1, label='Template File', pos=(450, 270), size=(125, 40))
        self.excel_template_button.SetForegroundColour('grey')
        self.excel_template_button.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        self.excel_template_button.SetToolTip("设置Excel模板")
        self.excel_template_text = wx.TextCtrl(self, pos=(610, 278), size=(270, -1))
        self.excel_template_text.SetBackgroundColour('turquoise')

        #todo 其他配置
        box_other = wx.StaticBox(self, -1, label='Other Config', pos=(430, 340), size=(470, 125))
        box_other.SetFont(wx_font1)
        box_other.SetForegroundColour('orange')

        self.mode_setting_label = wx.StaticText(self, label='Offline mode settings', pos=(450, 370))
        self.mode_setting_label.SetFont(wx_font)
        self.mode_setting_choose = wx.ComboBox(self, pos=(630, 370), size=(200, -1), choices=self.mode_value_list, style=wx.CB_DROPDOWN)
        self.mode_setting_choose.SetBackgroundColour('wheat')

        self.select_week_label = wx.StaticText(self, label='Choose weeks', pos=(450, 420))
        self.select_week_label.SetFont(wx_font)
        self.select_week_choose = wx.ComboBox(self, pos=(630, 420), size=(200, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
        self.select_week_choose.SetBackgroundColour('wheat')

        #todo 按钮配置
        box_default = wx.StaticBox(self, -1, label='Default Config', pos=(430, 480), size=(470, 100))
        box_default.SetFont(wx_font1)
        box_default.SetForegroundColour('orange')

        self.load_button = wx.Button(self, wx.ID_ANY, label='Load Default', pos=(450, 520), size=(120, 40))
        self.save_button = wx.Button(self, wx.ID_ANY, label='Save Default', pos=(760, 520), size=(120, 40))

        self.load_button.SetForegroundColour('red')
        self.save_button.SetForegroundColour('blue')

        self.load_button.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        self.save_button.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        self.load_button.SetToolTip("加载默认配置")
        self.save_button.SetToolTip("保存当前配置为默认配置")

        #todo 绑定按钮事件
        self.load_button.Bind(wx.EVT_BUTTON, self.load_default_event)
        self.save_button.Bind(wx.EVT_BUTTON, self.save_default_event)
        self.Bind(wx.EVT_CLOSE, self.window_close_event)
        self.send_email_flag_text.Bind(wx.EVT_TEXT, self.send_email_text_frame_event)
        self.excel_template_button.Bind(wx.EVT_BUTTON, self.choose_excel_file_frame_event)

        def onSelect(event):
            print("onSelect")

        menuBar = wx.MenuBar()
        menu = wx.Menu()

        menu.Append(-1, u'撤消(U)')
        menu.AppendSeparator()
        self.menu_select = menu.Append(-1, u'全选(N)\tCtrl+A')  # 快捷键
        self.Bind(wx.EVT_MENU, onSelect, self.menu_select)
        menuBar.Append(menu, u'编辑(F)')
        self.SetMenuBar(menuBar)

    #todo 选择Excel模板文件按钮组件事件响应函数
    def choose_excel_file_frame_event(self, event):
        dialog = wx.FileDialog(self, message='%s项目选择Excel模板文件' % self.name, defaultDir=os.getcwd(), style=wx.ID_OPEN, wildcard=("*.xlsx;*.xls;*.csv"))
        #todo 选择了文件则dialog.ShowModal()为wx.ID_OK否则为 wx.ID_CANCEL
        if dialog.ShowModal() == wx.ID_OK:
            self.excel_template_text.SetValue(dialog.GetPath())

    #todo 是否发送邮件文本框组件事件响应函数
    def send_email_text_frame_event(self, event):
        # todo 根据是否发送邮件标记 来控制邮件相关组件的状态
        if self.send_email_flag_text.GetValue().strip() == 'NO':
            self.mail_server_text.Disable()
            self.sender_email_text.Disable()
            self.receive_email_text.Disable()
        else:
            self.mail_server_text.Enable()
            self.sender_email_text.Enable()
            self.receive_email_text.Enable()

    #todo 主窗口关闭时绑定的事件
    def window_close_event(self, event):
        #todo 窗口关闭前检测参数的有效性
        self.check_gui_parameter_validity()
        #todo 自动将最终的配置信息保存为配置文件的当前配置
        self.current_gui_config_as_current_file_config()
        self.Destroy()
        #todo 显示用户的项目配置信息
        display_config_info(logger=self.logger, purl_bak_string=self.name)

    #todo Load Default按钮对应的事件处理函数
    def load_default_event(self, event):
        print 'load default button pressed!!!'
        self.load_default_config_as_current_config()

    #todo Save Default按钮对应的事件处理函数
    def save_default_event(self, event):
        print 'save default button pressed!!!'
        self.current_config_as_default_config()

    #todo 检查界面参数的合法性
    def check_gui_parameter_validity(self):
        #todo 1、检查邮件合法性
        email_compile = re.compile(pattern='\w+.@intel.com')
        #TODO 不发送邮件时不做检查
        if self.send_email_flag_text.GetValue().strip() == 'YES':
            if len(self.mail_server_text.GetValue().strip()) == 0 or not self.mail_server_text.GetValue().endswith(
                    'intel.com'):
                self.logger.print_message('The email server address is illegal!!!', _file_name, 30)
                raise UserWarning('The email server address is illegal!!!')

            if not re.search(email_compile,
                             self.sender_email_text.GetValue().strip()) or not self.sender_email_text.GetValue().endswith(
                    'intel.com'):
                self.logger.print_message('email sender address is illegal!!!', _file_name, 30)
                raise UserWarning('The email sender address is illegal!!!')

            for receive_address in self.receive_email_text.GetValue().strip().split(','):
                if not re.search(email_compile, receive_address.strip()) or not receive_address.endswith(
                        'intel.com'):
                    self.logger.print_message('email recipient address is illegal!!!', _file_name, 30)
                    raise UserWarning('The email recipient address is illegal!!!')

        #todo 2、检查模板文件路径的合法性
        if not os.path.exists(self.excel_template_text.GetValue().strip()):
            self.logger.print_message('The template file path does not exist', _file_name, 30)
            self.excel_template_text.Clear()
            raise UserWarning('The template file path does not exist')
        else:
            #TODO 判断是否是个文件
            if os.path.isfile(self.excel_template_text.GetValue().strip()):
                #TODO 当前目录下则填充全路径
                if self.excel_template_text.GetValue().strip() in os.listdir(os.getcwd()):
                    self.excel_template_text.Clear()
                    self.excel_template_text.SetValue(
                        os.getcwd() + os.sep + self.excel_template_text.GetValue().strip())
            else:
                self.logger.print_message('The path of the file you entered is a directory, not a file', _file_name,
                                          30)
                self.excel_template_text.Clear()
                raise UserWarning('The path of the file you entered is a directory, not a file')

        #todo 3、检查验证excel的等待时间
        if not len(self.max_time_text.GetValue().strip()) or not self.max_time_text.GetValue().strip().isalnum():
            self.logger.print_message("Verify the file's time setting is invalid! The default value is set to 120",
                                      _file_name, 30)
            self.max_time_text.Clear()
            self.max_time_text.SetValue('120')

    #todo 获取初始化界面配置参数
    def get_init_config_info(self, status):
        conf = MachineConfig(CONFIG_FILE_PATH)
        project_name_sep = obtain_prefix_project_name(self.name)

        if status == 'current':
            #todo 加载邮件配置信息
            self.current_server_address = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_server_address')
            self.current_send_address = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_send_address')
            self.current_receive_address = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_receive_address')
            self.current_send_email_flag = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_send_email_flag')
            #todo 加载文件配置信息
            self.current_reacquire_data_flag = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_reacquire_data_flag')
            self.current_verify_file_flag = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_verify_file_flag')
            self.current_max_waiting_time = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_max_waiting_time')
            #todo 其他配置信息(离线在线模式以及是否自定义选择周)
            self.current_on_off_line_save_flag = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_on_off_line_save_flag', )
            self.current_keep_continuous = conf.get_node_info(self.name + '_real-time_control_parameter_value', 'default_keep_continuous')
        elif status == 'default':
            #todo 加载邮件配置信息
            self.current_server_address = conf.get_node_info(project_name_sep + '_server', 'server_address')
            self.current_send_address = conf.get_node_info(project_name_sep + '_from_address', 'from_address')
            self.current_receive_address = conf.get_node_info(project_name_sep + '_receive_address', 'receive_address')
            self.current_send_email_flag = conf.get_node_info(project_name_sep + '_other_config', 'send_email_flag')
            #todo 加载文件配置信息
            self.current_reacquire_data_flag = conf.get_node_info(project_name_sep + '_other_config', 'reacquire_data_flag')
            self.current_verify_file_flag = conf.get_node_info(project_name_sep + '_other_config', 'verify_file_flag')
            self.current_max_waiting_time = conf.get_node_info(project_name_sep + '_other_config', 'max_waiting_time')
            #todo 其他配置信息(离线在线模式以及是否自定义选择周)
            self.current_on_off_line_save_flag = conf.get_node_info(project_name_sep + '_other_config', 'on_off_line_save_flag')
            self.current_keep_continuous = conf.get_node_info(project_name_sep + '_other_config', 'keep_continuous')

        #todo 加载图表配置信息
        self.current_display_software = get_interface_config('display_software', self.name)
        self.current_display_new = get_interface_config('display_new', self.name)
        self.current_display_existing = get_interface_config('display_existing', self.name)
        self.current_display_closed = get_interface_config('display_closed', self.name)
        self.current_display_total = get_interface_config('display_total', self.name)
        self.current_display_save_test = get_interface_config('display_save_test', self.name)
        self.current_display_save_effort = get_interface_config('display_save_effort', self.name)
        self.current_display_miss = get_interface_config('display_miss', self.name)
        #todo 加载Excel模板配置信息
        self.current_template_file = get_interface_config('template_file', self.name)

    #todo 加载初始化界面配置参数
    def load_init_config_info(self):
        #todo 加载邮件配置信息
        self.mail_server_text.SetValue(self.server_deal_config_value(self.current_server_address))
        self.sender_email_text.SetValue(self.current_send_address)
        self.receive_email_text.SetValue(self.current_receive_address)
        self.send_email_flag_text.SetValue(self.deal_config_value(self.current_send_email_flag))
        #todo 加载文件配置信息
        self.reacquire_data_choose.SetValue(self.deal_config_value(self.current_reacquire_data_flag))
        self.review_file_choose.SetValue(self.deal_config_value(self.current_verify_file_flag))
        self.max_time_text.SetValue(self.time_deal_config_value(self.current_max_waiting_time))
        #todo 加载图表配置信息
        self.software_change_choose.SetValue(self.deal_config_value(self.current_display_software))
        self.new_sighting_choose.SetValue(self.deal_config_value(self.current_display_new))
        self.exist_sighting_choose.SetValue(self.deal_config_value(self.current_display_existing))
        self.closed_sighting_choose.SetValue(self.deal_config_value(self.current_display_closed))
        self.total_sighting_choose.SetValue(self.deal_config_value(self.current_display_total))
        self.save_test_case_choose.SetValue(self.deal_config_value(self.current_display_save_test))
        self.save_efforts_choose.SetValue(self.deal_config_value(self.current_display_save_effort))
        self.miss_sighting_choose.SetValue(self.deal_config_value(self.current_display_miss))
        #todo Excel模板配置
        self.excel_template_text.SetValue(self.current_template_file)
        #todo 其他配置
        self.mode_setting_choose.SetValue(self.mode_deal_config_value(self.current_on_off_line_save_flag))
        self.select_week_choose.SetValue(self.deal_config_value(self.current_keep_continuous))

        #todo 根据是否发送邮件标记 来控制邮件相关组件的初始状态
        if self.deal_config_value(self.current_send_email_flag) == 'NO':
            self.mail_server_text.Disable()
            self.sender_email_text.Disable()
            self.receive_email_text.Disable()

    #todo 空值设置 对'YES'和'NO'的两值变量处理
    def deal_config_value(self, value):
        return 'YES' if value.strip() == 'YES' else 'NO'

    #todo 对时间变量处理
    def time_deal_config_value(self, value):
        return value.strip() if len(value.strip()) else '60'

    #todo 对离线在线模式变量处理
    def mode_deal_config_value(self, value):
        return 'online' if value.strip() == 'online' else 'offline'

    #todo 对邮件服务器变量处理
    def server_deal_config_value(self, value):
        return 'smtp.intel.com'
        # return (value.strip() if len(value.strip()) else 'smtp.intel.com')

    #todo 将当前的配置保存为默认配置
    def current_config_as_default_config(self):
        conf = MachineConfig(CONFIG_FILE_PATH)
        project_name_sep = obtain_prefix_project_name(self.name)

        #todo 邮件部分
        conf.modify_node_value(project_name_sep + '_server', 'server_address', self.mail_server_text.GetValue())
        conf.modify_node_value(project_name_sep + '_from_address', 'from_address', self.sender_email_text.GetValue())
        conf.modify_node_value(project_name_sep + '_receive_address', 'receive_address', self.receive_email_text.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'send_email_flag', self.send_email_flag_text.GetValue())
        #todo 文件部分
        conf.modify_node_value(project_name_sep + '_other_config', 'reacquire_data_flag', self.reacquire_data_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'verify_file_flag', self.review_file_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'max_waiting_time', self.max_time_text.GetValue())
        #todo 图表部分
        conf.modify_node_value(project_name_sep + '_other_config', 'display_software', self.software_change_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_new', self.new_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_existing', self.exist_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_closed', self.closed_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_total', self.total_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_save_test', self.save_test_case_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_save_effort', self.save_efforts_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_miss', self.miss_sighting_choose.GetValue())
        #todo 模板文件部分
        conf.modify_node_value(project_name_sep + '_other_config', 'template_file', self.excel_template_text.GetValue())
        #todo 其他部分
        conf.modify_node_value(project_name_sep + '_other_config', 'on_off_line_save_flag', self.mode_setting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'keep_continuous', self.select_week_choose.GetValue())
        #todo 默认配置周数为１００
        conf.modify_node_value(project_name_sep + '_other_config', 'week_num', '100')

    #todo 窗口关闭自动将当前窗口配置保存为配置文件当前配置
    def current_gui_config_as_current_file_config(self):
        conf = MachineConfig(CONFIG_FILE_PATH)
        project_name_sep = obtain_prefix_project_name(self.name)

        #todo 邮件部分
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_server_address', self.mail_server_text.GetValue())
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_send_address', self.sender_email_text.GetValue())
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_receive_address', self.receive_email_text.GetValue())
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_send_email_flag', self.send_email_flag_text.GetValue())
        #todo 文件部分
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_reacquire_data_flag', self.reacquire_data_choose.GetValue())
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_verify_file_flag', self.review_file_choose.GetValue())
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_max_waiting_time', self.max_time_text.GetValue())
        #todo 图表部分
        conf.modify_node_value(project_name_sep + '_other_config', 'display_software', self.software_change_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_new', self.new_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_existing', self.exist_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_closed', self.closed_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_total', self.total_sighting_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_save_test', self.save_test_case_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_save_effort', self.save_efforts_choose.GetValue())
        conf.modify_node_value(project_name_sep + '_other_config', 'display_miss', self.miss_sighting_choose.GetValue())
        #todo 模板文件部分
        conf.modify_node_value(project_name_sep + '_other_config', 'template_file', self.excel_template_text.GetValue())
        #todo 其他部分
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_on_off_line_save_flag', self.mode_setting_choose.GetValue())
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_keep_continuous', self.select_week_choose.GetValue())
        #todo 默认配置周数为１００
        conf.modify_node_value(self.name + '_real-time_control_parameter_value', 'default_choose_week_num', '100')

    #todo 加载默认配置为当前配置
    def load_default_config_as_current_config(self):
        self.get_init_config_info('default')
        self.load_init_config_info()


class ProjectSelectGui(wx.Frame):
    def __init__(self, logger):
        self.purl_bak_string = None
        self.logger = logger

        wx.Frame.__init__(self, None, wx.ID_ANY, "Configuration GUI", size=(540, 370), style=wx.DEFAULT_FRAME_STYLE)
        self.button = wx.Button(self, wx.ID_ANY, 'NFVi', pos=(50, 50), size=(170, 80))
        self.button1 = wx.Button(self, wx.ID_ANY, 'Bakerville', pos=(50, 200), size=(170, 80))
        self.button2 = wx.Button(self, wx.ID_ANY, 'Purley-FPGA', pos=(300, 50), size=(170, 80))
        self.button3 = wx.Button(self, wx.ID_ANY, 'Crystal-Ridge', pos=(300, 200), size=(170, 80))

        #todo 设置鼠标指针样式
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        #todo 设置字体大小格式
        wx_font = wx.Font(14, wx.MODERN, wx.ITALIC, wx.BOLD)
        self.button1.SetFont(wx_font)
        self.button2.SetFont(wx_font)
        self.button3.SetFont(wx_font)
        self.button.SetFont(wx_font)

        #todo 设置字体颜色
        self.button.SetForegroundColour('red')
        self.button1.SetForegroundColour('blue')
        self.button2.SetForegroundColour('orange')
        self.button3.SetForegroundColour('khaki')

        #todo 绑定回调函数
        self.button.Bind(wx.EVT_BUTTON, self.project_choose_event)
        self.button1.Bind(wx.EVT_BUTTON, self.project_choose_event)
        self.button2.Bind(wx.EVT_BUTTON, self.project_choose_event)
        self.button3.Bind(wx.EVT_BUTTON, self.project_choose_event)

        #todo 显示界面
        self.Center()
        self.Layout()
        self.Show()

    def project_choose_event(self, event):
        if event.Id == self.button.GetId():
            self.purl_bak_string = 'NFVi'
        elif event.Id == self.button1.GetId():
            self.purl_bak_string = 'Bakerville'
        elif event.Id == self.button2.GetId():
            self.purl_bak_string = 'Purley-FPGA'
        else:
            self.purl_bak_string = 'Purley-Crystal-Ridge'

        self.logger.print_message('The program you selected is: [ %s ], please close the window to continue the main program!!!'
                                    'If you want to change the choice of project name, please continue to select!!!' % self.purl_bak_string, _file_name, 20)
        # todo 修改配置文件项目名称信息
        conf = MachineConfig(CONFIG_FILE_PATH)
        conf.modify_node_value('real-time_control_parameter_value', 'default_purl_bak_string', self.purl_bak_string)
        self.Destroy()


#todo 检测用户是否自定义周并做出相应动作
def check_user_redefinition_week(purl_bak_string, logger):
    conf = MachineConfig(CONFIG_FILE_PATH)
    keep_continuous = conf.get_node_info(purl_bak_string + '_real-time_control_parameter_value', 'default_keep_continuous')
    if keep_continuous == 'YES':
        #todo 自定义选择周主界面
        week_gui_config('', purl_bak_string, logger)


#TODO 主程序
def main(logger):
    #todo 项目选择主界面
    app = wx.App()
    ProjectSelectGui(logger)
    app.MainLoop()

    #todo 加载最新的项目名称信息
    conf = MachineConfig(CONFIG_FILE_PATH)
    purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')

    #todo 项目配置参数主界面
    app1 = wx.App()
    ProjectConfigParameterGui(purl_bak_string, logger)
    app1.MainLoop()

    #todo 当关闭窗口时会检测是否用户自定义选择周
    check_user_redefinition_week(purl_bak_string, logger)

    return purl_bak_string


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

    #TODO 检测是否有空值，有则添加默认值 2017-06-02
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
            conf.modify_node_value(project_name_sep + '_other_config', 'max_waiting_time', '30')
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
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_max_waiting_time', '30')
    if len(on_off_line_save_flag.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_on_off_line_save_flag', 'online')
    if len(send_email_flag.strip()) == 0:
        conf.modify_node_value(purl_bak_string + '_real-time_control_parameter_value', 'default_send_email_flag', 'YES')

    #TODO 以下参数必须非空
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





if __name__ == "__main__":
    import time
    start = time.time()
    app = wx.App(False)
    frame = ProjectConfigParameterGui('NFVi', '')
    app.MainLoop()
    print time.time() - start