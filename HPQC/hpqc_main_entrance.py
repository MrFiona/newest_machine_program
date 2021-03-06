#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-11 08:52
# Author  : MrFiona
# File    : hpqc_main_entrance.py
# Software: PyCharm Community Edition



import os
import re
import csv
import json
import random
try:
    import cPickle as pickle
except:
    import pickle
import time
from operator import itemgetter
from _hpqc_parser_tool import HPQC_info_parser_tool
from hpqc_parser import HPQCWHQLParser
from hpqc_create_operation import create_test_set, create_test_set_folders, create_test_instance_json
from hpqc_common_func import create_test_set_decorator
from setting_global_variable import HPQC_CACHE_DIR, HPQC_PARENT_PATH, EXCEL_TEST_CASE_RESULT

__file_name = os.path.split(__file__)[1]



#todo 获取项目名称以及id
def get_program_name_id(query, session, program_name):
    program_name_id_list = []
    while 1:
        result = query.enumerate_folder_private(0, session, 0, print_error=True)
        if result:
            break
    for element in result:
        if program_name == element[1]:
            program_name_id_list.append(element)
    # print 'program_name_id_list:\t', program_name_id_list
    return program_name_id_list


#todo 获取最近一周周目录名称以及id
def get_program_max_week_folders(logger, query, session, program_name):
    test_sets = query.enumerate_folder(program_name, session)
    if test_sets:
        # week_folders_id_list = [ folders for folders in test_sets ]
        week_folders_id_list = [ folders for folders in test_sets if re.match('\d+WW\d+', folders[1]) ]
        # week_folders_id_list.sort(key=lambda x: x[1], reverse=True)
        week_folders_id_list.sort(key=itemgetter(1), reverse=True)
        logger.print_message('week_folders_id_list:\t%s' % (week_folders_id_list,), __file_name)
    else:
        week_folders_id_list = []
    week_name_id_list = list(week_folders_id_list[0])
    return week_name_id_list


#todo 获取指定目录下的目录名称以及id flag: 1--test-plan；0--test-lab
def get_folders_by_parent_id(query, session, parent_id, flag):
    result = query.enumerate_folder_private(parent_id,session, flag)
    return result


#todo 生成待创建周目录的名称 根据系统时间生成
def generate_newest_week_name(week_name_id_list):
    # week_name = week_name_id_list[1]
    # split_list = week_name.split('WW')
    # print 'split_list:\t', split_list
    # week_num = int(split_list[-1])
    # split_list[-1] = str(week_num + 10)
    # return 'WW'.join(split_list)
    time_string = time.strftime("%Y-%m-%d %U", time.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), '%Y-%m-%d %X'))
    time_list = re.split('[- ]', time_string)
    year, week_num = time_list[0], str(int(time_list[-1]) + 1)
    if len(week_num) == 1:
        week_num = ''.join(['0',week_num])
    return 'WW'.join([year, week_num])



#todo 正常流程主程序
def HPQC_main_entrance(logger, query, session, program_name):
    program_name_id_list = get_program_name_id(query, session, program_name)
    logger.print_message('program_name_id_list:\t%s' % (program_name_id_list,), __file_name)
    week_name_id_list = get_program_max_week_folders(logger, query, session, program_name)
    #todo 获取未创建最新目录之前最大week目录下的目录名称以及id
    logger.print_message('week_name_id_list:\t%s' % (week_name_id_list,), __file_name)
    son_week_dir_name_id_list = get_folders_by_parent_id(query, session, int(week_name_id_list[0]), 0)
    logger.print_message('son_week_dir_name_id_list:\t%s' % (son_week_dir_name_id_list,), __file_name)

    #todo 创建最新的周目录
    newest_week_name = generate_newest_week_name(week_name_id_list)
    logger.print_message('newest_week_name:\t%s' % (newest_week_name,), __file_name)
    create_test_set_folders(session, newest_week_name, program_name_id_list[0][0], 'newest_week', program_name_id_list[0][1], print_error=True)
    with open(HPQC_PARENT_PATH + os.sep + 'create_test_folders_' + program_name + os.sep + 'newest_week_json_data.json', 'rb') as p:
        json_data = json.load(p)
    newest_week_dir_id = [ element['values'][0]['value'] for element in json_data['Fields'] if element['Name'] == 'id' ][0]
    logger.print_message('newest_week_dir_id:\t%s%s' %(newest_week_dir_id, type(newest_week_dir_id)), __file_name)
    #todo 创建最新周目录下的子目录
    for son_name in son_week_dir_name_id_list:
        create_test_set_folders(session, son_name[1], int(newest_week_dir_id), son_name[1], program_name_id_list[0][1], print_error=True)
    #todo 在新创建的周目录创建test-set

    header_list = [u'project', u'work_week', u'test_set_name', u'test_case_name', u'test_case_id',
                   u'attended', u'create_date', u'designer', u'domain', u'priority', u'setup_time',
                   u'status', u'type', u'unattended', u'test_exec_date']
    num_line = 1
    csv_file = open(HPQC_PARENT_PATH + os.sep + '%s_%s_test_case.csv' % (program_name_id_list[0][1], week_name_id_list[1]), 'wb')
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(header_list)

    #todo test-case与domain信息字典
    test_case_domain_dict = {}
    test_case_info_dict = {}
    all_insert_data = []
    upload_all_test_case = []
    all_test_case_name_info_dict = {}

    #todo 读取项目test plan里的test case信息
    with open(HPQC_PARENT_PATH + os.sep + 'HPQC_test_plan' + os.sep + program_name + os.sep + 'test_plan_case_detail_info.dump', 'rb') as fp:
        case_data = pickle.load(fp)
        #todo 存储项目test plan里的所有test case名称
        test_plan_all_test_case_name = sorted(case_data.keys())

    for path, dirs, files in os.walk(HPQC_CACHE_DIR):
        for name in files:
            test_case_domain_dict[name] = os.path.join(path, name)
    logger.print_message('tes_case_domain_dict:\t%s' % (test_case_domain_dict,), __file_name)

    #todo 是否新的test case出现
    exist_new_case = False
    new_test_case_info = []
    bkc_test_set_id = []

    for son_name in son_week_dir_name_id_list:
        logger.print_message('son_name:\t%s' % (son_name,), __file_name)
        #todo 获取子目录下的test-set名称以及id
        test_set_id_name_list = query.enumerate_test_set_private(son_name[0], session, 0)
        logger.print_message('test_set_id_name_list:\t%s' % (test_set_id_name_list,), __file_name)

        #todo 获取json文本里已经创建的子目录id
        with open(HPQC_PARENT_PATH + os.sep + 'create_test_folders_' + program_name + os.sep + son_name[1] + '_json_data.json', 'rb') as p:
            json_data = json.load(p)
        newest_son_week_dir_id = [element[u'values'][0][u'value'] for element in json_data[u'Fields'] if element[u'Name'] == 'id'][0]
        logger.print_message('newest_son_week_dir_id:\t%s' % (newest_son_week_dir_id,), __file_name)
        #todo 在子目录中创建test-set
        for test_set in test_set_id_name_list:
            test_set_new = test_set[1].replace('/', '#')
            logger.print_message('test_set_new:\t%s' % (test_set_new,), __file_name)
            create_test_set(session, test_set[1], int(newest_son_week_dir_id), test_set_new, program_name_id_list[0][1], print_error=True)
            #todo 上传test-case到test-set中
            with open(HPQC_PARENT_PATH + os.sep + 'create_test_set_' + program_name + os.sep + test_set_new + '_' + str(newest_son_week_dir_id) + '_json_data.json', 'rb') as p:
                json_data = json.load(p)
            newest_test_set_id = [element[u'values'][0][u'value'] for element in json_data[u'Fields'] if element[u'Name'] == 'id'][0]
            logger.print_message('newest_test_set_id:\t%s' % (newest_test_set_id,), __file_name)

            #todo 保存新建BKC目录下的test set id 信息用于上传新的test case
            if son_name == u'BKC':
                bkc_test_set_id.append(newest_test_set_id)

            #todo 获取上一周对应位置的相同test-set里的test-case相关信息并将test-case上传到最新创建的test-case
            json_obj = query.enumerate_test_instance_private(son_name[1], test_set[0], session, program_name_id_list[0][1], test_set_new)
            parser = HPQCWHQLParser()
            test_case_dict_list = parser.ParseTestInstance(json_obj)
            #todo 按照test-case name 排序
            test_case_dict_list = sorted(test_case_dict_list, key=lambda x: x[u'casename'])
            logger.print_message('test_case_dict_list:\t%s' % (test_case_dict_list,), __file_name)
            if test_set_id_name_list:
                test_set_id_name_list = []
            #todo 得到上一周test-set里的test-case然后依次创建
            for test_case in test_case_dict_list:
                logger.print_message('test_case:\t%s' % (test_case,), __file_name)
                case_info = {u'status': test_case[u'status'],
                             u'exec_date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                             u'test_set_id': str(newest_test_set_id),
                             u'value': u'',
                             u'unit': u'MB/Sec',
                             u'iterations':u'1',
                             u'hsd_id': u'',
                             u'test_case_id':  test_case[u'test_case_id'],
                             u'test_case_order': u'1',
                             u'exec-time': time.strftime('%H-%M-%S', time.localtime(time.time()))}
                logger.print_message('case_info:\t%s' % (case_info,), __file_name)

                #todo 对上传的test-case进行过滤 start
                with open(EXCEL_TEST_CASE_RESULT + os.sep + 'excel_result_test_case.dump', 'rb') as fp:
                    data = pickle.load(fp)
                true_data = [ele[3] for ele in data if ele[0] == True]

                #todo 如果test-case不在excel表格caseresult表里True为的test-case集合
                #todo 并且test-case不在项目的test plan里则视为新的test case，新的上传到BKC目录里(BKC目录必须存在，否则报错)
                #todo 在表里则正常上传到对应目录对应位置
                #todo test case在true_data里则肯定在项目test plan所有的test case列表里
                if test_case[u'casename'] in true_data:
                    upload_all_test_case.append(test_case[u'casename'])
                    #todo 开始上传test-case到新建的test-set
                    create_test_instance_json(case_info, session, print_error=True)
                    #todo 获取test-case domain信息
                    file_name = '.'.join([str(test_case['test_case_id']), 'json'])
                    if file_name in test_case_domain_dict:
                        test_case_file_path = test_case_domain_dict[file_name]
                        with open(test_case_file_path, 'rb') as fp:
                            data = json.load(fp)
                        test_case_info_dict = HPQC_info_parser_tool(data)
                        logger.print_message('test_case_info_dict:\t%s' % (test_case_info_dict,), __file_name)

                    insert_data = [program_name, son_name[1], test_set[1], test_case[u'casename'], test_case[u'test_case_id'], test_case_info_dict[u'_attended'],
                                   test_case_info_dict[u'_create_date'], test_case_info_dict[u'_designer'], test_case_info_dict[u'_domain'],
                                   test_case_info_dict[u'_priority'], test_case_info_dict[u'_setup_time'], test_case_info_dict[u'_status'],
                                   test_case_info_dict[u'_type'], test_case_info_dict[u'_unattended'], time.strftime('%Y-%m-%d', time.localtime(time.time()))]
                    all_test_case_name_info_dict[test_case[u'casename']] = insert_data
                    logger.print_message('insert_data:\t%s' % (insert_data,), __file_name)
                    all_insert_data.append(insert_data)
                    time.sleep(0.01)
                    num_line += 1
                #todo 存在新的test case
                elif test_case[u'casename'] not in true_data and test_case[u'casename'] not in test_plan_all_test_case_name:
                    exist_new_case = True
                    new_test_case_info.append(case_info)

            time.sleep(0.01)

    #todo 当新的test case信息存在且为BKC目录且BKC目录下存在test set
    if exist_new_case and new_test_case_info and bkc_test_set_id:
        #todo 有可能存在多个新的test case
        for case in new_test_case_info:
            #todo 更改上传信息为上传到BKC目录下的某个test set 随机选
            test_set_id = random.choice(bkc_test_set_id)
            case[u'test_set_id'] = str(test_set_id)
            case[u'exec_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            case[u'exec-time'] = time.strftime('%H-%M-%S', time.localtime(time.time()))
            #todo 开始上传test-case到新建的test-set
            create_test_instance_json(new_test_case_info, session)
        logger.print_message(u'存在新的test case，已上传', __file_name)

    logger.print_message('all_test_case_name_info_dict:\t%s%d' %(all_test_case_name_info_dict, len(all_test_case_name_info_dict)), __file_name)
    writer.writerows(all_insert_data)
    logger.print_message(u'上传的所有test case名称列表:\t%s%d' %(upload_all_test_case, len(upload_all_test_case)), __file_name)
    csv_file.close()


#todo 仅执行HPQC功能的主程序
def HPQC_main_entrance_all_copy(logger, query, session, program_name):
    program_name_id_list = get_program_name_id(query, session, program_name)
    logger.print_message('program_name_id_list:\t%s' % (program_name_id_list,), __file_name)
    week_name_id_list = get_program_max_week_folders(logger, query, session, program_name)
    #todo 获取未创建最新目录之前最大week目录下的目录名称以及id
    logger.print_message('week_name_id_list:\t%s' % (week_name_id_list,), __file_name)
    son_week_dir_name_id_list = get_folders_by_parent_id(query, session, int(week_name_id_list[0]), 0)
    logger.print_message('son_week_dir_name_id_list:\t%s' % (son_week_dir_name_id_list,), __file_name)

    #todo 创建最新的周目录
    newest_week_name = generate_newest_week_name(week_name_id_list)
    logger.print_message('newest_week_name:\t%s' % (newest_week_name,), __file_name)
    create_test_set_folders(session, newest_week_name, program_name_id_list[0][0], 'newest_week', program_name_id_list[0][1], print_error=True)
    with open(HPQC_PARENT_PATH + os.sep + 'create_test_folders_' + program_name + os.sep + 'newest_week_json_data.json', 'rb') as p:
        json_data = json.load(p)
    newest_week_dir_id = [ element['values'][0]['value'] for element in json_data['Fields'] if element['Name'] == 'id' ][0]
    logger.print_message('newest_week_dir_id:\t%s%s' %(newest_week_dir_id, type(newest_week_dir_id)), __file_name)
    #todo 创建最新周目录下的子目录
    for son_name in son_week_dir_name_id_list:
        create_test_set_folders(session, son_name[1], int(newest_week_dir_id), son_name[1], program_name_id_list[0][1], print_error=True)
    #todo 在新创建的周目录创建test-set

    header_list = [u'project', u'work_week', u'test_set_name', u'test_case_name', u'test_case_id',
                   u'attended', u'create_data', u'designer', u'domain', u'priority', u'setup_time',
                   u'status', u'type', u'unattended', u'test_exec_date']
    num_line = 1
    csv_file = open(HPQC_PARENT_PATH + os.sep + '%s_%s_test_case.csv' % (program_name_id_list[0][1], week_name_id_list[1]), 'wb')
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(header_list)

    #todo test-case与domain信息字典
    test_case_domain_dict = {}
    test_case_info_dict = {}
    all_insert_data = []
    upload_all_test_case = []
    all_test_case_name_info_dict = {}

    for path, dirs, files in os.walk(HPQC_CACHE_DIR):
        for name in files:
            test_case_domain_dict[name] = os.path.join(path, name)
    logger.print_message('tes_case_domain_dict:\t%s' % (test_case_domain_dict,), __file_name)

    for son_name in son_week_dir_name_id_list:
        logger.print_message('son_name:\t%s' % (son_name,), __file_name)
        #todo 获取子目录下的test-set名称以及id
        test_set_id_name_list = query.enumerate_test_set_private(son_name[0], session, 0)
        logger.print_message('test_set_id_name_list:\t%s' % (test_set_id_name_list,), __file_name)

        #todo 获取json文本里已经创建的子目录id
        with open(HPQC_PARENT_PATH + os.sep + 'create_test_folders_' + program_name + os.sep + son_name[1] + '_json_data.json', 'rb') as p:
            json_data = json.load(p)
        newest_son_week_dir_id = [element[u'values'][0][u'value'] for element in json_data[u'Fields'] if element[u'Name'] == 'id'][0]
        logger.print_message('newest_son_week_dir_id:\t%s' % (newest_son_week_dir_id,), __file_name)
        #todo 在子目录中创建test-set
        for test_set in test_set_id_name_list:
            test_set_new = test_set[1].replace('/', '#')
            logger.print_message('test_set_new:\t%s' % (test_set_new,), __file_name)
            create_test_set(session, test_set[1], int(newest_son_week_dir_id), test_set_new, program_name_id_list[0][1], print_error=True)
            #todo 上传test-case到test-set中
            with open(HPQC_PARENT_PATH + os.sep + 'create_test_set_' + program_name + os.sep + test_set_new + '_' + str(newest_son_week_dir_id) + '_json_data.json', 'rb') as p:
                json_data = json.load(p)
            newest_test_set_id = [element[u'values'][0][u'value'] for element in json_data[u'Fields'] if element[u'Name'] == 'id'][0]
            logger.print_message('newest_test_set_id:\t%s' % (newest_test_set_id,), __file_name)

            #todo 获取上一周对应位置的相同test-set里的test-case相关信息并将test-case上传到最新创建的test-case
            json_obj = query.enumerate_test_instance_private(son_name[1], test_set[0], session, program_name_id_list[0][1], test_set_new)
            parser = HPQCWHQLParser()
            test_case_dict_list = parser.ParseTestInstance(json_obj)
            #todo 按照test-case name 排序
            test_case_dict_list = sorted(test_case_dict_list, key=lambda x: x[u'casename'])
            logger.print_message('test_case_dict_list:\t%s' % (test_case_dict_list,), __file_name)
            if test_set_id_name_list:
                test_set_id_name_list = []
            #todo 得到上一周test-set里的test-case然后依次创建
            for test_case in test_case_dict_list:
                logger.print_message('test_case:\t%s' % (test_case,), __file_name)
                case_info = {u'status': test_case[u'status'],
                             u'exec_date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                             u'test_set_id': str(newest_test_set_id),
                             u'value': u'',
                             u'unit': u'MB/Sec',
                             u'iterations':u'1',
                             u'hsd_id': u'',
                             u'test_case_id':  test_case[u'test_case_id'],
                             u'test_case_order': u'1',
                             u'exec-time': time.strftime('%H-%M-%S', time.localtime(time.time()))}
                logger.print_message('case_info:\t%s' % (case_info,), __file_name)

                upload_all_test_case.append(test_case[u'casename'])
                #todo 开始上传test-case到新建的test-set
                create_test_instance_json(case_info, session, print_error=True)
                #todo 获取test-case domain信息
                file_name = '.'.join([str(test_case['test_case_id']), 'json'])
                if file_name in test_case_domain_dict:
                    test_case_file_path = test_case_domain_dict[file_name]
                    with open(test_case_file_path, 'rb') as fp:
                        data = json.load(fp)
                    test_case_info_dict = HPQC_info_parser_tool(data)
                    logger.print_message('test_case_info_dict:\t%s' % (test_case_info_dict,), __file_name)

                insert_data = [program_name, son_name[1], test_set[1], test_case[u'casename'], test_case[u'test_case_id'], test_case_info_dict[u'_attended'],
                               test_case_info_dict[u'_create_date'], test_case_info_dict[u'_designer'], test_case_info_dict[u'_domain'],
                               test_case_info_dict[u'_priority'], test_case_info_dict[u'_setup_time'], test_case_info_dict[u'_status'],
                               test_case_info_dict[u'_type'], test_case_info_dict[u'_unattended'], time.strftime('%Y-%m-%d', time.localtime(time.time()))]
                all_test_case_name_info_dict[test_case[u'casename']] = insert_data
                logger.print_message('insert_data:\t%s' % (insert_data,), __file_name)
                all_insert_data.append(insert_data)
                time.sleep(0.01)
                num_line += 1

            time.sleep(0.01)

    logger.print_message('all_test_case_name_info_dict:\t%s%d' %(all_test_case_name_info_dict, len(all_test_case_name_info_dict)), __file_name)
    writer.writerows(all_insert_data)
    logger.print_message(u'上传的所有test case名称列表:\t%s%d' %(upload_all_test_case, len(upload_all_test_case)), __file_name)
    csv_file.close()



#todo 创建test-set
@create_test_set_decorator
def func_create_test_set(session, split_info_list, program_id, program_name, print_error=True):
    # todo 创建test-set
    create_test_set(session, split_info_list[-1], int(program_id), split_info_list[-1], program_name, print_error=print_error)
    with open('create_test_set_' + program_name + os.sep + split_info_list[-1] + '_' + str(
            program_id) + '_json_data.json', 'rb') as p:
        json_data = json.load(p)

    return json_data



# start = time.time()
# host = r'https://hpalm.intel.com'
# session = Session(host, 'pengzh5x', 'QQ@08061635')
# query = HPQCQuery('DCG', 'BKC')
# HPQC_main_entrance(query, session, 'Bakerville')
# f_case = open('result_test_case_info_pnp113.txt', 'w')
# f_case_combine = open('test_case_combine_pnp113.txt', 'w')
# recursive_get_program_test_case_or_test_sets(query, f_case, f_case_combine, 'Subject/Bakerville', session, 0)
# f_case.close()
# f_case_combine.close()

# print time.time() - start
