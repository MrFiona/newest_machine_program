#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-03-21 09:40
# Author  : MrFiona
# File    : extract_data.py
# Software: PyCharm Community Edition


import os
import re
import ssl
import sys
import codecs
import urllib2
import collections
from lxml import etree
from functools import wraps
from logging import ERROR, CRITICAL

from bs4 import BeautifulSoup

from machine_scripts.cache_mechanism import DiskCache
from machine_scripts.public_use_function import remove_line_break, judge_get_config
from setting_global_variable import REPORT_HTML_DIR, SRC_CACHE_DIR
from machine_scripts.common_interface_func import remove_non_alphanumeric_characters
from machine_scripts.common_interface_branch_func import extract_sw_data_deal_bracket


#todo 强制ssl使用TLSv2
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv2
        return func(*args, **kw)

    return bar

context = ssl._create_unverified_context()
ssl.wrap_socket = sslwrap(ssl.wrap_socket)


reload(sys)
sys.setdefaultencoding('utf-8')

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
                self.logger.print_message('Please check whether the input [ %s ] url is correct!!!' % self.data_url, self.__file_name, definition_log_level=40)
                raise UserWarning('Please check whether the input [ %s ] url is correct!!!' %self.data_url)

        self.save_file_name = os.path.split(self.data_url)[-1].split('.')[0] + '_html'
        temp_path = self.data_url.split('auto')[1].strip('/').split('/')[:-1]  #todo 去掉最后一个html文件名
        self.grandfather_path = temp_path[0]  #todo 部门类型级别
        self.father_path = temp_path[1]  #todo 测试类型级别
        self.son_path = re.sub('[%]', '_', temp_path[-1])  #todo 日期级别
        self.save_file_path = REPORT_HTML_DIR + os.sep + '%s' % os.sep.join([self.grandfather_path, self.father_path, self.son_path])
        url_split_string = self.data_url.split('/')[-2]
        week_string = url_split_string[-4:]
        year_string = url_split_string.split('%')[0]
        self.date_string = ''.join([year_string, week_string])

        #todo 保存文件标记开启，将html代码保存为文件
        if get_info_not_save_flag:
            self.save_html()

    #todo 将html保存到report_html目录
    def save_html(self):
        try:
            html = urllib2.urlopen(self.data_url, context=context).read().decode('utf-8')
            with codecs.open(self.save_file_path + os.sep + self.save_file_name, 'w', encoding='utf-8') as file:
                file.write(html)
        except urllib2.HTTPError as e:
            self.logger.print_message(e, self.__file_name, CRITICAL)
            self.logger.print_message('Access error, please check whether address [ %s ] is valid!!!' % self.data_url, self.__file_name, CRITICAL)
            return
        except urllib2.URLError as e:
            self.logger.print_message(e, self.__file_name, CRITICAL)
            return

    #todo 提取通用的部分,如果bkc_flag=True并且BKC和Gold都没有数据则取Silver数据 优先级：BKC > Gold > Silver
    def _common_regex(self, data_type, bkc_flag=False, replace_flag=False, header_list=None, cell_data_list=None):
        Silver_Gold_BKC_string = 'Silver'
        if not header_list:
            header_list = []
        if not cell_data_list:
            cell_data_list = []

        #todo BKC标记开启，自动更换为文件BKC地址
        if bkc_flag:
            self.save_file_path = self.save_file_path.replace('Silver', 'BKC')
            self.data_url = self.data_url.replace('Silver', 'BKC')
            Silver_Gold_BKC_string = 'BKC'
            #todo 如果BKC无数据则取Gold数据
            if not os.path.exists(self.save_file_path):
                self.save_file_path = self.save_file_path.replace('BKC', 'Gold')
                self.data_url = self.data_url.replace('BKC', 'Gold')
                Silver_Gold_BKC_string = 'Gold'
                #todo 如果Gold无数据则取Silver数据
                if not os.path.exists(self.save_file_path):
                    self.save_file_path = self.save_file_path.replace('Gold', 'Silver')
                    self.data_url = self.data_url.replace('Gold', 'Silver')
                    Silver_Gold_BKC_string = 'Silver'
                    if not os.path.exists(self.save_file_path):
                        return '', None, [], []

            search_file_list = os.listdir(self.save_file_path)
            bkc_file_name = ''
            for file in search_file_list:
                match = re.match(r'\d+', file)
                if match:
                    bkc_file_name = file
            if len(bkc_file_name) == 0:
                print 'BKC or Gold or Silver file is not exists!!!'
                return '', None, [], []
            self.save_file_name = os.path.split(self.data_url)[-1].split('.')[0] + '_html'
            self.save_file_name = bkc_file_name

        data = self.cache[self.data_url]
        #todo 提取HW Configuration部分的代码
        regex = re.compile(r'<div id="collapse%s"\s+class="panel-collapse collapse\s+[i]{0,1}[n]{0,1}">(.*?)'
                           r'<div class="marginBoxPreview">' % data_type, re.S | re.M)
        header = re.findall(regex, data)
        string_data = ''.join(header)
        xml_soup = etree.HTML(string_data)
        return Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list

    #todo 获取hw有效的列名列表
    def _get_hw_effective_header_list(self, effective_header_list):
        #todo 提取有效的行数
        effective_num_list = []
        prefix_suffix_list = []
        for label in range(len(effective_header_list)):
            temp_string_list = re.split('[\D+]', effective_header_list[label])
            temp = re.split('[\d+~]', effective_header_list[label])
            temp = remove_line_break(temp, empty_string=True)
            prefix_suffix_list.append(temp)
            temp_list = list(set(temp_string_list))[1:]
            for i in range(len(temp_list)):
                temp_list[i] = int(temp_list[i])
                temp_list.sort()
            effective_num_list.append(temp_list)

        effective_temp_list = []
        for pre, head in zip(prefix_suffix_list, effective_num_list):
            effective_temp_list.append([pre, head])

        effective_header_list = []
        for node_list in effective_temp_list:
            try:
                range_col = node_list[1]
                left_half_section = range_col[0]
                try:
                    right_half_section = range_col[1] + 1
                except IndexError:
                    right_half_section = left_half_section + 1

                for col in range(left_half_section, right_half_section):
                    if len(node_list[0]) == 1:
                        effective_header_list.append(node_list[0][0] + str(col))
                    if len(node_list[0]) > 1:
                        effective_header_list.append(node_list[0][0] + str(col) + node_list[0][-1])
            except (ValueError, IndexError) as e:
                print e
        return effective_header_list, effective_num_list

    #todo 适配Bakerville  获取hw有效的列名列表
    def _get_hw_bak_effective_header_list(self, effective_header_list):
        header_list = []
        #todo 提取有效的行数
        effective_num_list = []
        header_regex = re.compile('[Ss]ystem(?P<name>\(?.*\)?)', re.M | re.S)
        element_regex = re.compile('\d+')

        #todo 判断周表头列是否含有SKX-DE
        SKX_DE_FLAG = False
        for label in range(len(effective_header_list)):
            temp_num_list = []
            temp_string_list = re.split(header_regex, effective_header_list[label])
            temp_string_list = remove_line_break(temp_string_list, empty_string=True)
            temp_string = re.sub('[()]', '', temp_string_list[0])
            header_list.append(temp_string)
            #todo 进一步提取表头列数
            #todo 排除类似这种情况 SKX-DE(001,~004)(Cycling Test)
            if temp_string_list[0].startswith('SKX-DE'):
                SKX_DE_FLAG = True
                continue
            #todo 1、数字之间逗号相隔且不含有连续数字符号~
            if '~' not in temp_string:
                signal_num_list = re.findall(element_regex, temp_string)
                if signal_num_list:
                    signal_num_list = [int(ele) for ele in signal_num_list]
                    temp_num_list.extend(signal_num_list)
                    # print 'temp_num_list:\t', temp_num_list
            #todo 含有连续数字符号~  (1,~5)  (1~5)  1~5
            else:
                if ',' not in temp_string:
                    #todo 不含有逗号只含有~
                    range_num_list = re.findall('\d+', temp_string)
                    if range_num_list:
                        #todo 转换为离散的数字列
                        temp_change_list = [nu for nu in range(int(range_num_list[0]), int(range_num_list[1]) + 1)]
                        temp_num_list.extend(temp_change_list)
                #todo 既含有逗号又含有~ (1,~5) 1,~5 (1,3~6) 1,2~5
                else:
                    #todo 去括号
                    temp_string = re.sub('[()]', '', temp_string)
                    judge_string_list = re.findall('\d+~\d+', temp_string)
                    #todo 说明是 (1,2~7)这样的情况 ~左右数字齐全
                    # print 'judge_string_list:\t',judge_string_list
                    if judge_string_list:
                        temp_list = []
                        split_string_list = [ele for ele in re.split(',', temp_string) if len(ele) != 0]
                        print 'split_string_list:\t', split_string_list
                        for deal_num in split_string_list:
                            #todo 2~6
                            if '~' in deal_num:
                                range_num_list = re.findall('\d+', deal_num)
                                temp_list = [nu for nu in range(int(range_num_list[0]), int(range_num_list[1]) + 1)]
                            #todo 单个数字 2
                            else:
                                temp_list.append(int(deal_num))
                            temp_num_list.extend(temp_list)
                        print temp_num_list
                    #todo 说明是 (1,~5)这种情况
                    else:
                        range_num_list = re.findall('\d+', temp_string)
                        if range_num_list:
                            #todo 转换为离散的数字列
                            temp_change_list = [nu for nu in
                                                range(int(range_num_list[0]), int(range_num_list[1]) + 1)]
                            temp_num_list.extend(temp_change_list)
            if temp_num_list:
                effective_num_list.append(temp_num_list)

        effective_header_list = [int(ele) for child_element in effective_num_list for ele in child_element]
        effective_header_list = sorted(effective_header_list, key=lambda x: x)
        #todo SKX_DE标记开启,自动填充至12 表示12列数据
        if SKX_DE_FLAG:
            for i in range(len(effective_header_list) + 1, 12 + 1):
                effective_header_list.append(i)
        effective_header_list = ['System ' + str(ele) for ele in effective_header_list]
        # print 'effective_num_list:\t', effective_num_list
        # print 'effective_header_list:\t', effective_header_list

        return effective_header_list, effective_num_list

    #todo 判断插入到cell_data_list的次数并插入数据 todo 根据表头列数字和cell_data_list进一步处理,生成新的cell_data_list,effective_num_list
    def _insert_bak_numbers_to_cell_data_list(self, effective_num_list, cell_data_list):
        cell_data_direction_dict = collections.OrderedDict()
        for ele in range(len(effective_num_list)):
            for k in effective_num_list[ele]:
                temp_cell_data_list = []
                for j in range(len(cell_data_list)):
                    temp_cell_data_list.append(cell_data_list[j][ele])
                cell_data_direction_dict[k] = temp_cell_data_list
        cell_data_direction_dict = sorted(cell_data_direction_dict.iteritems())
        x, effective_cell_data_list = zip(*cell_data_direction_dict)
        effective_cell_data_list = [[ele[i] for ele in effective_cell_data_list] for i in range(len(cell_data_list))]
        # print 'effective_cell_data_list:\t', effective_cell_data_list
        #todo 重复拷贝信息的次数
        repeat_append_num = 12 - len(effective_cell_data_list[0])
        #todo 不管是否含有SKX_DE，只要小于12列后面的列就用最后一列信息补充
        if repeat_append_num > 0:
            for m in range(len(cell_data_list)):
                for nu in range(repeat_append_num):
                    effective_cell_data_list[m].append(cell_data_list[m][-1])

        return effective_cell_data_list

    def get_hw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, xml_soup, left_header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            table_list = xml_soup.xpath('//div[@class="panel-body"]//table[@class="sightingPreviewTable"]')
            effective_header_list = []
            #todo 存放单元数据的列表
            for table in table_list:
                #todo 提取数据部分
                tr_list = table.findall('tbody')[0].findall('tr')
                signal_table_data = [[td.text for td in tr[1:]] for tr in tr_list[1:]]
                cell_data_list.append(signal_table_data)
                if not left_header_list:
                    left_header_list = [td.text for tr in tr_list[1:] for td in tr[:1]]

                #todo 提取表头数据部分
                header = [th.text for th in tr_list[0].findall('th')[1:]]
                effective_header_list.extend(header)

            #todo 将多个表合并为一个表
            m = cell_data_list[0]
            for element in cell_data_list[1:]:
                for ele in xrange(len(m)):
                    m[ele].extend(element[ele])

            #todo 将多列合并数据按照顺序展开（根据数字标记）
            effective_header_list, effective_num_list = self._get_hw_bak_effective_header_list(effective_header_list)
            cell_data_list = self._insert_bak_numbers_to_cell_data_list(effective_num_list, m)
            print '\033[31mSilver_Gold_BKC_string111:\t\033[0m', Silver_Gold_BKC_string
            print '\033[32meffective_header_list:\t\033[0m', effective_header_list, len(effective_header_list)
            print '\033[31mleft_header_list:\t\033[0m', left_header_list, len(left_header_list)
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            return Silver_Gold_BKC_string, self.date_string, effective_header_list, left_header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', 'Error', [], [], []

    def get_sw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            table_list = xml_soup.xpath('//div[@class="panel-body"]//table[@class="MsoNormalTable"]')
            url_list = []
            table_string = etree.tostring(table_list[0].findall('tbody')[0])
            bs_soup = BeautifulSoup(table_string, 'html.parser')
            tr_list = bs_soup.find_all('tr')
            header_list = list(tr_list[0].stripped_strings)[:4]
            header_length = len(header_list)

            for tr_ele in tr_list[1:]:
                temp_url_list = []
                tr_string_list = list(tr_ele.stripped_strings)
                tr_string_list = tr_string_list[-6:-2]
                cell_data_list.append(tr_string_list)
                #todo 提取url链接
                td_list = tr_ele.find_all('td')
                for td in td_list:
                    try:
                        attribute_list = td.a.attrs
                        temp_url_list.append(attribute_list['href'])
                    except AttributeError:
                        pass
                if temp_url_list:
                    url_list.append(temp_url_list)
            print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            print '\033[31murl_list:\t\033[0m', url_list, len(url_list)
            print '\033[31Silver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, header_length, self.date_string, url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url,logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', 0, self.date_string, [], [], []

    def get_new_sightings_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            new_table = xml_soup.xpath('//div[@class="panel-body"]//table[@class="sightingPreviewTable"]')[1]
            table_string = etree.tostring(new_table.findall('tbody')[0])
            bs_soup = BeautifulSoup(table_string, 'html.parser')
            tr_list = bs_soup.find_all('tr')

            #todo 获取header_list
            th_list = tr_list[0].find_all('th')
            if th_list:
                header_list = list(tr_list[0].stripped_strings)
                cell_tr_list = tr_list[1:]
            else:
                header_list = [u'ID', u'Title', u'Priority', u'Severity', u'Owner', u'Closed Reason', u'Status', u'Subsystem', u'Promoted ID']
                cell_tr_list = tr_list

            effective_url_list = []
            for tr in cell_tr_list:
                url_list = []
                #todo 获取Key Sightings 列url链接
                temp_url_list = tr.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                if temp_url_list:
                    for soup_href in temp_url_list:
                        if soup_href:
                            string_url = soup_href.attrs
                            url_list.append(string_url['href'])
                    effective_url_list.append(url_list)
                else:
                    effective_url_list.append([])

                temp = list(tr.stripped_strings)
                cell_data_list.append(temp)

            #todo 当cell_data_list长度等于1时约定为当前周无数据 即页面数据为N/A
            if len(cell_data_list[0]) == 1:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            print '\033[31mheader_list:\t\033[0m', header_list
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list
            print '\033[32meffective_url_list:\t\033[0m', effective_url_list
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url,
                                      logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    def get_existing_sighting_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            new_table = xml_soup.xpath('//div[@class="panel-body"]//table[@class="sightingPreviewTable"]')[2]
            table_string = etree.tostring(new_table.findall('tbody')[0])
            bs_soup = BeautifulSoup(table_string, 'html.parser')
            tr_list = bs_soup.find_all('tr')

            #todo 获取header_list
            th_list = tr_list[0].find_all('th')
            if th_list:
                header_list = list(tr_list[0].stripped_strings)
                cell_tr_list = tr_list[1:]
            else:
                header_list = [u'ID', u'Title', u'Priority', u'Severity', u'Owner', u'Closed Reason', u'Status', u'Subsystem', u'Promoted ID']
                cell_tr_list = tr_list

            effective_url_list = []
            for tr in cell_tr_list:
                url_list = []
                #todo 获取Key Sightings 列url链接
                temp_url_list = tr.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                if temp_url_list:
                    for soup_href in temp_url_list:
                        if soup_href:
                            string_url = soup_href.attrs
                            url_list.append(string_url['href'])
                    effective_url_list.append(url_list)
                else:
                    effective_url_list.append([])

                temp = list(tr.stripped_strings)
                cell_data_list.append(temp)

            #todo 当cell_data_list长度等于1时约定为当前周无数据 即页面数据为N/A
            if len(cell_data_list[0]) == 1:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            print '\033[31mheader_list:\t\033[0m', header_list
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list
            print '\033[32meffective_url_list:\t\033[0m', effective_url_list
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    def get_closed_sightings_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            new_table = xml_soup.xpath('//div[@class="panel-body"]//table[@class="sightingPreviewTable"]')[3]
            table_string = etree.tostring(new_table.findall('tbody')[0])
            bs_soup = BeautifulSoup(table_string, 'html.parser')
            tr_list = bs_soup.find_all('tr')

            #todo 获取header_list
            th_list = tr_list[0].find_all('th')
            if th_list:
                header_list = list(tr_list[0].stripped_strings)
                cell_tr_list = tr_list[1:]
            else:
                header_list = [u'ID', u'Title', u'Priority', u'Severity', u'Owner', u'Closed Reason', u'Status', u'Subsystem', u'Promoted ID']
                cell_tr_list = tr_list

            effective_url_list = []
            for tr in cell_tr_list:
                url_list = []
                #todo 获取Key Sightings 列url链接
                temp_url_list = tr.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                if temp_url_list:
                    for soup_href in temp_url_list:
                        if soup_href:
                            string_url = soup_href.attrs
                            url_list.append(string_url['href'])
                    effective_url_list.append(url_list)
                else:
                    effective_url_list.append([])

                temp = list(tr.stripped_strings)
                cell_data_list.append(temp)

            #todo 当cell_data_list长度等于1时约定为当前周无数据 即页面数据为N/A
            if len(cell_data_list[0]) == 1:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            print '\033[31mheader_list:\t\033[0m', header_list
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list
            print '\033[32meffective_url_list:\t\033[0m', effective_url_list
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    def get_rework_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            new_table = xml_soup.xpath('//div[@class="panel-body"]/div/div/div/div')
            text_string = etree.tostring(new_table[0])
            text_soup = BeautifulSoup(text_string, 'html.parser')
            temp_list = []
            object_string_list = []
            child_tag_list = list(text_soup.children)
            for child in range(len(child_tag_list)):
                child_soup = BeautifulSoup(str(child_tag_list[child]), 'html.parser')
                string_list = list(child_soup.stripped_strings)
                string_list = remove_non_alphanumeric_characters(string_list)
                temp_list.extend(string_list)
            try:
                object_string_list = [temp_list[0] + ':', temp_list[1], ' '.join(temp_list[2:5]), temp_list[5] + ':',' '.join(temp_list[6:9]),
                                      temp_list[9], temp_list[10], '#' + ' '.join(temp_list[11:13]), '', temp_list[13] + ':',[temp_list[14], temp_list[15]],
                                      [temp_list[16], temp_list[17]], [temp_list[18], temp_list[19]],[temp_list[20],temp_list[21]]]
            except:
                object_string_list.extend(temp_list)

            print Silver_Gold_BKC_string, object_string_list, self.date_string
            return Silver_Gold_BKC_string, object_string_list, self.date_string
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url,
                                      logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', [], self.date_string

    def get_ifwi_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            table_list = xml_soup.xpath('//div[@class="panel-body"]//table[@class="MsoNormalTable"]')
            table_string = etree.tostring(table_list[0].findall('tbody')[0])
            bs_soup = BeautifulSoup(table_string, 'html.parser')
            tr_list = bs_soup.find_all('tr')

            th_list = tr_list[0].find_all('th')
            for th in th_list:
                th_string = list(th.stripped_strings)
                if th_string:
                    header_list.extend(th_string)

            for tr in tr_list[1:]:
                td_string_list = list(tr.stripped_strings)
                cell_data_list.append(td_string_list)
            print '\033[31mheader_list:\t\033[0m', header_list
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list
            print '\033[31mSilver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, self.date_string, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', self.date_string, [], []

    #todo 获取case result测试报告数据链接地址并将数据缓存到缓存目录 以方便通过缓存方式从get_caseresult_data接口获取测试报告数据
    def save_caseresult_url(self, bkc_flag):
        parent_caseresult_url = self.data_url
        if bkc_flag:
            parent_caseresult_url = parent_caseresult_url.replace('Silver', 'BKC')

        regex = re.compile(r'Detail case result could be found in this\s+<a href="(.*?)</div>', re.S | re.M)

        try:
            self.cache[parent_caseresult_url]
        except KeyError:
            parent_caseresult_url = parent_caseresult_url.replace('BKC', 'Gold')
            try:
                self.cache[parent_caseresult_url]
            except KeyError:
                parent_caseresult_url = parent_caseresult_url.replace('Gold', 'Silver')

        data = self.cache[parent_caseresult_url]
        header = re.findall(regex, data)
        temp_string = ''.join(header)
        page_url_sep = re.sub('\"', '', temp_string).split()[0]

        if page_url_sep.startswith('.'):
            pre_url_string = os.path.split(parent_caseresult_url)[0]
            page_url = pre_url_string + page_url_sep[1:]
        elif page_url_sep.startswith('/'):
            page_url = 'https:' + page_url_sep
        else:
            page_url = page_url_sep

        self.logger.print_message('page_url:\t%s' % page_url, self.__file_name)
        # TODO 是否离线标记获取
        on_off_line_save_flag = judge_get_config('on_off_line_save_flag', self.purl_bak_string)
        if on_off_line_save_flag == 'online':
            html = urllib2.urlopen(page_url, context=context).read()
            self.cache[page_url] = html

    def get_platform_data(self, data_type, bkc_flag=True):
        try:
            #todo 缓存case report页面数据
            self.save_caseresult_url(bkc_flag)
            Silver_Gold_BKC_string, xml_soup, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
            table_list = xml_soup.xpath('//div[@class="panel-body"]//table[@class="newTableCenterPreview"]')
            table_string = etree.tostring(table_list[0].findall('tbody')[0])
            bs_soup = BeautifulSoup(table_string, 'html.parser')
            tr_list = bs_soup.find_all('tr')

            #todo 获取header_list
            header_list = list(tr_list[0].stripped_strings)

            effective_url_list = []
            for tr in tr_list[1:]:
                url_list = []
                #todo 获取Key Sightings 列url链接
                temp_url_list = tr.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                if temp_url_list:
                    for soup_href in temp_url_list:
                        if soup_href:
                            string_url = soup_href.attrs
                            url_list.append(string_url['href'])
                    effective_url_list.append(url_list)
                else:
                    effective_url_list.append([])

                temp = list(tr.stripped_strings)
                cell_data_list.append(temp)

            print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            print '\033[32meffective_url_list:\t\033[0m', effective_url_list, len(effective_url_list)
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    #todo 获取case result最终测试报告
    def get_caseresult_data(self, data_type, bkc_flag=True):
        try:
            parent_caseresult_url = self.data_url
            Silver_Gold_BKC_string = 'Silver'
            tip_string = 'default_tip_string'
            cell_data_list = []

            if bkc_flag:
                parent_caseresult_url = parent_caseresult_url.replace('Silver', 'BKC')
                Silver_Gold_BKC_string = 'BKC'

            try:
                self.cache[parent_caseresult_url]
            except KeyError:
                parent_caseresult_url = parent_caseresult_url.replace('BKC', 'Gold')
                Silver_Gold_BKC_string = 'Gold'
                try:
                    self.cache[parent_caseresult_url]
                except KeyError:
                    Silver_Gold_BKC_string = 'Silver'
                    parent_caseresult_url = parent_caseresult_url.replace('Gold', 'Silver')

            data = self.cache[parent_caseresult_url]
            regex = re.compile(r'Detail case result could be found in this\s+<a href="(.*?)".*</div>', re.S | re.M)
            case_report_url = re.findall(regex, data)
            page_url_sep = case_report_url[0]

            if page_url_sep.startswith('.'):
                pre_url_string = os.path.split(parent_caseresult_url)[0]
                page_url = pre_url_string + page_url_sep[1:]
            elif page_url_sep.startswith('/'):
                page_url = 'https:' + page_url_sep
            else:
                page_url = page_url_sep

            self.logger.print_message(msg='page_url:\t%s' % page_url, logger_name=self.__file_name)
            html = self.cache[page_url]
            soup = BeautifulSoup(str(html), 'html.parser')
            #todo 获取数据部分头部的标记字符串  如Purley-FPGA WW12
            table_list = soup.find_all('table')
            table_tip = table_list[0]
            tip_string_list = list(table_tip.stripped_strings)
            if tip_string_list:
                tip_string = tip_string_list[0].strip(' ')
                temp = tip_string.split(' ')
                if temp:
                    tip_string = temp[0] + ' ' + temp[-1]
                    print tip_string
            #todo 获取有效的待插入数据
            cell_table = table_list[1]
            tr_list = cell_table.find_all('tr')

            if not tr_list:
                return self.date_string, 'Error', 'Error', [], []

            #todo 获取表列名
            header_list = list(tr_list[0].stripped_strings)
            #todo 获取表单元格数据
            for soup_tr in tr_list[1:]:
                tr_cell_data = list(soup_tr.stripped_strings)
                cell_data_list.append(tr_cell_data)

            print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            print '\033[32mtip_string:\t\033[0m', tip_string, len(tip_string)
            print '\033[32mSilver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            return self.date_string, Silver_Gold_BKC_string, tip_string, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url,
                                      logger_name=self.__file_name, definition_log_level=ERROR)
            return self.date_string, 'Error', 'Error', [], []




if __name__ == '__main__':
    #Purley-FPGA Bakerville
    import time
    start = time.time()
    key_url_list = []
    # f = open(r'C:\Users\pengzh5x\Desktop\machine_scripts\report_html\Purley-FPGA_url_info.txt', 'r')
    # for line in f:
    #     if 'Purley-FPGA' in line and 'Silver' in line:
    #         key_url_list.append(line.strip('\n'))

    cache = DiskCache('Bakerville')
    key_url_list = ['https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW52/17139_Silver.html',]
                    # 'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW34/6565_Silver.html',
                    # 'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW38/6706_Silver.html',
                    # 'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW37/6668_Silver.html']
    # key_url_list = ['https://dcg-oss.intel.com/ossreport/auto/Purley-FPGA/Silver/2017%20WW31/6464_Silver.html',]
    for url in key_url_list:
        obj = GetAnalysisData(url, 'Bakerville', get_info_not_save_flag=True, insert_flag=True, cache=cache)
        # obj.get_platform_data('PlatformIntegrationValidationResult', True)
        obj.get_caseresult_data('PlatformIntegrationValidationResult', True)
        # obj.get_sw_data('SWConfiguration', True)
        # obj.get_sw_data_1('SW Configuration', True)
        # obj.get_ifwi_data('IFWIConfiguration', True)
        # obj.get_hw_data('HWConfiguration', True)
        # obj.get_lastest_FPGA_hw_data('HW Configuration', True)
        # obj.get_bak_hw_data('HW Configuration', True)
        # obj.get_lastest_bak_hw_data('HW Configuration', True)
        # obj.get_existing_sighting_data('KeySightings', True)
        # obj.get_new_sightings_data('KeySightings', True)
        # obj.get_bak_rework_data('HW Rework', True)
        # obj.get_closed_sightings_data('KeySightings', True)
        # obj.get_rework_data('HWRework', True)
    print time.time() - start