#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-06 10:43
# Author  : MrFiona
# File    : send_email.py
# Software: PyCharm Community Edition


import glob
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from machine_config import MachineConfig
from machine_scripts.public_use_function import deal_html_data, get_url_list_by_keyword, judge_get_config
from setting_global_variable import DEBUG_FLAG, MANUAL_CONFIG_FILE_PATH


class SendEmail:
    def __init__(self, purl_bak_string, logger, type_string=''):
        self.logger = logger
        self.file_logger_name = os.path.split(__file__)[1]
        self.purl_bak_string = purl_bak_string
        self.type_string = type_string
        deal_html_data()
        self.send()

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((
            Header(name, 'utf-8').encode(),
            addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    def send(self):
        # TODO 正常流程
        if self.type_string == '':
            from_addr = judge_get_config('from_address', self.purl_bak_string)
            to_addr = judge_get_config('receive_address', self.purl_bak_string)
            smtp_server = judge_get_config('server_address', self.purl_bak_string)

            Silver_url_list = get_url_list_by_keyword(self.purl_bak_string, 'Silver')
            lastest_week_string = Silver_url_list[0]
            lastest_week_string = 'WW' + lastest_week_string.split('/')[-2].split('%')[-1].split('WW')[-1]
        # TODO 自动发邮件
        else:
            conf = MachineConfig(MANUAL_CONFIG_FILE_PATH)
            from_addr = conf.get_node_info('from_address', 'from_address')
            to_addr = conf.get_node_info('receive_address', 'receive_address')
            smtp_server = conf.get_node_info('server_address', 'server_address')
            lastest_week_string = conf.get_node_info('manual_machine_info', 'week_info')

        SUBJECT = 'BKC ITF Test Plan of %s %s' % (self.purl_bak_string, lastest_week_string)

        if DEBUG_FLAG:
            self.logger.print_message('from address: %s' % from_addr, self.file_logger_name)
            self.logger.print_message('to address: %s' % to_addr, self.file_logger_name)
            self.logger.print_message('server address:  %s' % smtp_server, self.file_logger_name)
            self.logger.print_message("***************************** Message body *****************************", self.file_logger_name)
            self.logger.print_message("         subject: %s" % SUBJECT, self.file_logger_name)
            self.logger.print_message("************************************************************************", self.file_logger_name)

        html_string = ''
        print os.getcwd() + os.sep + self.type_string + 'html_result'
        if os.path.exists(os.getcwd() + os.sep + self.type_string + 'html_result'):
            print glob.glob(os.getcwd() + os.sep + self.type_string + 'html_result' + os.sep + '*.html')
            for file_name in glob.glob(os.getcwd() + os.sep + self.type_string + 'html_result' + os.sep + '*.html'):
                if self.purl_bak_string in file_name:
                    with open(file_name, 'r') as f:
                        html_data = f.readlines()
                    for i in range(len(html_data)):
                        html_data[i] = html_data[i].strip()
                        html_string += html_data[i]

        msg = MIMEText(html_string, 'html', 'utf-8')
        msg['From'] = self._format_addr(from_addr)

        address_list = []
        for address in to_addr.split(','):
            if len(address.strip()) == 0:
                continue
            address_list.append(address.strip())

        msg['To'] = ','.join(address_list)
        msg['Subject'] = Header(u'BKC ITF Test Plan of %s %s' % (self.purl_bak_string, lastest_week_string), 'utf-8').encode()
        server = smtplib.SMTP(smtp_server, 25)
        # server.set_debuglevel(1)
        server.sendmail(from_addr, address_list, msg.as_string())
        server.quit()



if __name__ == '__main__':
    file_path = r'C:\Users\pengzh5x\Desktop\2017-07-14_1\excel_dir\Bakerville_100_2017WW11_15_BKC_2017_07_20_15_11_20.xlsx'
    from machine_scripts.public_use_function import get_win_proc_ids
    os.system('start excel.exe %s' % file_path)
    get_win_proc_ids()
    # time.sleep(10)
    os.system('ntsd -c q -pn excel.exe')
    # from custom_log import WorkLogger
    # from setting_global_variable import CONFIG_FILE_PATH
    # log_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
    # _logger = WorkLogger(log_filename='machine_log', log_time=log_time)
    # conf = MachineConfig(CONFIG_FILE_PATH)
    # purl_bak_string = conf.get_node_info('real-time_control_parameter_value', 'default_purl_bak_string')
    # keep_continuous = judge_get_config('keep_continuous', purl_bak_string)
    # SendEmail(purl_bak_string, _logger, keep_continuous)