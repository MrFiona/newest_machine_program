#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-03-21 09:40
# Author  : MrFiona
# File    : extract_data.py
# Software: PyCharm Community Edition

from __future__ import absolute_import

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
from machine_scripts.common_interface_branch_func import extract_sw_data_deal_bracket


# 强制ssl使用TLSv2
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

    #提取通用的部分,如果bkc_flag=True并且BKC和Gold都没有数据则取Silver数据 优先级：BKC > Gold > Silver
    def _common_regex(self, data_type, bkc_flag=False, replace_flag=False, header_list=None, cell_data_list=None):
        Silver_Gold_BKC_string = 'Silver'
        if not header_list:
            header_list = []
        if not cell_data_list:
            cell_data_list = []

        #BKC标记开启，自动更换为文件BKC地址
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
                print 'BKC and Gold file is not exists!!!'
                return '', [], [], []
            self.save_file_name = os.path.split(self.data_url)[-1].split('.')[0] + '_html'
            self.save_file_name = bkc_file_name

        data = self.cache[self.data_url]
        # 提取HW Configuration部分的代码
        regex = re.compile(r'<span class="sh2">&nbsp; %s </span>(.*?)<div class="panel-heading">' % data_type, re.S | re.M)
        header = re.findall(regex, data)
        string_data = ''.join(header)
        # 提取所有的tr部分
        soup_tr = BeautifulSoup(string_data, 'html.parser')
        tr_list = soup_tr.find_all(re.compile('tr'))

        #增加保险措施，通过关键字提取文本html实现
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

        return Silver_Gold_BKC_string, tr_list, header_list, cell_data_list

    #获取hw有效的列名列表
    def _get_hw_effective_header_list(self, effective_header_list):
        # 提取有效的行数
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
        # 提取有效的行数
        effective_num_list = []
        header_regex = re.compile('[Ss]ystem(?P<name>\(?.*\)?)', re.M | re.S)
        element_regex = re.compile('\d+')
        range_num_regex = re.compile('\d+?\,?~\d+')
        #判断周表头列是否含有SKX-DE
        SKX_DE_FLAG = False
        for label in range(len(effective_header_list)):
            temp_num_list = []
            temp_string_list = re.split(header_regex, effective_header_list[label])
            temp_string_list = remove_line_break(temp_string_list, empty_string=True)
            temp_string = re.sub('[()]', '', temp_string_list[0])
            header_list.append(temp_string)
            #进一步提取表头列数
            #排除类似这种情况 SKX-DE(001,~004)(Cycling Test)
            if temp_string_list[0].startswith('SKX-DE'):
                SKX_DE_FLAG = True
                continue
            #1、数字之间逗号相隔且不含有连续数字符号~
            if '~' not in temp_string:
                signal_num_list = re.findall(element_regex, temp_string)
                if signal_num_list:
                    signal_num_list = [int(ele) for ele in signal_num_list]
                    temp_num_list.extend(signal_num_list)
                # print 'temp_num_list:\t', temp_num_list
            #含有连续数字符号~  (1,~5)  (1~5)  1~5
            else:
                if ',' not in temp_string:
                    #不含有逗号只含有~
                    range_num_list = re.findall('\d+', temp_string)
                    if range_num_list:
                        #转换为离散的数字列
                        temp_change_list = [nu for nu in range(int(range_num_list[0]), int(range_num_list[1]) + 1)]
                        temp_num_list.extend(temp_change_list)
                #既含有逗号又含有~ (1,~5) 1,~5 (1,3~6) 1,2~5
                else:
                    #去括号
                    temp_string = re.sub('[()]', '', temp_string)
                    judge_string_list = re.findall('\d+~\d+', temp_string)
                    #说明是 (1,2~7)这样的情况 ~左右数字齐全
                    # print 'judge_string_list:\t',judge_string_list
                    if judge_string_list:
                        temp_list = []
                        split_string_list = [ele for ele in re.split(',', temp_string) if len(ele) != 0]
                        print 'split_string_list:\t', split_string_list
                        for deal_num in split_string_list:
                            #2~6
                            if '~' in deal_num:
                                range_num_list = re.findall('\d+', deal_num)
                                temp_list = [nu for nu in range(int(range_num_list[0]), int(range_num_list[1]) + 1)]
                            #单个数字 2
                            else:
                                temp_list.append(int(deal_num))
                            temp_num_list.extend(temp_list)
                        print temp_num_list
                    #说明是 (1,~5)这种情况
                    else:
                        range_num_list = re.findall('\d+', temp_string)
                        if range_num_list:
                            # 转换为离散的数字列
                            temp_change_list = [nu for nu in range(int(range_num_list[0]), int(range_num_list[1]) + 1)]
                            temp_num_list.extend(temp_change_list)
            if temp_num_list:
                effective_num_list.append(temp_num_list)

        effective_header_list = [int(ele) for child_element in effective_num_list for ele in child_element]
        effective_header_list = sorted(effective_header_list, key=lambda x: x)
        #SKX_DE标记开启,自动填充至12 表示12列数据
        if SKX_DE_FLAG:
            for i in range(len(effective_header_list)+1, 12+1):
                effective_header_list.append(i)
        effective_header_list = ['System ' + str(ele) for ele in effective_header_list]
        # print 'effective_num_list:\t', effective_num_list
        # print 'effective_header_list:\t', effective_header_list

        return effective_header_list, effective_num_list

    #判断插入到cell_data_list的次数并插入数据
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

    # 判断插入到cell_data_list的次数并插入数据
    # 根据表头列数字和cell_data_list进一步处理,生成新的cell_data_list,effective_num_list
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
        # 重复拷贝信息的次数
        repeat_append_num = 12 - len(effective_cell_data_list[0])
        # 不管是否含有SKX_DE，只要小于12列后面的列就用最后一列信息补充
        if repeat_append_num > 0:
            for m in range(len(cell_data_list)):
                for nu in range(repeat_append_num):
                    effective_cell_data_list[m].append(cell_data_list[m][-1])

        return effective_cell_data_list

    def get_hw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)
            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], [], []
            # 循环处理tr中的代码，提取出excel表头信息，存放在表头列表header_list
            effective_header_list = []
            for t in tr_list:
                soup_td = BeautifulSoup(str(t), 'html.parser')
                # 排除其他非td杂项
                if soup_td.td != None:
                    # 排除td中无字符串的情况
                    if soup_td.td.strings != None:
                        left_string_list = list(soup_td.td.strings)
                        # 适配，去除字符串列表中的多余字符   最终列表长度为1
                        left_string_list = remove_line_break(left_string_list, line_break=True)
                        if left_string_list:
                            data = left_string_list[0].encode('utf-8')
                            # 去除header_list元素中换行符
                            data = data.replace('\n', '')
                            # 排除字符串部分为非字母数字的td
                            header_list.append(data)
                td_data_list = soup_td.find_all('td')
                # 获取td中的字符串即待插入excel表中单元格中的数据部分
                temp = []
                for td in td_data_list:
                    get_td_data = BeautifulSoup(str(td), 'html.parser')
                    td_string_list = list(get_td_data.td.strings)
                    td_string_list = remove_line_break(td_string_list, line_break=True)
                    if td_string_list:
                        td_data = td_string_list[0].encode('utf-8')
                        # 去除cell_data_list元素中的非字母编码部分
                        td_data = re.sub('[\xc2\xa0\xc3\x82]', '', td_data)
                        temp.append(td_data)
                        # 获取有效的列表明列表
                        if t == tr_list[0]:
                            if td != td_data_list[0]:
                                effective_header_list.append(td_data)
                                effective_header_list, effective_num_list = self._get_hw_effective_header_list(effective_header_list)
                if temp:
                    temp = remove_non_alphanumeric_characters(temp)
                    cell_data_list.append(temp[1:])
                #适配html表列名对应行中含有标签不含有td标签
                if t == tr_list[0]:
                    if not effective_header_list:
                        th_soup = BeautifulSoup(str(tr_list[0]), 'html.parser')
                        th_list = th_soup.find_all('th')
                        th_list = th_list[1:]
                        for word in th_list:
                            string_soup = BeautifulSoup(str(word), 'html.parser')
                            th_strings_list = list(string_soup.strings)
                            # todo 去除换行符
                            remove_line_break(th_strings_list, line_break=True, second_method=True)
                            effective_header_list.append(th_strings_list[0])
                            cell_data_list.insert(0, effective_header_list)
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
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            return Silver_Gold_BKC_string, self.date_string, effective_header_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', 'Error', [], [], []

    # TODO DE和FPGA DE:24周之后 FPGA: 23周之后 hw格式更改
    def get_lastest_bak_hw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return 'Error', 'Error', [], [], []

            search_td_container_list = []
            temp_header_list = []
            effective_search_td_container_list = []
            effective_cell_data_td_list = []

            # print 'tr_list:\t', tr_list

            #todo 按行将信息加入列表 按列存储
            for tr in tr_list:
                soup_tr = BeautifulSoup(str(tr), 'html.parser')
                judge_th_exist = soup_tr.find_all('th')
                td_list = soup_tr.find_all('td')

                if not search_td_container_list:
                    for th in judge_th_exist:
                        search_td_container_list.append([th])
                else:
                    if td_list:
                        for index in range(len(search_td_container_list)):
                            search_td_container_list[index].append(td_list[index])
                    else:
                        for index in range(len(search_td_container_list)):
                            search_td_container_list[index].append(judge_th_exist[index])

            # TODO 根据Item位置进行确定
            separate_item_index_list = []
            for i in range(len(search_td_container_list[0])):
                if re.match('.*Item.*', str(search_td_container_list[0][i])):
                    separate_item_index_list.append(i)
            item_index = max(separate_item_index_list)

            # TODO 提取表左列值列表
            for header_ele in search_td_container_list[0]:
                header_soup = BeautifulSoup(str(header_ele), 'html.parser')
                temp = list(header_soup.strings)
                if temp:
                    temp_header_list.append(temp[0])
            # print 'effective_header_list:\t', temp_header_list, item_index
            if item_index:
                header_list = temp_header_list[1:item_index]
            else:
                header_list = temp_header_list[1:]
            # print 'search_td_container_list:\t', search_td_container_list

            #todo 两个table组合成一个table  虽然是24周以后但是却没有出现两个table而只是一个table，item_index为0则一个table
            for ele_list in search_td_container_list[1:]:
                if item_index:
                    effective_search_td_container_list.append(ele_list[0:item_index])
                    effective_search_td_container_list.append(ele_list[item_index:])
                else:
                    effective_search_td_container_list.append(ele_list)
            # print '\neffective_search_td_container_list:\t', effective_search_td_container_list

            # TODO 按列标号排序 数据对齐
            for ele in range(len(effective_search_td_container_list)):
                # print 'ttt:\t', effective_search_td_container_list[ele]
                soup_ele = BeautifulSoup(str(effective_search_td_container_list[ele][0]), 'html.parser')
                if list(soup_ele.strings):
                    effective_search_td_container_list[ele][0] = list(soup_ele.strings)[0]
            effective_search_td_container_list.sort(key=lambda x: x[0])
            # print '\neffective_search_td_container_list:\t\n', effective_search_td_container_list, len(effective_search_td_container_list)

            # TODO 按列转为按行
            for index in range(len(effective_search_td_container_list[0])):
                temp_list = [ ele[index] for ele in effective_search_td_container_list ]
                effective_cell_data_td_list.insert(index, temp_list)
            # print '\neffective_cell_data_td_list:\t\n', effective_cell_data_td_list, len(effective_cell_data_td_list)

            # TODO 提取单元格数据
            for location in range(len(effective_cell_data_td_list)):
                child_element = effective_cell_data_td_list[location]
                # print 'child_element:\t', child_element
                for ele in range(len(child_element)):
                    # print child_element[ele], ele
                    ele_soup = BeautifulSoup(str(child_element[ele]), 'html.parser')
                    ele_string_list = list(ele_soup.strings)
                    if ele_string_list:
                        child_element[ele] = ele_string_list[0]
                # child_element.pop(-1)
            # print '\neffective_cell_data_td_list:\t\n', effective_cell_data_td_list, len(effective_cell_data_td_list)

            #todo 去除多余的标签元素 由于空白产生的垃圾数据
            effective_header_list = [ header for header in effective_cell_data_td_list[0] if not re.search('width', str(header)) ]
            cell_data_list = effective_cell_data_td_list[1:]
            #todo 循环处理垃圾元素
            for cell in range(len(cell_data_list)):
                cell_data_list[cell] = [ header for header in cell_data_list[cell] if not re.search('style', str(header)) ]
                cell_data_list[cell] = remove_non_alphanumeric_characters(cell_data_list[cell])

            effective_header_list, effective_num_list = self._get_hw_bak_effective_header_list(effective_header_list)
            cell_data_list = self._insert_bak_numers_to_cell_data_list(effective_num_list, cell_data_list)

            # print '\033[31mSilver_Gold_BKC_string222:\t\033[0m', Silver_Gold_BKC_string
            # print '\033[32meffective_header_list:\t\033[0m', effective_header_list, len(effective_header_list)
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            return Silver_Gold_BKC_string, self.date_string, effective_header_list, header_list, cell_data_list

        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', 'Error', [], [], []

    # TODO DE和FPGA DE:24周之后 FPGA: 23周之后 hw格式更改
    def get_lastest_FPGA_hw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            search_td_container_list = []
            effective_header_list = []
            effective_cell_data_td_list = []
            effective_search_td_container_list = []

            for tr in tr_list:
                soup_tr = BeautifulSoup(str(tr), 'html.parser')
                judge_th_exist = soup_tr.find_all('th')
                td_list = soup_tr.find_all('td')

                if not search_td_container_list:
                    for th in judge_th_exist:
                        search_td_container_list.append([th])
                else:
                    if td_list:
                        for index in range(len(search_td_container_list)):
                            search_td_container_list[index].append(td_list[index])
                    else:
                        for index in range(len(search_td_container_list)):
                            search_td_container_list[index].append(judge_th_exist[index])

            # TODO 提取表左列值列表
            for header_ele in search_td_container_list[0]:
                header_soup = BeautifulSoup(str(header_ele), 'html.parser')
                temp = list(header_soup.strings)
                if temp:
                    effective_header_list.append(temp[0])
            header_list = effective_header_list[1:8]

            # TODO 目前四个特性 分离两个table组合成一个table
            for ele_list in search_td_container_list[1:]:
                effective_search_td_container_list.append(ele_list[0:8])
                effective_search_td_container_list.append(ele_list[8:])

            # TODO 按列标号排序 数据对齐
            for ele in range(len(effective_search_td_container_list)):
                soup_ele = BeautifulSoup(str(effective_search_td_container_list[ele][0]), 'html.parser')
                if list(soup_ele.strings):
                    effective_search_td_container_list[ele][0] = list(soup_ele.strings)[0]
            effective_search_td_container_list.sort(key=lambda x: x[0])
            # print '\neffective_search_td_container_list:\t\n', effective_search_td_container_list, len(effective_search_td_container_list)

            # TODO 按列转为按行
            for index in range(len(effective_search_td_container_list[0])):
                temp_list = [ele[index] for ele in effective_search_td_container_list]
                effective_cell_data_td_list.insert(index, temp_list)
            # print '\neffective_cell_data_td_list:\t\n', effective_cell_data_td_list, len(effective_cell_data_td_list)

            # # TODO 提取单元格数据
            for location in range(len(effective_cell_data_td_list)):
                child_element = effective_cell_data_td_list[location]
                for ele in range(len(child_element)):
                    ele_soup = BeautifulSoup(str(child_element[ele]), 'html.parser')
                    ele_string_list = list(ele_soup.strings)
                    if ele_string_list:
                        child_element[ele] = ele_string_list[0]
                    else:
                        child_element.pop(-1)
            temp_header_list, effective_num_list = self._get_hw_effective_header_list(effective_cell_data_td_list[0])
            effective_cell_data_td_list = self._insert_numers_to_cell_data_list(effective_cell_data_td_list)
            effective_cell_data_td_list[0] = temp_header_list

            effective_header_list = effective_cell_data_td_list[0]
            cell_data_list = effective_cell_data_td_list[1:]
            # print '\033[31meffective_header_list:\t\033[0m', effective_header_list, len(effective_header_list)
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[31mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list), len(cell_data_list)
            return Silver_Gold_BKC_string, self.date_string, effective_header_list, header_list, cell_data_list

        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', 'Error', [], [], []

    def get_bak_hw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return 'Error', 'Error', [], [], []
            # 循环处理tr中的代码，提取出excel表头信息，存放在表头列表header_list
            Index_Error_flag = False
            effective_header_list = []
            soup_tr = BeautifulSoup(str(tr_list[0]), 'html.parser')
            th_list = soup_tr.find_all('th')
            td_list = soup_tr.find_all('td')
            effective_th_or_td_list = th_list if th_list else td_list

            try:
                for th in effective_th_or_td_list[1:]:
                    soup_th = BeautifulSoup(str(th), 'html.parser')
                    th_string_list = list(soup_th.strings)
                    # 去掉换行符元素
                    th_string_list = remove_line_break(th_string_list, line_break=True)
                    effective_header_list.append(th_string_list[0])
            except IndexError:
                Index_Error_flag = True
                soup_tr = BeautifulSoup(str(tr_list[1]), 'html.parser')
                th_list = soup_tr.find_all('th')
                td_list = soup_tr.find_all('td')
                effective_th_or_td_list = th_list if th_list else td_list
                for th in effective_th_or_td_list[1:]:
                    soup_th = BeautifulSoup(str(th), 'html.parser')
                    th_string_list = list(soup_th.strings)
                    th_string_list = remove_line_break(th_string_list, line_break=True)
                    effective_header_list.append(th_string_list[0])

            max_length = len(effective_th_or_td_list)

            if Index_Error_flag:
                tr_list_for = tr_list[2:]
            else:
                tr_list_for = tr_list[1:]

            for tr in tr_list_for:
                temp = []
                add_header_flag = False
                # tr中可能是th也可能是td标签,最后两个tr是合并项
                soup_tr = BeautifulSoup(str(tr), 'html.parser')
                # 有可能出现tr出即出现td又出现th的情况
                th_list = soup_tr.find_all('th')
                td_list = soup_tr.find_all('td')
                effective_th_or_td_list = th_list if th_list else td_list
                compare_length = len(effective_th_or_td_list)
                if compare_length < max_length and not (td_list and th_list):
                    add_header_flag = True
                if not add_header_flag:
                    soup_string = BeautifulSoup(str(effective_th_or_td_list[0]), 'html.parser')
                    string_list = list(soup_string.strings)
                    string_list = remove_line_break(string_list, line_break=True)
                    string_list = remove_non_alphanumeric_characters(string_list)
                    header_list.append(string_list[0])

                if not (td_list and th_list):
                    if compare_length < max_length:
                        for_list = effective_th_or_td_list
                    else:
                        for_list = effective_th_or_td_list[1:]
                else:
                    for_list = td_list
                for ele in for_list:
                    cell_soup = BeautifulSoup(str(ele), 'html.parser')
                    cell_string_list = list(cell_soup.strings)
                    # print 'th_string_list_4:\t', cell_string_list
                    cell_string_list = remove_line_break(cell_string_list, line_break=True)
                    cell_string_list = remove_non_alphanumeric_characters(cell_string_list)
                    temp.append(cell_string_list[0])
                cell_data_list.append(temp)

            # print '1:\t', effective_header_list
            # 提取有效的表头列数
            effective_header_list, effective_num_list = self._get_hw_bak_effective_header_list(effective_header_list)
            # print cell_data_list
            # print '2:\t', effective_header_list, effective_num_list
            cell_data_list = self._insert_bak_numers_to_cell_data_list(effective_num_list, cell_data_list)
            # print 'Silver_Gold_BKC_string:\t', Silver_Gold_BKC_string

            # print '\033[31mSilver_Gold_BKC_string111:\t\033[0m', Silver_Gold_BKC_string
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[32meffective_header_list:\t\033[0m', effective_header_list, len(effective_header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)

            return Silver_Gold_BKC_string, self.date_string, effective_header_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', 'Error', [], [], []

    def judge_silver_bkc_func(self, data_type, bkc_flag):
        Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self._common_regex(data_type, bkc_flag)
        return  Silver_Gold_BKC_string, tr_list, header_list, cell_data_list

    def get_sw_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)
            if not tr_list:
                return Silver_Gold_BKC_string, 0, self.date_string, [], [], []
            soup_header = BeautifulSoup(str(tr_list[0]), 'html.parser')
            header_list = list(soup_header.strings)
            header_list = remove_line_break(header_list, line_break=True)
            for i in range(len(header_list)):
                header_list[i] = header_list[i].replace('\n', '')
            #排除部分周会有更多的列
            header_length = len(header_list)
            # todo remove special characters \xc2\xa0
            header_list = [ ele for ele in header_list if u'\xc2\xa0' not in ele ]
            header_list = header_list[:4]
            url_list = []

            for t in tr_list[1:]:
                temp_url_list = []; temp_string_list = []
                soup_tr = BeautifulSoup(str(t), 'html.parser')
                td_list = soup_tr.find_all('td')
                #默认情况是正常列数
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
                        if '2017%20WW28' in self.data_url and self.purl_bak_string in self.data_url:
                            temp_string_list = temp_string_list[header_length - 4 - 2:]
                        else:
                            temp_string_list = temp_string_list[header_length - 4:]
                #获取cell_data_list数据
                temp_string_list = remove_non_alphanumeric_characters(temp_string_list)

                if (len(temp_string_list) >= header_length + 1):
                    temp_string_list = [ele for ele in temp_string_list if len(ele) != 0]

                elif (len(temp_string_list) >= header_length + 2) and len(temp_string_list[-1]) == 0:
                    temp_string_list = temp_string_list[:-1]

                # todo 括号分离合并处理
                temp_string_list = extract_sw_data_deal_bracket(temp_string_list)
                if temp_string_list:
                    if u'APPs' == temp_string_list[0]:
                        temp_string_list = temp_string_list[1:]
                    if len(temp_string_list) < 4:
                        for nu in range(4 - len(temp_string_list)):
                            temp_string_list.append('')
                    cell_data_list.append(temp_string_list)
                # print 'temp_string_list:\t', temp_string_list, len(temp_string_list)
                for td in actual_td_list:
                    #正则取匹配url链接
                    obj_list = re.findall('<a href="(.*?)">', str(td), re.M|re.S)
                    if obj_list:
                        #逐个添加
                        for url in obj_list:
                            url = url.split()[0].replace("\"", "")
                            temp_url_list.append(url)

                if temp_url_list:
                    url_list.append(temp_url_list)
            for k in range(len(cell_data_list)):
                if header_length > 4 and len(cell_data_list[k]) > 4:
                    if cell_data_list[k][1] == u'VMWare':
                        cell_data_list[k] = cell_data_list[k][ 1: ]
                    else:
                        cell_data_list[k] = cell_data_list[k][:4 - header_length]

            header_length = len(header_list)
            if header_length < 4:
                header_length = 4
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            # print '\033[31murl_list:\t\033[0m', url_list, len(url_list)
            # print '\033[31Silver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, header_length, self.date_string, url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', 0, self.date_string, [], [], []

    def get_sw_data_1(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)
            if not tr_list:
                return Silver_Gold_BKC_string, 0, self.date_string, [], [], []
            url_list = []
            soup_header = BeautifulSoup(str(tr_list[0]), 'html.parser')
            header_td_list = soup_header.find_all('td')
            for header_td in header_td_list[1:]:
                header_td_soup = BeautifulSoup(str(header_td), 'html.parser')
                td_string_list = list(header_td_soup.strings)
                header_list.extend(td_string_list)
            header_list = list(remove_line_break(object_string_list=header_list, first_method=False, second_method=True, line_break=True))
            header_list = header_list[:4]
            header_list = remove_non_alphanumeric_characters(header_list)
            header_length = len(header_list)

            for tr_ele in tr_list[1:]:
                tr_string_soup = BeautifulSoup(str(tr_ele), 'html.parser')
                tr_string_list = list(tr_string_soup.strings)
                tr_string_list = remove_non_alphanumeric_characters(tr_string_list)
                tr_string_list = list(remove_line_break(object_string_list=tr_string_list, empty_string=True, second_method=True, first_method=False))
                tr_string_list = tr_string_list[-6:-2]
                cell_data_list.append(tr_string_list)

                obj_list = re.findall('<a href="(.*?)">', str(tr_ele), re.M | re.S)
                if obj_list:
                    url_list.append(list(obj_list))
            # print '\033[31mheader_list:\t\033[0m', header_list, len(header_list)
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list, len(cell_data_list)
            # print '\033[31murl_list:\t\033[0m', url_list, len(url_list)
            return Silver_Gold_BKC_string, header_length, self.date_string, url_list, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', 0, self.date_string, [], [], []

    def get_ifwi_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], []
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
            # print '\033[31mheader_list:\t\033[0m', header_list
            # print '\033[36mcell_data_list:\t\033[0m', cell_data_list
            # print '\033[31Silver_Gold_BKC_string:\t\033[0m', Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, self.date_string, header_list, cell_data_list
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', self.date_string, [], []

    def get_platform_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)
            self.save_caseresult_url(bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            effective_url_list = []
            for tr in tr_list:
                temp = []; url_list = []
                soup = BeautifulSoup(str(tr), 'html.parser')
                th_list = soup.find_all('th'); td_list = soup.find_all('td')
                #获取header_list
                if th_list:
                    th_strings = soup.strings
                    for th in th_strings:
                        str_th = th.replace('\n', '')
                        if len(str_th) == 0:
                            continue
                        header_list.append(th)
                if td_list:
                    # 获取url链接
                    temp_url_list = soup.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
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
                    #需要循环处理，防止丢失无内容的项
                    for td in td_list:
                        td_soup = BeautifulSoup(str(td), 'html.parser')
                        temp_list = list(td_soup.td.strings)
                        temp_list = remove_line_break(temp_list, line_break=True, blank_string=True)
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
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, [], self.date_string
            object_string_list = []
            for tr in tr_list:
                soup = BeautifulSoup(str(tr), 'html.parser')
                h4_list = soup.find_all('h4')
                for h4 in h4_list:
                    h4_string = BeautifulSoup(str(h4), 'html.parser')
                    temp_string = list(h4_string.strings)
                    temp_string = remove_line_break(temp_string, line_break=True, blank_string=True)
                    if h4 != h4_list[-1]:
                        if len(temp_string) == 1 and temp_string[0] == u'\xc2\xa0':
                            continue
                        object_string_list.append(' '.join(temp_string).strip(u'\xb7'))
                    else:
                        for i in range(len(temp_string)):
                            if temp_string[i] == u'l' or temp_string[i] == u'\xa0' or temp_string[i] == u'\xb7' or temp_string[i] == u'\xc2\xa0':
                                continue
                            object_string_list.append(temp_string[i])
                    if len(object_string_list) == 2:
                        object_string_list.append('')

                if len(object_string_list) < 10:
                    # 得到tr节点下的所有文本
                    text = list(soup.td.children)
                    object_string_list = []
                    for child in text:
                        soup_son = BeautifulSoup(str(child), 'html.parser')
                        child_tag_string_list = list(soup_son.strings)
                        if child_tag_string_list[0] == u'\n' or child_tag_string_list[0] == u'\xc2\xa0':
                            continue
                        temp_string = ''.join(child_tag_string_list).strip(' ')
                        if len(object_string_list) == 2:
                            object_string_list.append('')
                        object_string_list.append(temp_string)
            # 对提取的字符串列表进行清洗，统一组合格式：空格分隔  Mon Apr 10 14:00:27 2017
            object_string_list = remove_non_alphanumeric_characters(object_string_list)
            object_string_list[0] = re.sub('[()]', '', object_string_list[0]).strip()
            object_string_list = remove_line_break(object_string_list, empty_string=True)
            # print object_string_list, len(object_string_list); print Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, object_string_list, self.date_string
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name, definition_log_level=ERROR)
            return 'Error', [], self.date_string

    def get_bak_rework_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, [], self.date_string
            temp_list = []
            object_string_list = []
            for tr in tr_list:
                tr_soup = BeautifulSoup(str(tr), 'html.parser')
                tr_tag = tr_soup.contents[0]
                child_tag_list = list(tr_tag.children)
                for child in range(len(child_tag_list)):
                    child_soup = BeautifulSoup(str(child_tag_list[child]), 'html.parser')
                    string_list = list(child_soup.strings)
                    string_list = remove_non_alphanumeric_characters(string_list)
                    string_list = remove_line_break(string_list, empty_string=True)
                    if child == 1:
                        temp_list.extend(string_list)
            # print temp_list, len(temp_list)
            try:
                object_string_list = [temp_list[0]+':', temp_list[1], ' '.join(temp_list[2:5]), temp_list[5]+':', ' '.join(temp_list[6:9]),
                                      temp_list[9], temp_list[10], ' '.join(temp_list[11:13]), '', temp_list[13]+':', [temp_list[14], temp_list[15]],
                                      [temp_list[16], temp_list[17]], [temp_list[18], temp_list[19]], [temp_list[20], temp_list[21]]]
            except:
                object_string_list.extend(temp_list)

            # print object_string_list, len(object_string_list); print Silver_Gold_BKC_string
            return Silver_Gold_BKC_string, object_string_list, self.date_string
        except:
            self.logger.print_message(msg='Get [ %s ] Original Data Error' % self.data_url, logger_name=self.__file_name,
                                      definition_log_level=ERROR)
            return 'Error', [], self.date_string

    def get_existing_sighting_data(self, data_type, bkc_flag=True):
        try:
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], [], []
            #获取链接地址
            cell_last_data = [] ;effective_url_list = []
            for tr in tr_list:
                soup = BeautifulSoup(str(tr), 'html.parser')
                if tr == tr_list[0]:
                    header_list = list(soup.strings)[1::2]
                    continue

                temp = [] ;cell_last_string_list = [] ;url_list = []
                td_list = soup.find_all('td')
                for td in td_list:
                    soup_td = BeautifulSoup(str(td), 'html.parser')
                    # 获取url链接
                    temp_url_list = soup_td.find_all('a')
                    if temp_url_list:
                        for ele in temp_url_list:
                            soup_href = BeautifulSoup(str(ele), 'html.parser')
                            string_list = list(soup_href.a.strings)

                            if string_list:
                                cell_last_string_list.append(string_list[0])
                            #BKC第13周比较特殊，有个双层链接
                            try:
                                special_data = soup_href.findAll(name='a', attrs={'1358': re.compile(r'(.*)')})
                                if special_data:
                                    url_list.append('[BKC][FPGA][s927')
                            except KeyError:
                                pass

                            string_url = soup_href.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                            if string_url:
                                #排除无效的url
                                if re.search('.*id="></a>$', str(string_url[0])):
                                    continue
                                #提取有效的url链接
                                for url in string_url:
                                    url_soup = BeautifulSoup(str(url), 'html.parser')
                                    url = url_soup.a['href']
                                    url_list.append(url)

                    if soup_td.strings:
                        td_son_list = list(soup_td.strings)
                        td_son_list = remove_line_break(td_son_list, line_break=True, blank_string=True)
                        ( temp.append(td_son_list[0]) if len(td_son_list) == 1 else temp.append(td_son_list[-1]) ) \
                            if len(td_son_list) != 0 else temp.append('')

                cell_last_data.append(cell_last_string_list)
                #去除多余的换行符和空格，防止插入excel表格时报 255 characters since it exceeds Excel's limit for URLS 长度超过限定长度
                for k in range(len(url_list)):
                    url_list[k] = re.sub('[\s]', '', url_list[k])
                effective_url_list.append(url_list)
                #移除非字母数字字符
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
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            effective_url_list = []
            for tr in tr_list:
                url_list = []; temp = []
                soup = BeautifulSoup(str(tr), 'html.parser')
                th_list = soup.find_all('th'); td_list = soup.find_all('td')
                if th_list:
                    if soup.tr:
                        header_list = remove_line_break(list(soup.tr.strings), line_break=True)
                if td_list:
                    # 获取url链接
                    temp_url_list = soup.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                    if temp_url_list:
                        # 提取有效的url链接
                        for url in temp_url_list:
                            url_soup = BeautifulSoup(str(url), 'html.parser')
                            url = url_soup.a['href']
                            # 排除无效的url 无效的url id后不跟数字
                            if not re.search('(\d+)$', str(url)):
                                continue
                            url_list.append(url)
                        effective_url_list.append(url_list)
                    #需要循环处理，防止丢失无内容的项
                    for td in td_list:
                        td_soup = BeautifulSoup(str(td), 'html.parser')
                        if td_soup.td:
                            temp_list = remove_line_break(list(td_soup.td.strings), line_break=True, blank_string=True)
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
            Silver_Gold_BKC_string, tr_list, header_list, cell_data_list = self.judge_silver_bkc_func(data_type, bkc_flag)

            if not tr_list:
                return Silver_Gold_BKC_string, self.date_string, [], [], []

            effective_url_list = []
            for tr in tr_list:
                url_list = [] ;temp = []
                soup = BeautifulSoup(str(tr), 'html.parser')
                th_list = soup.find_all('th') ;td_list = soup.find_all('td')
                if th_list and soup.tr:
                        header_list = remove_line_break(list(soup.tr.strings), line_break=True)
                if td_list:
                    # 获取url链接
                    temp_url_list = soup.findAll(name='a', attrs={'href': re.compile(r'[https|http]:(.*?)')})
                    if temp_url_list:
                        for ele in temp_url_list:
                            soup_href = BeautifulSoup(str(ele), 'html.parser')
                            string_url = soup_href.a['href']
                            url_list.append(string_url)
                        effective_url_list.append(url_list)
                    #需要循环处理，防止丢失无内容的项
                    for td in td_list:
                        td_soup = BeautifulSoup(str(td), 'html.parser')
                        if td_soup and td_soup.td:
                            temp_list = remove_line_break(list(td_soup.td.strings), line_break=True, blank_string=True)
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
            parent_caseresult_url = self.data_url
            Silver_Gold_BKC_string = 'Silver'
            tip_string = 'default_tip_string'

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
            regex = re.compile(r'Detail case result could be found in this\s+<a href="(.*?)</div>', re.S | re.M)
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

            # self.logger.print_message(msg='page_url:\t%s' % page_url, logger_name=self.__file_name)
            html = self.cache[page_url]
            soup = BeautifulSoup(str(html), 'html.parser')
            #获取数据部分头部的标记字符串  Purley-FPGA WW12
            table_tip_list = soup.find_all('table')
            if table_tip_list:
                table_tip = table_tip_list[0]
                tip_soup = BeautifulSoup(str(table_tip), 'html.parser')
                if tip_soup:
                    tip_string_list = remove_line_break(list(tip_soup.strings), line_break=True)
                    if tip_string_list:
                        tip_string = tip_string_list[0].strip(' ')
                        temp = tip_string.split(' ')
                        if temp:
                            tip_string = temp[0] + ' ' + temp[-1]
            #获取有效的待插入数据
            table_list = soup.find_all('table')
            if len(table_list) >= 2:
                table = table_list[1]
                soup_tr = BeautifulSoup(str(table), 'html.parser')
                tr_list = soup_tr.find_all('tr')
                header_list = [] ;cell_data_list = []

                if not tr_list:
                    return self.date_string, '', '', [], []

                #获取表列名
                for tr in tr_list:
                    temp = []
                    soup = BeautifulSoup(str(tr), 'html.parser')
                    th_list = soup.find_all('th') ;td_list = soup.find_all('td')
                    if th_list and soup.tr:
                            header_list = remove_line_break(list(soup.tr.strings), line_break=True)
                    #获取表单元格数据
                    if td_list:
                        #需要循环处理，防止丢失无内容的项
                        for td in td_list:
                            td_soup = BeautifulSoup(str(td), 'html.parser')
                            if td_soup and td_soup.td:
                                temp_list = remove_line_break(list(td_soup.td.strings), line_break=True, blank_string=True)
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
    # f = open(os.getcwd() + os.sep + 'report_html' + os.sep + 'Bakerville_url_info.txt')
    # for line in f:
    #     if 'Bakerville' in line and 'Silver' in line:
    #         key_url_list.append(line.strip('\n'))

    cache = DiskCache('Bakerville')
    # key_url_list = ['https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW24/6170_Silver.html',
    #                 'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW34/6565_Silver.html',
    #                 'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW38/6706_Silver.html',
    #                 'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW37/6668_Silver.html']
    #                 # 'https://dcg-oss.intel.com/ossreport/auto/Bakerville/BKC/2017%20WW25/6211_BKC.html']
    key_url_list = ['https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW34/6565_Silver.html',
                    'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW38/6706_Silver.html',
                    'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW24/6170_Silver.html',
                    'https://dcg-oss.intel.com/ossreport/auto/Bakerville/Silver/2017%20WW37/6668_Silver.html']
    for url in key_url_list:
        obj = GetAnalysisData(url, 'Bakerville', get_info_not_save_flag=True, insert_flag=True, cache=cache)
        # obj.get_caseresult_data('Platform Integration Validation Result', True)
        # obj.get_sw_data('SW Configuration', True)
        # obj.get_platform_data('Platform Integration Validation Result', True)
        # obj.get_bak_hw_data('HW Configuration', True)
        obj.get_lastest_bak_hw_data('HW Configuration', True)
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