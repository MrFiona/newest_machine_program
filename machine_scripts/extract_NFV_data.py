#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-06-09 09:10
# Author  : MrFiona
# File    : extract_NFV_data.py
# Software: PyCharm Community Edition

import HTMLParser
import codecs
import os
import re
import sys
import urllib2
from logging import ERROR

from bs4 import BeautifulSoup

from cache_mechanism import DiskCache
from machine_scripts.public_use_function import remove_line_break
from machine_scripts.common_interface_func import (NFVi_remove_non_alphanumeric_characters, FilterTag)
from setting_global_variable import REPORT_HTML_DIR

reload(sys)
sys.setdefaultencoding('utf-8')

import ssl
from functools import wraps

# 强制ssl使用TLSv2
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv2
        return func(*args, **kw)

    return bar

context = ssl._create_unverified_context()
ssl.wrap_socket = sslwrap(ssl.wrap_socket)


class GetAnalysisData(object):
    def __init__(self, data_url, purl_bak_string, get_info_not_save_flag=False, cache=None, insert_flag=False, logger=None):
        self.data_url = data_url
        self.cache = cache
        self.logger = logger
        self.purl_bak_string = purl_bak_string
        self.__file_name = os.path.split(__file__)[1]

        if not insert_flag:
            try:
                result = None
                if self.cache:
                    try:
                        result = self.cache[self.data_url]
                    except KeyError:
                        pass

                if result is None:
                    result = urllib2.urlopen(self.data_url, context=context).read()
                    if self.cache:
                        self.cache[self.data_url] = result
            except IndexError:
                raise UserWarning('Please check whether the input [ %s ] url is correct!!!' %self.data_url)
        self.save_file_name = os.path.split(self.data_url)[-1].split('.')[0] + '_html'
        temp_path = self.data_url.split('auto')[1].strip('/').split('/')[:-1]  # 去掉最后一个html文件名
        self.grandfather_path = temp_path[0]  # 部门类型级别
        self.father_path = temp_path[1]  # 测试类型级别
        self.son_path = re.sub('[%]', '_', temp_path[-1])  # 日期级别
        self.save_file_path = REPORT_HTML_DIR + os.sep + '%s' % os.sep.join([self.grandfather_path, self.father_path, self.son_path])
        url_split_string = self.data_url.split('/')[-2]
        week_string = url_split_string[-4:]
        year_string = url_split_string.split('%')[0]
        self.date_string = ''.join([year_string, week_string])

        #保存文件标记开启，将html代码保存为文件
        if get_info_not_save_flag:
            self.save_html()

    def save_html(self):
        try:
            filters = FilterTag()
            html = urllib2.urlopen(self.data_url, context=context).read().decode('utf-8')
            response_parser = HTMLParser.HTMLParser()
            html = response_parser.unescape(html)
            html = filters.filterHtmlTag(html)
            html = filters.replaceCharEntity(html)
            # 将源代码写入文件
            with codecs.open(self.save_file_path + os.sep + self.save_file_name, 'w', encoding='utf-8') as file:
                file.write(html)
        except urllib2.HTTPError as e:
            print e
            print 'Access error, please check whether address [ %s ] is valid!!!' % self.data_url
            return
        except urllib2.URLError as e:
            print e
            return

    # 提取通用的部分,如果bkc_flag=True并且BKC和Gold都没有数据则取Silver数据 优先级：BKC > Gold > Silver
    def _common_regex(self, data_type, bkc_flag=False, replace_flag=False):
        Silver_Gold_BKC_string = 'Silver'
        # # 如果bkc_flag = True并且BKC没有数据则取Silver数据,需将变量恢复原值
        # if replace_flag and not bkc_flag:
        #     self.save_file_path = self.save_file_path.replace('BKC', 'Silver')
        #     self.save_file_path = self.save_file_path.replace('Gold', 'Silver')
        #     self.data_url = self.data_url.replace('BKC', 'Silver')
        #     self.data_url = self.data_url.replace('Gold', 'Silver')
        #     self.save_file_name = self.save_file_name.replace('BKC', 'Silver')
        #     self.save_file_name = self.save_file_name.replace('Gold', 'Silver')
        #     Silver_Gold_BKC_string = 'Silver'

        # BKC标记开启，自动更换为文件BKC地址
        if bkc_flag:
            self.save_file_path = self.save_file_path.replace('Silver', 'BKC')
            self.data_url = self.data_url.replace('Silver', 'BKC')
            Silver_Gold_BKC_string = 'BKC'
            # 如果BKC无数据则取Gold数据
            if not os.path.exists(self.save_file_path):
                self.save_file_path = self.save_file_path.replace('BKC', 'Gold')
                self.data_url = self.data_url.replace('BKC', 'Gold')
                Silver_Gold_BKC_string = 'Gold'
                # 如果Gold无数据则取Silver数据
                if not os.path.exists(self.save_file_path):
                    self.save_file_path = self.save_file_path.replace('Gold', 'Silver')
                    self.data_url = self.data_url.replace('Gold', 'Silver')
                    Silver_Gold_BKC_string = 'Silver'
                    if not os.path.exists(self.save_file_path):
                        return '', [], [], []

            search_file_list = os.listdir(self.save_file_path)
            bkc_file_name = ''
            for file in search_file_list:
                match = re.match(r'\d+', file)
                if match:
                    bkc_file_name = file
            if len(bkc_file_name) == 0:
                print 'BKC and Gold file is not exist!!!'
                return '', []
            self.save_file_name = os.path.split(self.data_url)[-1].split('.')[0] + '_html'
            self.save_file_name = bkc_file_name

        # 读取文本中的html代码
        # with codecs.open(self.save_file_path + os.sep + self.save_file_name, 'r', encoding='utf-8') as f:
        #     data = f.readlines()
        # data = ''.join(data)
        data = self.cache[self.data_url]
        # 提取HW Configuration部分的代码
        regex = re.compile(r'<span class="sh2">&nbsp; %s </span>(.*?)<div class="panel-heading">' % data_type,
                           re.S | re.M)
        header = re.findall(regex, data)
        string_data = ''.join(header)
        # 提取所有的tr部分
        soup_tr = BeautifulSoup(string_data, 'html.parser')
        tr_list = soup_tr.find_all(re.compile('tr'))

        # 增加保险措施，通过关键字提取文本html实现
        if not tr_list:
            fread = codecs.open(self.save_file_path + os.sep + self.save_file_name, 'r', 'utf-8')
            fwrite = codecs.open(self.save_file_path + os.sep + 'temp.txt', 'wb', 'utf-8')
            pre_keyword = data_type
            next_keyword = 'panel collapse-report-panel'
            flag = False
            for line in fread:
                if flag:
                    fwrite.write(line)
                if pre_keyword in line:
                    fwrite.write(line)
                    flag = True
                if next_keyword in line:
                    flag = False
            fread.close()
            fwrite.close()

            with codecs.open(self.save_file_path + os.sep + 'temp.txt', 'r', 'utf-8') as f:
                lines = f.readlines()

            lines = ''.join(lines)
            soup = BeautifulSoup(lines, 'html.parser')
            tr_list = soup.find_all('tr')
        return Silver_Gold_BKC_string, tr_list

    def judge_silver_bkc_func(self, data_type, bkc_flag):
        Silver_Gold_BKC_string, tr_list = self._common_regex(data_type, bkc_flag)
        # 如果bkc_flag = True并且BKC没有数据则取Silver数据
        # if not tr_list and bkc_flag:
        #     Silver_Gold_BKC_string, tr_list= self._common_regex(data_type, bkc_flag=False, replace_flag=True)
        return Silver_Gold_BKC_string, tr_list

    def get_hw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list = self.judge_silver_bkc_func(data_type, bkc_flag)
            effective_header_list, header_list, cell_data_list = [], [], []

            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], []

            th_soup = BeautifulSoup(str(tr_list[0]), 'html.parser')
            th_list = th_soup.find_all('th')
            for th in th_list:
                string_soup = BeautifulSoup(str(th), 'html.parser')
                th_strings_list = list(string_soup.strings)
                effective_header_list.extend([effective_string for effective_string in th_strings_list if len(effective_string) > 1])

            for tr in tr_list[1:]:
                temp_td_string_list = []
                soup_tr = BeautifulSoup(str(tr), 'html.parser')
                td_list = soup_tr.find_all('td')
                for td in td_list:
                    soup_td = BeautifulSoup(str(td), 'html.parser')
                    if soup_td:
                        td_string_list = list(soup_td.strings)
                        if td_string_list:
                            td_string_list = remove_line_break(td_string_list, line_break=True, empty_string=True, blank_string=True)
                            td_string_list = NFVi_remove_non_alphanumeric_characters(td_string_list)
                            temp_td_string_list.append('\n'.join(td_string_list))
                header_list.append(temp_td_string_list[0])
                cell_data_list.append(temp_td_string_list)

            for cell in range(len(cell_data_list)):
                cell_data_list[cell] = cell_data_list[cell][1:]

            # print '\033[31mSilver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            # print '\033[32mself.date_string:\t\033[0m', self.date_string
            # print '\033[34mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[31meffective_header_list:\t\033[0m', effective_header_list, len(effective_header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            return Silver_Gold_BKC_string, self.date_string, effective_header_list, header_list, cell_data_list

        except ImportError:
            self.logger.print_message(msg='Get [ %s ] Orignal Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', 'Error', [], [], []


if __name__ == '__main__':
    #Purley-FPGA Bakerville
    import time
    start = time.time()
    from machine_scripts.public_use_function import get_url_list_by_keyword
    cache = DiskCache('NFVi')
    key_url_list = get_url_list_by_keyword('NFVi', 'Silver')
    key_url_list = ['https://dcg-oss.intel.com/ossreport/auto/NFVi/Silver/2017%20WW02/5245_Silver.html']
    for url in key_url_list:
        obj = GetAnalysisData(url, 'NFVi', get_info_not_save_flag=True, cache=cache)
        # obj.get_platform_data('Platform Integration Validation Result', True)
        # obj.get_caseresult_data('Platform Integration Validation Result', True)
        # obj.get_bak_rework_data('HW Rework', True)
        # obj.get_rework_data('HW Rework', True)
        # obj.get_sw_data('SW Configuration', True)
        # obj.get_bak_hw_data('HW Configuration', True)
        obj.get_hw_data('HW Configuration', True)
        # obj.get_ifwi_data('IFWI Configuration')
    #     obj.get_existing_sighting_data('Existing Sightings', True)
    #     obj.get_new_sightings_data('New Sightings')
    #     obj.get_closed_sightings_data('Closed Sightings')
    print time.time() - start