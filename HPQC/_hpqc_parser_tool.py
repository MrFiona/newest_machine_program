#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-10-12 14:24
# Author  : MrFiona
# File    : _hpqc_parser_tool.py
# Software: PyCharm Community Edition



#todo 解析单个test_case json文件
def HPQC_info_parser_tool(data):
    global_info_dict = {}
    info = data[u'entities'][0][u'Fields']

    for element in info:
        if element[u'Name'] == u'user-08':
            if element[u'values']:
                _applicable_platform = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_applicable_platform', _applicable_platform)

        if element[u'Name'] == u'user-01':
            if element[u'values']:
                _attended = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_attended', _attended)

        if element[u'Name'] == u'user-04':
            _domain = element[u'values'][0].get(u'value', None)
            global_info_dict.setdefault('_domain', _domain)

        if element[u'Name'] == u'user-07':
            if element[u'values']:
                _priority = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_priority', _priority)

        if element[u'Name'] == u'user-02':
            if element[u'values']:
                _setup_time = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_setup_time', _setup_time)

        if element[u'Name'] == u'user-03':
            if element[u'values']:
                _unattended = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_unattended', _unattended)

        if element[u'Name'] == u'user-06':
            if element[u'values']:
                _config = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_config', _config)

        if element[u'Name'] == u'name':
            _test_name = element[u'values'][0].get(u'value', None)
            global_info_dict.setdefault('_test_name', _test_name)

        if element[u'Name'] == u'status':
            if element[u'values']:
                _status = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_status', _status)

        if element[u'Name'] == u'owner':
            if element[u'values']:
                _designer = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_designer', _designer)

        if element[u'Name'] == u'creation-time':
            if element[u'values']:
                _create_date = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_create_date', _create_date)

        if element[u'Name'] == u'subtype-id':
            if element[u'values']:
                _type = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_type', _type)

        if element[u'Name'] == u'id':
            if element[u'values']:
                _test_id = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_test_id', _test_id)

    # print global_info_dict
    return global_info_dict



if __name__ == '__main__':
    import json
    # with open(r'C:\Users\pengzh5x\Desktop\machine_scripts\HPQC\test_case_cache\Subject\Bakerville\TCD_Candidate_ww51\Linux\P1\Memory\DDR4\PI_Memory_DDR4_DIMMMaximumMemory_L\11614.json', 'r') as p:
    #     data = json.load(p)
    #     global_info_dict = HPQC_info_parser_tool(data)
    #     print global_info_dict
    #
    #
    # import os
    # all_test_case = []
    # for path, dirs, files in os.walk(r'C:\Users\pengzh5x\Desktop\machine_scripts\HPQC\test_case_cache\Subject\Bakerville'):
    #     for name in files:
    #         print os.path.join(path, name)
    #         all_test_case.append(os.path.join(path, name))
    #
    # test_case_name = [test.split(os.sep)[-2] for test in all_test_case ]
    # # os.path.split()
    # print 'all_test_case:\t', all_test_case, len(all_test_case)
    # print 'test_case_name:\t', test_case_name, len(test_case_name)
    #
    # all_test_case_key_info = []
    #
    # for i in range(len(all_test_case)):
    #     with open(all_test_case[i], 'r') as fp:
    #         data = json.load(fp)
    #         test_case_info_dict = HPQC_info_parser_tool(data)
    #     print '解析文件第[%d]个test case [ %s ]结果为:\t%s' % (i+1, test_case_name[i], test_case_info_dict)
    #     all_test_case_key_info.append(test_case_info_dict)
    #
    #
    # with open('test.dump', 'wb') as fp:
    #     json.dump(all_test_case_key_info, fp)

    # import pickle
    # with open(r'C:\Users\pengzh5x\Desktop\machine_scripts\HPQC\HPQC_test_plan\Bakerville\test_plan_case_detail_info.dump', 'rb') as fp:
    #     data = pickle.load(fp)
    #     # print data, len(data), type(data)
    #     test_case_dict_list = sorted(data.items(), key=lambda x: x[1][u'_test_name'])
    #     # print test_case_dict_list, len(test_case_dict_list)
    #     for ele in test_case_dict_list:
    #         print ele, type(ele), ele[1]