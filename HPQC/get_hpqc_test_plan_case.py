#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-06 15:13
# Author  : MrFiona
# File    : get_hpqc_test_plan_case.py
# Software: PyCharm Community Edition


import os
import json
try:
    import cPickle as pickle
except:
    import pickle
import time
from threading import Thread
from HPQC.test_case_cache import Test_Case_Cache
from HPQC._hpqc_parser_tool import HPQC_info_parser_tool
from setting_global_variable import HPQC_PARENT_PATH, HPQC_CACHE_DIR



class GetHPQCTestPlanCase:
    def __init__(self, logger, session, query, program_name):
        """
        :param session:
        :param query:
        :param program_name:
        """
        self.logger = logger
        self.session = session
        self.query = query
        self.program_name = program_name
        self.project_path = 'Subject/' + program_name
        self.__file_name = os.path.split(__file__)[1]

        #todo 抓取program_name项目test_plan中的test_case信息 存放在在HPQC_test_plan目录下
        self.test_plan_dir = HPQC_PARENT_PATH + os.sep + 'HPQC_test_plan' + os.sep + program_name
        if not os.path.exists(self.test_plan_dir):
            os.makedirs(self.test_plan_dir)

        #todo 提供存放test_case相关信息的文件对象
        self.f_case = open(self.test_plan_dir + os.sep + 'test_case_info.txt', 'w')
        self.f_case_combine = open(self.test_plan_dir + os.sep + 'test_case_combine_info.txt', 'w')

        #todo 抓取test_case信息
        self.get_plan_case_info()
        self.return_close()
        self.establish_test_plan_case_cache_dir()

    def return_close(self):
        self.f_case.close()
        self.f_case_combine.close()

    def recursive_program_test_plan_case(self, dir_case_plan_string, session):
        print dir_case_plan_string
        session.extend_session()
        folders = dir_case_plan_string.split(r'/')
        parent_id = 0
        #todo 过滤历史目录
        if 'OutofDate' in dir_case_plan_string or 'Outofdate' in dir_case_plan_string:
            return
        self.logger.print_message('ret_folders:\t%s' % dir_case_plan_string, self.__file_name)
        for folder in folders:
            if folder:
                ret_folders = self.query.enumerate_folder_private(parent_id, session, flag=1)
                if ret_folders == None:
                    ret_folders = []
                    self.logger.print_message('ret_folders:\t%s' % dir_case_plan_string, self.__file_name)
                folder_compare = [ele for ele in ret_folders if ele[1] == folder]
                if folder_compare:
                    parent_id = folder_compare[0][0]
        ret_folders = self.query.enumerate_folder_private(parent_id, session, flag=1)

        #todo 返回信息并将数据保存到json文件  参数：save_data=True, program_name=self.program_name
        testsets = self.query.enumerate_test_set_private(parent_id, session, flag=1, save_data=True, program_name=self.program_name)
        if testsets:
            self.logger.print_message('original_preview_string path:\t%s\ttestsets:\t%s' %(dir_case_plan_string, testsets), self.__file_name)
            test_case_num_list, test_case_name_list = zip(*testsets)
            self.logger.print_message('test_case_num_list:\t%s' % (test_case_num_list,), self.__file_name)
            self.logger.print_message('test_case_name_list:\t%s' % (test_case_name_list,), self.__file_name)
            self.f_case.write('\n' + dir_case_plan_string + '\n')
            self.f_case.write(' ' * 10 + '1 => ' + str(test_case_num_list[0]) + '\t' + test_case_name_list[0] + '\n')
            for line_num in xrange(1, len(test_case_num_list)):
                self.f_case.write(' ' * 10 + '%d => ' % (line_num + 1) + str(test_case_num_list[line_num]) + '\t' +
                             test_case_name_list[line_num] + '\n')
            time.sleep(0.01)
            for line in xrange(len(test_case_num_list)):
                self.f_case_combine.write(
                    dir_case_plan_string + '/' + str(test_case_num_list[line]) + '/' + test_case_name_list[line] + '\n')
            time.sleep(0.01)

        if not ret_folders:
            return

        thread_list = []
        for folder in ret_folders:
            t = Thread(target=self.recursive_program_test_plan_case, args=(dir_case_plan_string + '/' + folder[1], session))
            thread_list.append(t)

        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()

    # TODO 获取test plan里test-case详细信息
    def get_plan_case_info(self):
        try:
            self.recursive_program_test_plan_case(self.project_path, self.session)
        except Exception, e:
            self.logger.print_message('get_program_test_plan_case error: %s' % e, self.__file_name)

    # todo 从get_plan_case_info接口获取到的test-case信信息，建立其缓存目录
    def establish_test_plan_case_cache_dir(self):
        cache = Test_Case_Cache()
        test_case_id_list = []
        test_case_name_list = []
        test_case_name_path_list = []
        with open(self.test_plan_dir + os.sep + 'test_case_combine_info.txt', 'r') as p:
            for line in p:
                test_case_string_list = line.strip().split('/')
                # print 'test_case_string_list:\t', test_case_string_list
                test_case_id = int(test_case_string_list[-2])
                test_case_name = str(test_case_string_list[-1])
                test_case_id_list.append(test_case_id)
                test_case_name_list.append(test_case_name)
                pre_case_string_list = test_case_string_list[:-2]
                pre_case_string_list.append(test_case_string_list[-1])
                test_case_name_path_list.append('/'.join(pre_case_string_list))

        self.logger.print_message('test_case_id_list:\t%s%d' %(test_case_id_list, len(test_case_id_list)), self.__file_name)
        self.logger.print_message('test_case_name_list:\t%s%d' %(test_case_name_list, len(test_case_name_list)), self.__file_name)
        self.logger.print_message('test_case_name_path_list:\t%s%d' %(test_case_name_path_list, len(test_case_name_path_list)), self.__file_name)
        test_case_name_id_dict = dict(zip(test_case_name_list, test_case_id_list))

        #todo 保存test_case name,id组合字典对象
        with open(self.test_plan_dir + os.sep + 'test_case_name_id_dict.dump', 'wb') as f:
            f.write(pickle.dumps(test_case_name_id_dict))
            print 'pickle successfully!!!'
            self.logger.print_message('pickle successfully!!!', self.__file_name)

        thread_list = []
        for nu in range(len(test_case_id_list)):
            t = Thread(target=self.query.enumerate_plan_private,
                       args=(self.session, cache, test_case_id_list[nu], test_case_name_path_list[nu]))
            thread_list.append(t)

        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()

    #todo 在从test_plan中获取test-case时将test-case信息记录在excel中
    def preserve_test_case_info(self):
        all_test_plan_case_info = {}
        for path, dirs, files in os.walk(HPQC_CACHE_DIR + os.sep + self.project_path):
            for name in files:
                print os.path.join(path, name)
                with open(os.path.join(path, name), 'rb') as fp:
                    json_data = json.load(fp)
                case_key_info = HPQC_info_parser_tool(json_data)
                all_test_plan_case_info[case_key_info[u'_test_name']] = case_key_info
        self.logger.print_message('all_test_plan_case_info:\t%s' % all_test_plan_case_info, self.__file_name)
        #todo 保存test_case name,id组合字典对象
        with open(self.test_plan_dir + os.sep + 'test_plan_case_detail_info.dump', 'wb') as f:
            f.write(pickle.dumps(all_test_plan_case_info))

        return all_test_plan_case_info


if __name__ == '__main__':
    import time
    from create_session import Session
    from hpqc_query import HPQCQuery
    start = time.time()
    host = r'https://hpalm.intel.com'
    session = Session(host, 'pengzh5x', 'QQ@08061635')
    query = HPQCQuery('DCG', 'BKC')
    test_case = GetHPQCTestPlanCase(session, query, 'Bakerville')
    test_case.preserve_test_case_info()
    # test_case.get_plan_case_info()
    # test_case.return_close()
    # test_case.establish_test_plan_case_cache_dir()
    print time.time() - start
    # with open('test_case_combine_pnp6.txt', 'r') as p:
    #     for line in p:
    #         print line.strip()