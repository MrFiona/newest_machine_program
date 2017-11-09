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
from functools import wraps
from logging import ERROR, CRITICAL

from bs4 import BeautifulSoup

from machine_scripts.cache_mechanism import DiskCache
from machine_scripts.public_use_function import remove_line_break, judge_get_config
from setting_global_variable import REPORT_HTML_DIR
from machine_scripts.common_interface_func import remove_non_alphanumeric_characters


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
        self._page_url = None
        self._parent_caseresult_url = self.data_url

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
                        return '', [], [], []

            search_file_list = os.listdir(self.save_file_path)
            bkc_file_name = ''
            for file in search_file_list:
                match = re.match(r'\d+', file)
                if match:
                    bkc_file_name = file
            if len(bkc_file_name) == 0:
                print 'BKC and Gold file is not exists!!!'
                return '', [], [], []
            self.save_file_name = os.path.split(self.data_url)[-1].split('.')[0] + '_html'
            self.save_file_name = bkc_file_name

        data = self.cache[self.data_url]
        #todo 提取HW Configuration部分的代码
        regex = re.compile(r'<span class="sh2">&nbsp; %s </span>(.*?)<div class="panel-heading">' % data_type, re.S | re.M)
        header = re.findall(regex, data)
        string_data = ''.join(header)
        #todo 提取所有的tr部分
        soup_table = BeautifulSoup(string_data, 'html.parser')
        table_list = soup_table.find_all(re.compile('table'))

        #todo 增加保险措施，通过关键字提取文本html实现
        if not table_list:
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
            table_list = soup.find_all('table')

        #todo 当没有数据时应该返回空防止误判为提取数据Error
        if not table_list:
            return Silver_Gold_BKC_string, table_list, header_list, cell_data_list
        else:
            return Silver_Gold_BKC_string, table_list[0], header_list, cell_data_list

    #todo 获取page_url有两种方式获取，依次尝试是否成功获取
    def _get_common_page_url(self):
        try:
            regex = re.compile(r'Detail case result could be found in this\s+<a href="(.*?)</div>', re.S | re.M)
            data = self.cache[self._parent_caseresult_url]
            header = re.findall(regex, data)
            temp_string = ''.join(header)
            page_url_sep = re.sub('\"', '', temp_string).split()[0]

            if page_url_sep.startswith('.'):
                pre_url_string = os.path.split(self._parent_caseresult_url)[0]
                self._page_url = pre_url_string + page_url_sep[1:]
            elif page_url_sep.startswith('/'):
                self._page_url = 'https:' + page_url_sep
            else:
                self._page_url = page_url_sep
            urllib2.urlopen(self._page_url, context=context).read()
        except:
            #TODO 更具self.data_url来计算出page_url
            page_url = self._parent_caseresult_url[:-5] + '_files/'
            html = urllib2.urlopen(page_url, context=context).read().encode('utf-8')
            soup_html = BeautifulSoup(str(html), 'html.parser')
            li_list = soup_html.find_all('li')

            target_url_string = ''
            for ele in li_list:
                #todo 在Purley-Crystal-Ridge项目WW44周的时候 BKC有两个满足条件的file，更新以第一个找到的文件为准
                if 'detailed_case' in str(ele):
                    target_url_string = ele
                    break

            url_string_sep = re.findall('<a href="(.*?)">', str(target_url_string), re.M | re.S)
            page_url = ''.join([page_url, url_string_sep[0].replace(' ', '')])
            self._page_url = page_url

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
                            temp_change_list = [nu for nu in range(int(range_num_list[0]), int(range_num_list[1]) + 1)]
                            temp_num_list.extend(temp_change_list)
            if temp_num_list:
                effective_num_list.append(temp_num_list)

        effective_header_list = [int(ele) for child_element in effective_num_list for ele in child_element]
        effective_header_list = sorted(effective_header_list, key=lambda x: x)
        #todo SKX_DE标记开启,自动填充至12 表示12列数据
        if SKX_DE_FLAG:
            for i in range(len(effective_header_list)+1, 12+1):
                effective_header_list.append(i)
        effective_header_list = ['System ' + str(ele) for ele in effective_header_list]
        # print 'effective_num_list:\t', effective_num_list
        # print 'effective_header_list:\t', effective_header_list

        return effective_header_list, effective_num_list

    #todo 判断插入到cell_data_list的次数并插入数据
    def _insert_numers_to_cell_data_list(self, cell_data_list):
        try:
            effective_header_list, effective_num_list = self._get_hw_effective_header_list(cell_data_list[0])
            for node_list in effective_num_list:
                left_half_section = node_list[0]
                try:
                    right_half_section = node_list[1] + 1
                except IndexError:
                    right_half_section = left_half_section + 1
                for col in range(left_half_section-1, right_half_section-2):
                    for i in range(len(cell_data_list)):
                        if col >= len(cell_data_list[i]) - 1:
                            cell_data_list[i].append( cell_data_list[i][-1] )
                        elif col < len(cell_data_list[i]) - 1:
                            cell_data_list[i].insert( col, cell_data_list[i][col] )
        except (ValueError, IndexError) as e:
            self.logger.print_message(e, self.__file_name, definition_log_level=40)
        return cell_data_list

    def save_caseresult_url(self, bkc_flag):
        if bkc_flag:
            self._parent_caseresult_url = self._parent_caseresult_url.replace('Silver', 'BKC')

        try:
            self.cache[self._parent_caseresult_url]
        except KeyError:
            self._parent_caseresult_url = self._parent_caseresult_url.replace('BKC', 'Gold')
            try:
                self.cache[self._parent_caseresult_url]
            except KeyError:
                self._parent_caseresult_url = self._parent_caseresult_url.replace('Gold', 'Silver')

        #todo 获取page_url
        self._get_common_page_url()

        self.logger.print_message('page_url:\t%s' % self._page_url, self.__file_name)
        #TODO 是否离线标记获取
        on_off_line_save_flag = judge_get_config('on_off_line_save_flag', self.purl_bak_string)
        if on_off_line_save_flag == 'online':
            html = urllib2.urlopen(self._page_url, context=context).read()
            self.cache[self._page_url] = html

    #todo 判断插入到cell_data_list的次数并插入数据
    #todo 根据表头列数字和cell_data_list进一步处理,生成新的cell_data_list,effective_num_list
    def _insert_bak_numers_to_cell_data_list(self, effective_num_list, cell_data_list):
        cell_data_direction_dict = collections.OrderedDict()
        for ele in range(len(effective_num_list)):
            for k in effective_num_list[ele]:
                temp_cell_data_list = []
                for j in range(len(cell_data_list)):
                    temp_cell_data_list.append(cell_data_list[j][ele])
                cell_data_direction_dict[k] = temp_cell_data_list
                # print k, cell_data_direction_dict
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
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            tr_list = soup_table_element.find_all('tr')
            #todo 循环处理tr中的代码，提取出excel表头信息，存放在表头列表header_list
            effective_header_list = []

            for soup_tr in tr_list[1:]:
                #todo 排除其他非td杂项
                if soup_tr.td != None:
                    #todo 排除td中无字符串的情况
                    if soup_tr.td.strings != None:
                        left_string_list = list(soup_tr.td.stripped_strings)
                        if left_string_list:
                            data = left_string_list[0]
                            data = data.replace('\n', '')
                            header_list.append(data)
                td_data_list = soup_tr.find_all('td')
                #todo 获取td中的字符串即待插入excel表中单元格中的数据部分
                temp = []
                for td_soup in td_data_list:
                    td_string_list = list(td_soup.stripped_strings)
                    #todo 去掉可能出现的html注释
                    td_string_list = [ element for element in td_string_list if '<!--' not in element ]
                    if td_string_list:
                        td_data = ''.join(td_string_list)
                        temp.append(td_data)
                if temp:
                    temp = remove_non_alphanumeric_characters(temp)
                    cell_data_list.append(temp[1:])
            #todo 适配html表列名对应行中含有标签不含有td标签
            th_list = tr_list[0].find_all('th')
            #todo 去除首行第一个无效
            th_list = th_list[1:]
            for string_soup in th_list:
                th_strings_list = list(string_soup.stripped_strings)
                #todo 信息可能会在多个标签
                th_strings_list = [re.sub('[\r\n\xc2\xa0 ]', '', element) for element in th_strings_list]
                multiple_th_string = ''.join(th_strings_list)
                effective_header_list.append(multiple_th_string)
                cell_data_list.insert(0, effective_header_list)
            #todo 处理Purley-Crystal-Ridge项目HW表第一行表头信息
            effective_header_list = [re.sub('-', '~', element) for element in effective_header_list]
            effective_header_list, effective_num_list = self._get_hw_effective_header_list(effective_header_list)

            cell_data_list = self._insert_numers_to_cell_data_list(cell_data_list)
            header_list = remove_non_alphanumeric_characters(header_list)
            if cell_data_list:
                cell_data_list[0] = effective_header_list
            header_list = header_list[ -(len(cell_data_list) -1): ]
            try:
                if header_list[0].startswith('Ingredient'):
                    header_list = header_list[1:]
            except IndexError:
                pass
            cell_data_list = cell_data_list[ -(len(header_list)): ]
            # print '\033[32meffective_header_list:\t\033[0m', effective_header_list, len(effective_header_list)
            # effective_header_list = [UnicodeDammit(ele).original_encoding for ele in effective_header_list]
            # print '\033[33meffective_header_list:\t\033[0m', effective_header_list, len(effective_header_list)
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            return Silver_Gold_BKC_string, self.date_string, effective_header_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', 'Error', [], [], []

    def judge_silver_bkc_func(self, data_type, bkc_flag):
        Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
        return  Silver_Gold_BKC_string, tr_list, header_list, cell_data_list

    def get_sw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, 0, self.date_string, [], [], []

            tr_list = soup_table_element.find_all('tr')

            header_list = list(tr_list[0].stripped_strings)
            header_length = len(header_list)
            # print 'header_length:\t', header_length
            header_list = header_list[:4]
            url_list = []

            for soup_tr in tr_list[1:]:
                temp_url_list = []; temp_string_list = []
                td_list = soup_tr.find_all('td')
                #todo 默认情况是正常列数
                actual_td_list = td_list
                num = len(td_list)
                if num == header_length + 1:
                    string_5_list = []
                    for td in soup_tr:
                        soup_td = BeautifulSoup(str(td), 'html.parser')
                        soup_td_list = list(soup_td.stripped_strings)
                        if soup_td_list:
                            string_5_list.append(''.join(soup_td_list))
                    temp_string_list = string_5_list[1:]
                    actual_td_list = td_list[1:]
                elif num == header_length + 2:
                    actual_td_list = td_list[2:]
                    string_6_list = []
                    for td in soup_tr:
                        soup_td = BeautifulSoup(str(td), 'html.parser')
                        soup_td_list = list(soup_td.stripped_strings)
                        if soup_td_list:
                            string_6_list.append(''.join(soup_td_list))
                    temp_string_list = string_6_list[2:]
                elif num <= header_length:
                    string_4_list = []
                    for td in soup_tr:
                        soup_td = BeautifulSoup(str(td), 'html.parser')
                        soup_td_list = list(soup_td.stripped_strings)
                        if soup_td_list:
                            string_4_list.append(''.join(soup_td_list))
                    temp_string_list = string_4_list

                #todo 获取cell_data_list数据
                temp_string_list = remove_non_alphanumeric_characters(temp_string_list)
                # print '\033[33mtemp_string_list:\t\033[0m', temp_string_list, len(temp_string_list)
                if len(temp_string_list) > 4:
                    temp_string_list = temp_string_list[:4]
                if temp_string_list:
                    cell_data_list.append(temp_string_list)

                for td in actual_td_list:
                    #todo 匹配url链接
                    if td.a:
                        #todo 去除链接里的垃圾
                        temp_url_list.append(td.a['href'].split()[0])

                if temp_url_list:
                    url_list.append(temp_url_list)
            if header_length >= 4:
                header_length = 4
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            # print '\033[31murl_list:\t\033[0m', url_list, len(url_list)
            # print '\033[31mSilver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, header_length, self.date_string, url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', 0, self.date_string, [], [], []

    def get_ifwi_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, self.date_string, [], []

            tr_list = soup_table_element.find_all('tr')

            for soup_tr in tr_list:
                th_list = soup_tr.find_all('th')
                if soup_tr == tr_list[0]:
                    for th in th_list:
                        th_string = re.findall('>(.*?)<', str(th))
                        if th_string:
                            header_list.append(th_string[0])
                if not th_list:
                    td_string_list = list(soup_tr.stripped_strings)
                    #todo 去掉首位字符串开头的空格,排除空格的影响 后续会排序
                    if td_string_list:
                        td_string_list[0] = td_string_list[0].lstrip(' ')
                    cell_data_list.append(td_string_list)
            # print '\033[31mheader_list:\t\033[0m', header_list
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            # print '\033[31mSilver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, self.date_string, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', self.date_string, [], []

    def get_platform_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)
            self.save_caseresult_url(bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            tr_list = soup_table_element.find_all('tr')

            effective_url_list = []
            for soup_tr in tr_list:
                temp = []; url_list = []
                th_list = soup_tr.find_all('th'); td_list = soup_tr.find_all('td')
                #todo 获取header_list
                if th_list:
                    for th in soup_tr.stripped_strings:
                        header_list.append(th)
                if td_list:
                    #todo 获取url链接
                    temp_url_list = soup_tr.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                    # print 'temp_url_list:\t', temp_url_list
                    if temp_url_list:
                        for ele in temp_url_list:
                            soup_href = BeautifulSoup(str(ele), 'html.parser')
                            if soup_href:
                                string_url = soup_href.a['href']
                                url_list.append(string_url)
                        effective_url_list.append(url_list)
                    else:
                        effective_url_list.append([])
                    #todo 需要循环处理，防止丢失无内容的项
                    for td_soup in td_list:
                        temp_list = list(td_soup.stripped_strings)
                        if not temp_list:
                            temp.append('')
                            continue
                        for k in temp_list:
                            temp.append(k)
                    cell_data_list.append(temp)
            header_list = header_list[1:]
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            # print '\033[32meffective_url_list:\t\033[0m', effective_url_list, len(effective_url_list)
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    def get_rework_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, [], self.date_string

            tr_list = soup_table_element.find_all('tr')

            object_string_list = []
            for soup_tr in tr_list:
                h4_list = soup_tr.find_all('h4')
                for h4_soup in h4_list:
                    temp_string = list(h4_soup.stripped_strings)
                    # print 'temp_string:\t', temp_string
                    for i in range(len(temp_string)):
                        object_string_list.append(temp_string[i])
                    if len(object_string_list) == 2:
                        object_string_list.append('')

                if len(object_string_list) < 10:
                    #todo 得到tr节点下的所有文本
                    text = list(soup_tr.td.children)
                    object_string_list = []
                    for child in text:
                        soup_son = BeautifulSoup(str(child), 'html.parser')
                        child_tag_string_list = list(soup_son.stripped_strings)
                        if not child_tag_string_list:
                            continue
                        temp_string = ''.join(child_tag_string_list).strip(' ')
                        object_string_list.append(temp_string)
            #todo 对提取的字符串列表进行清洗，统一组合格式：空格分隔  Mon Apr 10 14:00:27 2017
            object_string_list = remove_non_alphanumeric_characters(object_string_list)
            # print object_string_list, len(object_string_list); print Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, object_string_list, self.date_string
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', [], self.date_string

    def get_existing_sighting_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            tr_list = soup_table_element.find_all('tr')

            #todo 获取链接地址
            cell_last_data = [] ;effective_url_list = []
            for soup_tr in tr_list:
                if soup_tr == tr_list[0]:
                    header_list = list(soup_tr.stripped_strings)
                    continue

                temp = [] ;cell_last_string_list = [] ;url_list = []
                td_list = soup_tr.find_all('td')
                for soup_td in td_list:
                    #todo 获取url链接
                    temp_url_list = soup_td.find_all('a')
                    if temp_url_list:
                        for ele in temp_url_list:
                            soup_href = BeautifulSoup(str(ele), 'html.parser')
                            string_list = list(soup_href.a.stripped_strings)

                            if string_list:
                                cell_last_string_list.append(string_list[0])

                            string_url = soup_href.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                            if string_url:
                                #todo 排除无效的url
                                if re.search('.*id="></a>$', str(string_url[0])):
                                    continue
                                #todo 提取有效的url链接
                                for url in string_url:
                                    url_soup = BeautifulSoup(str(url), 'html.parser')
                                    url = url_soup.a['href']
                                    url_list.append(url)

                    if soup_td.strings:
                        td_son_list = list(soup_td.stripped_strings)
                        ( temp.append(td_son_list[0]) if len(td_son_list) == 1 else temp.append(td_son_list[-1]) ) \
                            if len(td_son_list) != 0 else temp.append('')

                cell_last_data.append(cell_last_string_list)
                #todo 去除多余的换行符和空格，防止插入excel表格时报 255 characters since it exceeds Excel's limit for URLS 长度超过限定长度
                for k in range(len(url_list)):
                    url_list[k] = re.sub('[\s]', '', url_list[k])
                effective_url_list.append(url_list)
                #todo 移除非字母数字字符
                temp = remove_non_alphanumeric_characters(temp)
                cell_data_list.append(temp)

            for k in range(len(cell_data_list)):
                cell_data_list[k].pop()
                if len(cell_last_data[k]) >= 2:
                    for e in cell_last_data[k][1:]:
                        cell_data_list[k].append(e)
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            # print '\033[32meffective_link_address_list:\t\033[0m', effective_url_list, len(effective_url_list)
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    def get_new_sightings_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            tr_list = soup_table_element.find_all('tr')

            effective_url_list = []
            for soup_tr in tr_list:
                url_list = []; temp = []
                th_list = soup_tr.find_all('th'); td_list = soup_tr.find_all('td')
                if th_list:
                    header_list = list(soup_tr.stripped_strings)
                if td_list:
                    #todo 获取url链接
                    temp_url_list = soup_tr.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                    if temp_url_list:
                        #todo 提取有效的url链接
                        for url in temp_url_list:
                            url_soup = BeautifulSoup(str(url), 'html.parser')
                            url = url_soup.a['href']
                            #todo 排除无效的url 无效的url id后不跟数字
                            if not re.search('(\d+)$', str(url)):
                                continue
                            url_list.append(url)
                        effective_url_list.append(url_list)
                    #todo 需要循环处理，防止丢失无内容的项
                    for td in td_list:
                        td_soup = BeautifulSoup(str(td), 'html.parser')
                        if td_soup.td:
                            temp_list = list(td_soup.td.stripped_strings)
                            if not temp_list:
                                temp.append('')
                                continue
                            if temp_list:
                                temp.append(temp_list[0])
                    temp = remove_non_alphanumeric_characters(temp)
                    cell_data_list.append(temp)

            # print '\033[31mheader_list:\t\033[0m', header_list
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list
            # print '\033[32meffective_url_list:\t\033[0m', effective_url_list
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    def get_closed_sightings_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, soup_table_element, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not soup_table_element:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            tr_list = soup_table_element.find_all('tr')

            effective_url_list = []
            for soup_tr in tr_list:
                url_list = [] ;temp = []
                th_list = soup_tr.find_all('th') ;td_list = soup_tr.find_all('td')
                if th_list:
                        header_list = list(soup_tr.stripped_strings)
                if td_list:
                    #todo 获取url链接
                    temp_url_list = soup_tr.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                    if temp_url_list:
                        for ele in temp_url_list:
                            soup_href = BeautifulSoup(str(ele), 'html.parser')
                            string_url = soup_href.a['href']
                            url_list.append(string_url)
                        effective_url_list.append(url_list)
                    #todo 需要循环处理，防止丢失无内容的项
                    for td in td_list:
                        td_soup = BeautifulSoup(str(td), 'html.parser')
                        if td_soup and td_soup.td:
                            temp_list = list(td_soup.td.stripped_strings)
                            if not temp_list:
                                temp.append('')
                                continue
                            if temp_list:
                                temp.append(temp_list[0])
                    temp = remove_non_alphanumeric_characters(temp)
                    cell_data_list.append(temp)
            # print '\033[31mheader_list:\t\033[0m', header_list
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list
            # print '\033[32meffective_url_list:\t\033[0m', effective_url_list
            return Silver_Gold_BKC_string, self.date_string, effective_url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', self.date_string, [], [], []

    def get_caseresult_data(self, data_type, bkc_flag=True):
        try:
            self._parent_caseresult_url = self.data_url
            Silver_Gold_BKC_string = 'Silver'
            tip_string = 'default_tip_string'

            if bkc_flag:
                self._parent_caseresult_url = self._parent_caseresult_url.replace('Silver', 'BKC')
                Silver_Gold_BKC_string = 'BKC'

            try:
                self.cache[self._parent_caseresult_url]
            except KeyError:
                self._parent_caseresult_url = self._parent_caseresult_url.replace('BKC', 'Gold')
                Silver_Gold_BKC_string = 'Gold'
                try:
                    self.cache[self._parent_caseresult_url]
                except KeyError:
                    Silver_Gold_BKC_string = 'Silver'
                    self._parent_caseresult_url = self._parent_caseresult_url.replace('Gold', 'Silver')

            #TODO 获取page_url
            self._get_common_page_url()

            self.logger.print_message(msg='page_url:\t%s' % self._page_url, logger_name=self.__file_name)
            html = self.cache[self._page_url]
            soup = BeautifulSoup(str(html), 'html.parser')
            #todo 获取数据部分头部的标记字符串  Purley-FPGA WW12
            table_tip_list = soup.find_all('table')
            if table_tip_list:
                table_tip = table_tip_list[0]
                if table_tip:
                    tip_string_list = list(table_tip.stripped_strings)
                    if tip_string_list:
                        tip_string = tip_string_list[0].strip(' ')
                        temp = tip_string.split(' ')
                        if temp:
                            tip_string = temp[0] + ' ' + temp[-1]
            #todo 获取有效的待插入数据
            table_list = soup.find_all('table')
            if len(table_list) >= 2:
                tr_list = table_list[1].find_all('tr')
                header_list = [] ;cell_data_list = []

                if not tr_list:
                    return self.date_string, '', '', [], []

                #todo 获取表列名
                for soup_tr in tr_list:
                    temp = []
                    th_list = soup_tr.find_all('th');td_list = soup_tr.find_all('td')
                    if th_list:
                        header_list = list(soup_tr.stripped_strings)
                    #todo 获取表单元格数据
                    if td_list:
                        #todo 需要循环处理，防止丢失无内容的项
                        for td_soup in td_list:
                            if td_soup:
                                temp_list = list(td_soup.stripped_strings)
                                if not temp_list:
                                    temp.append('')
                                    continue
                                if temp_list:
                                    temp.append(temp_list[0])
                        cell_data_list.append(temp)
                # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
                # print '\033[32mtip_string:\t\033[0m', tip_string, len(tip_string)
                # print '\033[32mSilver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
                # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
                return self.date_string, Silver_Gold_BKC_string, tip_string, header_list, cell_data_list

            else:
                return self.date_string, '', '', [], []

        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return self.date_string, 'Error', 'Error', [], []



if __name__ == '__main__':
    #Purley-FPGA Bakerville
    import time
    start = time.time()
    key_url_list = []
    f = open(r'C:\Users\pengzh5x\Desktop\machine_scripts\report_html\Purley-Crystal-Ridge_url_info.txt', 'r')
    # for line in f:
    #     if 'Purley-Crystal-Ridge' in line and 'Silver' in line:
    #         key_url_list.append(line.strip('\n'))

    cache = DiskCache('Purley-Crystal-Ridge')
    key_url_list = ['https://dcg-oss.intel.com/ossreport/auto/Purley-Crystal-Ridge/Silver/2017%20WW44/7020_Silver.html']
    for url in key_url_list:
        obj = GetAnalysisData(url, 'Purley-Crystal-Ridge', get_info_not_save_flag=True, insert_flag=True, cache=cache)
        # obj.get_closed_sightings_data('Closed Sightings', True)
        # obj.get_new_sightings_data('New Sightings', True)
        # obj.get_existing_sighting_data('Existing Sightings', True)
        #print 'data_url:\t', self.data_url
        # obj.get_closed_sightings_data('Closed Sightings', True)
        # obj.get_rework_data('HW Rework')
        # obj.get_hw_data('HW Configuration', True)
        obj.get_sw_data('SW Configuration', True)
        # obj.get_ifwi_data('IFWI Configuration', True)
        # obj.get_platform_data('Platform Integration Validation Result', True)
        # obj.get_caseresult_data('Platform Integration Validation Result', True)
    print time.time() - start
    # import pstats
    # p = pstats.Stats('mkm_run.prof')
    # print p.strip_dirs().sort_stats('cumtime').print_stats(10, 10, '.*')

#\xe2\u20ac\u2122t '
#\u2019 '右单引号
#\u2018 '左单引号
#OrderedDict([(u'\xe2', 226), (u'\u2018', 8216), (u'\u2019', 8217), (u'\u20ac', 8364), (u'\u2122', 8482)])
    # unicode_character_list = set()
    # import collections
    # temp_list = collections.OrderedDict()
    # for num in range(sys.maxunicode+1):
    #     unicode_character_list.add(unichr(num))
    #     if unichr(num) in [u'\u2018', u'\u2019', u'\u20ac', u'\u2122', u'\xe2']:
    #         print unichr(num)
    #         temp_list[unichr(num)] = num
    # print unicode_character_list
    # print temp_list