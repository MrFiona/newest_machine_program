#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-03-21 09:40
# Author  : MrFiona
# File    : get_all_html.py
# Software: PyCharm Community Edition

from __future__ import absolute_import

import codecs
import os
import re
import shutil
import ssl
import time
import urllib2
from functools import wraps

import chardet
from bs4 import BeautifulSoup

from machine_scripts.cache_mechanism import DiskCache
from machine_scripts.extract_data import GetAnalysisData
from machine_scripts.public_use_function import get_url_list_by_keyword
from setting_global_variable import SRC_WEEK_DIR, REPORT_HTML_DIR, SRC_CACHE_DIR


# 强制ssl使用TLSv2
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv2
        return func(*args, **kw)

    return bar

context = ssl._create_unverified_context()
ssl.wrap_socket = sslwrap(ssl.wrap_socket)


class GetUrlFromHtml(object):
    def __init__(self, html_url_pre=None, file_path = REPORT_HTML_DIR, logger=None):
        if not html_url_pre:
            raise UserWarning('Please send the url parameter!!!')
        if (html_url_pre and isinstance(html_url_pre, str) and html_url_pre.isspace()):
            raise UserWarning('All parameters cannot be an empty string!!!')
        if not isinstance(html_url_pre, str):
            raise UserWarning('All parameters must be a string!!!')

        self.html_url_pre = html_url_pre
        self.file_path = file_path
        self.logger = logger
        self.logger_file_name = os.path.split(__file__)[1]
        self.department_list = []
        self.stage_type_list = []
        self.date_list = []
        self.all_date_list = []
        self.url_info_list = []

    # TODO 递归创建目录函数  私有函数
    def _recursive_create_dir(self, purl_bak_string, create_html_name, dir_path=None):
        if not dir_path:
            raise UserWarning('The directory path to be created is None!!!')
        #检测目录是否存在
        if not os.path.exists(dir_path):
            if purl_bak_string in dir_path or create_html_name == 'auto':
                os.makedirs(dir_path)

    # TODO 将指定目录中的文件写入数据  私有函数
    def _write_info(self, file_path, write_message):
        try:
            if not file_path:
                raise UserWarning('The directory path to be created is None!!!')
            #当输入的是目录而不是文件路径时则报错
            if os.path.isdir(file_path) and not os.path.isfile(file_path):
                raise UserWarning("The function's file argument is a file instead of a directory!!!")
            with codecs.open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(write_message.decode( chardet.detect(write_message)['encoding']))
        #当上一级以及以上目录不存在时则会报错
        except IOError:
            pass

    # TODO 提取Html中指定的tag信息列表
    def _get_html_tag(self, html, tag_name):
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup.find_all(re.compile(tag_name))
        # 去除Parent Directory这个无效选项
        tag.pop(0)
        # 按时间倒序输出
        tag.sort(reverse=True)
        return tag

    # TODO 将当前html写入对应路径的文件，返回含有li吧标签的信息列表
    def _common_get_info(self, url, create_html_name, purl_bak_string):
        try:
            # 写入html,需考虑多级路径的情况下处理，将路径分隔符替换为下划线,在连接日期的时候会出现%也要替换为下划线
            create_html_name = re.sub('[%_]', '_', create_html_name)
            response_html = urllib2.urlopen(url, timeout=6, context=context).read()
            # 递归创建存储信息的目录
            if create_html_name == 'auto':
                file_path = self.file_path
            else:
                file_path = self.file_path + os.sep + create_html_name
            self._recursive_create_dir(purl_bak_string, create_html_name, file_path)
            self._write_info(file_path + os.sep +  '_'.join(create_html_name.split(os.sep)) + '.html', response_html)
            # 提取html信息
            li_list = self._get_html_tag(response_html, 'li')
        except urllib2.HTTPError as e:
            print e
            print 'Access error, please check whether address [ %s ] is valid!!!' % url
            return
        except urllib2.URLError as e:
            print e
            print 'timeout'
            return
        return li_list

    # TODO 获取主页面html中的部门信息列表
    def get_department_html_info(self, purl_bak_string, get_only_department=True):
        li_list = self._common_get_info(self.html_url_pre, 'auto', purl_bak_string)
        if not li_list:
            return []
        department_info_list = []
        if not get_only_department:
            for li in li_list:
                if 'Purley-FPGA/' in li.encode('utf-8'):
                    department_info_list.append('Purley-FPGA')
                if 'Bakerville/' in li.encode('utf-8'):
                    department_info_list.append('Bakerville')
                if 'NFVi/' in li.encode('utf-8'):
                    department_info_list.append('NFVi')
            department_info_list.sort(reverse=True)

        else:
            for li in li_list:
                if purl_bak_string in li.encode('utf-8'):
                    department_info_list.append(purl_bak_string)

        return department_info_list

    # TODO 获取部门html中的阶段信息列表
    def get_stage_type_html_info(self, department_name, purl_bak_string):
        li_list = self._common_get_info(self.html_url_pre + department_name, department_name, purl_bak_string)
        if not li_list:
            return []
        stage_info_list = []
        for li in li_list:
            if 'Silver/' in li.encode('utf-8'):
                stage_info_list.append('Silver')
            if 'Gold/' in li.encode('utf-8'):
                stage_info_list.append('Gold')
            if 'BKC/' in li.encode('utf-8'):
                stage_info_list.append('BKC')
            stage_info_list.sort(reverse=True)
        return stage_info_list

    # TODO 获取阶段html中的日期信息列表
    def get_date_html_info(self, department_name, stage_type_name, purl_bak_string):
        li_list = self._common_get_info(self.html_url_pre + department_name + '/' + stage_type_name, department_name + os.sep + stage_type_name, purl_bak_string)
        if not li_list:
            return []
        # 循环提取后续url前缀和文件名前缀
        url_pre_list = []
        file_pre_list = []
        li_list = list(li_list)
        for pre in li_list:
            href = re.search('<li><a\s+href=(?P<name>.*)>(?P<year>.*)</a></li>', str(pre))
            url_pre_list.append(href.groupdict()['name'].replace("\"""", ""))
            file_pre_list.append(href.groupdict()['year'])
        url_pre_list.sort(reverse=True)
        return url_pre_list

    # TODO 获取日期Html中的数据url地址
    def get_result_data_url(self, department_name, stage_type_name, date_name, purl_bak_string):
        li_list = self._common_get_info(self.html_url_pre + department_name + '/' + stage_type_name + '/' + date_name, department_name + os.sep + stage_type_name + os.sep + date_name, purl_bak_string)
        if not li_list:
            return None
        file_name = None
        for li in li_list:
            file = re.findall('<li><.*>\s(.*?)</a></li>', li.encode('utf-8'))
            if file[0].endswith('.html'):
                file_name = file[0]
        return file_name

    # TODO 更新相应周缓存
    def write_html_by_multi_thread(self, purl_bak_string, keep_continuous):
        cache = DiskCache(purl_bak_string)
        effective_url_list = []
        # TODO 此时已经删除缓存不置标记为False
        effective_week_string_list = []
        if keep_continuous == 'YES':
            # TODO 只获取相应周信息列表
            effective_week_string_list = self.get_week_info_by_flag(purl_bak_string, delete_cache_flag=False)
        for type in ['Silver', 'Gold', 'BKC']:
            # TODO 获取对应周url列表
            effective_url_list.extend(get_url_list_by_keyword(purl_bak_string, type, pre_url_list=effective_week_string_list))
        for url in effective_url_list:
            # TODO 更新对应周缓存
            GetAnalysisData(data_url=url, purl_bak_string=purl_bak_string, get_info_not_save_flag=True, cache=cache, insert_flag=False)

    # TODO  将url写进文件
    def save_url_info(self):
        with open(self.file_path + os.sep + 'url_info.txt', 'w') as f:
            f.write('\n'.join(self.url_info_list))

    # TODO 获取所有的类型的数据
    def get_all_type_data(self, purl_bak_string, get_only_department=True):
        #获取部门列表
        self.department_list = self.get_department_html_info(purl_bak_string, get_only_department=get_only_department)
        if not self.department_list:
            return
        for department in self.department_list:
            #获取部门中的测试类型列表
            self.stage_type_list = self.get_stage_type_html_info(department, purl_bak_string)
            if not self.stage_type_list:
                self.logger.print_message('Reacquire the url corresponding to the file', self.logger_file_name)
                start_time = time.time()
                while 1:
                    self.stage_type_list = self.get_stage_type_html_info(department, purl_bak_string)
                    if self.stage_type_list:
                        self.logger.print_message('The final url corresponding to the department:\t%s' % self.stage_type_list, self.logger_file_name)
                        self.logger.print_message('The total reacquire department time:\t%s' % (time.time() - start_time), self.logger_file_name)
                        break
            for stage in self.stage_type_list:
                self.date_list = self.get_date_html_info(department, stage, purl_bak_string)
                if not self.date_list:
                    self.logger.print_message('Reacquire the url corresponding to the file', self.logger_file_name)
                    start_time = time.time()
                    while 1:
                        self.date_list = self.get_date_html_info(department, stage, purl_bak_string)
                        if self.date_list:
                            self.logger.print_message('The final url corresponding to the stage:\t%s' % self.date_list, self.logger_file_name)
                            self.logger.print_message('The total reacquire stage time:\t%s' % (time.time() - start_time), self.logger_file_name)
                            break
                for date in self.date_list:
                    file_name = self.get_result_data_url(department, stage, date.replace('/', ''), purl_bak_string)
                    if not file_name:
                        self.logger.print_message('Reacquire the url corresponding to the file', self.logger_file_name)
                        start_time = time.time()
                        while 1:
                            file_name = self.get_result_data_url(department, stage, date.replace('/', ''), purl_bak_string)
                            if file_name:
                                self.logger.print_message('The final url corresponding to the file:\t%s' % file_name, self.logger_file_name)
                                self.logger.print_message('The total reacquire file time:\t%s' % (time.time() - start_time), self.logger_file_name)
                                break
                    html_suffix = '/'.join([str(department), str(stage), str(date.replace('/', '')), str(file_name)])
                    #将url添加到url列表
                    self.url_info_list.append(self.html_url_pre + html_suffix)
                    if purl_bak_string in self.html_url_pre + html_suffix:
                        self.logger.print_message(self.html_url_pre + html_suffix, self.logger_file_name)
        #将url列表信息写进文件
        self.save_url_info()

    # TODO 获取部门, 测试类型, 日期列表
    def get_department_stage_date_list(self):
        return self.department_list, self.stage_type_list, self.date_list

    # TODO 根据周日期标记来获取周数据 delete_cache_flag 防止重复删缓存标记
    def get_week_info_by_flag(self, purl_bak_string, delete_cache_flag=False):
        with open(SRC_WEEK_DIR + os.sep + 'week_info.txt', 'r') as f:
            week_string = f.readline()

        week_string_list = week_string.strip().split(',')

        # TODO 未配置日期值
        if not week_string_list:
            return []

        week_string_list = [week.split('WW')[0] + '_20WW' + week.split('WW')[1] for week in week_string_list]
        # print 'week_string_list:\t', week_string_list
        if delete_cache_flag:
            search_num = 0
            for dirpath, dirnames, filenames in os.walk(SRC_CACHE_DIR):
                object_dirname = os.path.join(dirpath)
                if object_dirname.endswith(purl_bak_string):
                    search_num += 1
                    if search_num == 2:
                        # TODO 删除指定周目录
                        for pre_dir in ['BKC', 'Gold', 'Silver']:
                            for file in week_string_list:
                                try:
                                    shutil.rmtree(object_dirname + os.sep + pre_dir + os.sep + file)
                                    self.logger.print_message('Delete [ %s ] file successfully' % (
                                    object_dirname + os.sep + pre_dir + os.sep + file), os.path.split(__file__)[1])
                                except WindowsError:
                                    pass

        # TODO 重新获取数据
        effective_week_string_list = [ re.sub('_', '%', week) + '/' for week in week_string_list ]
        # print 'effective_week_string_list:\t', effective_week_string_list
        return effective_week_string_list

    # TODO 当配置周日期标记开启时删除相应周的缓存并且重新更新缓存
    def update_week_cache(self, purl_bak_string):
        # TODO 删除对应周缓存
        self.get_week_info_by_flag(purl_bak_string, delete_cache_flag=True)
        self.get_all_type_data(purl_bak_string)
        # TODO 更新缓存
        object.write_html_by_multi_thread(purl_bak_string, 'NO')



if __name__ == '__main__':
    start = time.time()
    # TODO 类型: Bakerville or Purley-FPGA
    from machine_scripts.custom_log import WorkLogger
    _logger = WorkLogger('get_all_html_log', create_log_flag=False)

    # purl_bak_string = get_interface_config('default_purl_bak_string', 'PURL_BAK_STRING')
    purl_bak_string = 'Purley-FPGA'
    object = GetUrlFromHtml(html_url_pre='https://dcg-oss.intel.com/ossreport/auto/', logger=_logger)
    # object.get_all_type_data(purl_bak_string, get_only_department=True, remove_week_cache_flag=True, remove_week_list=None)
    #多线程写文件
    object.update_week_cache(purl_bak_string)
    # object.write_html_by_multi_thread(purl_bak_string)
    # object.get_department_stage_date_list()
    print '用时: [ %d ]' %(time.time() - start)
    # hw = object.get_hw_configuration_info('BasinFalls', 'Gold111', '')
    # object.get_department_html_info()
    # object.get_stage_type_html_info('Purley-FPGA')
    # object.get_date_html_info('Purley-FPGA', 'Silver')
    # object.get_result_data_url('Purley-FPGA', 'Silver', '2017%20WW03'