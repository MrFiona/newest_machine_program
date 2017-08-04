#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-08-02 15:00
# Author  : MrFiona
# File    : predict_extract_data.py
# Software: PyCharm Community Edition


import os
import re
import urllib2
from bs4 import BeautifulSoup
from machine_scripts.public_use_function import remove_line_break
from machine_scripts.common_interface_func import remove_non_alphanumeric_characters


class PredictGetData(object):

    def __init__(self, logger, predict_url):
        self.logger = logger
        self.predict_url = predict_url
        self.html = urllib2.urlopen(self.predict_url).read()
        self.date_string = 'default_date_string_value'
        self._file_name = os.path.split(__file__)[1]
        soup_html = BeautifulSoup(self.html, 'html.parser')
        object_string = soup_html.find_all('table')[0]
        soup_string = BeautifulSoup(str(object_string), 'html.parser')
        candidate_string = soup_string.find_all('p')[1]
        result_dict = re.search('<p\s+.*\s+--\s+(?P<name>(.*))</p>', str(candidate_string))
        if result_dict:
            self.logger.print_message('result_dict:\t%s' % result_dict.group('name'), self._file_name)
            self.date_string = result_dict.group('name')

    def return_save_miss_bkc_string(self):
        save_miss_insert_bkc_string = self.date_string
        re_bkc_obj_list = re.findall('\d{4}\s+WW\d{2}', save_miss_insert_bkc_string)
        effect_bkc_string = ''.join(re_bkc_obj_list[0].split())
        return effect_bkc_string

    def predict_get_sw_data(self):
        regex = re.compile(r'<span class="sh2">&nbsp; SW Configuration: </span>(.*?)<span class="sh2">&nbsp; IFWI Configuration: </span>', re.S|re.M)
        header = re.findall(regex, self.html)
        string_data = ''.join(header)
        # 提取所有的tr部分
        soup_tr = BeautifulSoup(string_data, 'html.parser')
        tr_list = soup_tr.find_all(re.compile('tr'))
        url_list, header_list, cell_data_list = [], [], []
        try:
            if not tr_list:
                return 'null', 0, [], [], []
            soup_header = BeautifulSoup(str(tr_list[0]), 'html.parser')
            header_list = list(soup_header.strings)
            header_list = remove_line_break(header_list, line_break=True)
            for i in range(len(header_list)):
                header_list[i] = header_list[i].replace('\n', '')
            # 排除部分周会有更多的列
            # print 'header:list:\t', header_list
            header_length = len(header_list)
            header_list = header_list[:4]
            url_list = []

            for t in tr_list[1:]:
                temp_url_list = []
                temp_string_list = []
                soup_tr = BeautifulSoup(str(t), 'html.parser')
                td_list = soup_tr.find_all('td')
                # 默认情况是正常列数
                actual_td_list = td_list

                num = len(td_list)
                if num == header_length + 1:
                    soup_5 = BeautifulSoup(str(t), 'html.parser')
                    string_5_list = list(soup_5.strings)
                    string_5_list = remove_line_break(string_5_list, line_break=True)
                    temp_string_list = string_5_list[1:]
                    actual_td_list = td_list[1:]

                elif num == header_length + 2:
                    actual_td_list = td_list[2:]
                    soup_6 = BeautifulSoup(str(t), 'html.parser')
                    string_6_list = list(soup_6.strings)
                    string_6_list = remove_line_break(string_6_list, line_break=True)
                    temp_string_list = string_6_list[2:]

                elif num <= header_length:
                    soup_4 = BeautifulSoup(str(t), 'html.parser')
                    string_4_list = list(soup_4.strings)
                    string_4_list = remove_line_break(string_4_list, line_break=True)
                    temp_string_list = string_4_list
                    if header_length > 4 and len(temp_string_list) > 4:
                        temp_string_list = temp_string_list[header_length - 4:]

                # 获取cell_data_list数据
                temp_string_list = remove_non_alphanumeric_characters(temp_string_list)

                if (len(temp_string_list) >= header_length + 1):
                    temp_string_list = [ele for ele in temp_string_list if len(ele) != 0]

                elif (len(temp_string_list) >= header_length + 2) and len(temp_string_list[-1]) == 0:
                    temp_string_list = temp_string_list[:-1]

                if temp_string_list:
                    if len(temp_string_list) < 4:
                        for nu in range(4 - len(temp_string_list)):
                            temp_string_list.append('')
                    cell_data_list.append(temp_string_list)
                # print 'temp_string_list:\t', temp_string_list, len(temp_string_list)
                for td in actual_td_list:
                    # 正则取匹配url链接
                    obj_list = re.findall('<a href="(.*?)">', str(td), re.M | re.S)
                    if obj_list:
                        # 逐个添加
                        for url in obj_list:
                            url = url.split()[0].replace("\"", "")
                            temp_url_list.append(url)

                if temp_url_list:
                    url_list.append(temp_url_list)

            for k in range(len(cell_data_list)):
                if header_length > 4 and len(cell_data_list[k]) > 4:
                    cell_data_list[k] = cell_data_list[k][:4 - header_length]

            header_length = len(header_list)

            if header_length < 4:
                header_length = 4

            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            # print '\033[31murl_list:\t\033[0m', url_list, len(url_list)
            return 'Candidate', header_length, url_list, header_list, cell_data_list
        except:
            return 'Error', 0, [], [], []

    def predict_get_ifwi_data(self):
        regex = re.compile(r'<span class="sh2">&nbsp; IFWI Configuration: </span>(.*?)<span class="sh2">&nbsp; BKC Useful Info: </span>', re.S|re.M)
        header = re.findall(regex, self.html)
        string_data = ''.join(header)
        # 提取所有的tr部分
        soup_tr = BeautifulSoup(string_data, 'html.parser')
        tr_list = soup_tr.find_all(re.compile('tr'))
        url_list, header_list, cell_data_list = [], [], []
        try:
            if not tr_list:
                return '', [], []
            for tr in tr_list:
                soup = BeautifulSoup(str(tr), 'html.parser')
                th_list = soup.find_all('th')
                if tr == tr_list[0]:
                    for th in th_list:
                        th_string = re.findall('>(.*?)<', str(th))
                        if th_string:
                            header_list.append(th_string[0])
                if not th_list:
                    td_string_list = list(soup.strings)
                    td_string_list = remove_line_break(td_string_list, line_break=True)
                    for ele in range(len(td_string_list)):
                        for regex in ['\xe2', u'\u20ac', u'\u201c', u'\s+']:
                            td_string_list[ele] = re.sub(regex, ' ', td_string_list[ele])
                    #去掉首位字符串开头的空格,排除空格的影响 后续会排序
                    if td_string_list:
                        td_string_list[0] = td_string_list[0].lstrip(' ')
                    cell_data_list.append(td_string_list)
            # print '\033[31mself.date_string:\t\033[0m', self.date_string, len(self.date_string)
            # print '\033[36mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            return 'Candidate', header_list, cell_data_list
        except:
            return 'Error', [], []

if __name__ == '__main__':
    # https://dcg-oss.intel.com/test_report/test_report/6446/0/
    # https://oss-sh.ccr.corp.intel.com/test_report/test_report/6421/0/
    obj = PredictGetData('https://dcg-oss.intel.com/test_report/test_report/6446/0/')
    # obj.predict_get_sw_data()
    obj.predict_get_ifwi_data()