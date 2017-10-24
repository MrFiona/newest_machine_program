#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-08-22 13:48
# Author  : MrFiona
# File    : compress_result.py
# Software: PyCharm Community Edition


import os
import glob
import time
import tarfile
import shutil
import traceback


#todo 错误异常信息
def traceback_print_info():
    print '\033[35mError#####################################################Error\033[0m'
    print 'traceback.format_exc():\n%s' % traceback.format_exc()
    print '\033[35mError#####################################################Error\033[0m'

start = time.time()
current_time_string = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))

#todo 将machine_scripts目录下的文件拷贝至主程序machine_model_entrance.py同级目录下 start
orignal_parent_path = os.getcwd()
print 'orignal_parent_path:\t', orignal_parent_path
os.chdir('..')
main_program_path = os.getcwd()
machine_scripts_file_list = []
for element in glob.glob(os.getcwd() + os.sep + 'machine_scripts' + os.sep + '*.py'):
    if os.path.split(element)[-1] == '__init__.py':
        continue
    machine_scripts_file_list.append(element)
# print machine_scripts_file_list, len(machine_scripts_file_list)

#todo 当前在主程序目录 将文件拷贝至主目录
for element in machine_scripts_file_list:
    shutil.copy(element, os.getcwd())

os.chdir(orignal_parent_path)
#todo 将machine_scripts目录下的文件拷贝至主程序machine_model_entrance.py同级目录下 end

os.system('pyinstaller --onefile ../machine_model_entrance.py')
os.system('pyinstaller --onefile ../manual_mode_entrance.py')

parent_dir = os.path.split(os.getcwd())[0]
os.chdir('../')

#todo ********************** 将相关文件移动到 pyinstall_normal以及pyinstall_manual目录 **********************
if not os.path.exists('pyinstall_normal'):
    os.makedirs('pyinstall_normal')

if not os.path.exists('pyinstall_manual'):
    os.makedirs('pyinstall_manual')

if not os.path.exists('pyinstall_normal' + os.sep + 'machineConfig'):
    os.makedirs(parent_dir + os.sep + 'pyinstall_normal' + os.sep + 'machineConfig')

if not os.path.exists('pyinstall_manual' + os.sep + 'machineConfig'):
    os.makedirs(parent_dir + os.sep + 'pyinstall_manual' + os.sep + 'machineConfig')

machine_config_path = parent_dir + os.sep + 'machineConfig'
for ele in os.listdir(machine_config_path):
    shutil.copy2(machine_config_path+ os.sep + ele, parent_dir + os.sep + 'pyinstall_normal' + os.sep + 'machineConfig')
    shutil.copy2(machine_config_path+ os.sep + ele, parent_dir + os.sep + 'pyinstall_manual' + os.sep + 'machineConfig')

#todo 将tools目录下生成dist目录下的exe文件拷贝至目标目录 start
dist_dir_path = os.getcwd() + os.sep + 'tools' + os.sep + 'dist'
for file_exe in os.listdir(dist_dir_path):
    if 'machine_model_entrance' in file_exe:
        shutil.copy2(dist_dir_path + os.sep + file_exe, os.getcwd() + os.sep + 'pyinstall_normal')
    else:
        shutil.copy2(dist_dir_path + os.sep + file_exe, os.getcwd() + os.sep + 'pyinstall_manual')
#todo 将tools目录下生成dist目录下的exe文件拷贝至目标目录 end

shutil.copy2(os.getcwd() + os.sep + 'requirements.txt', os.getcwd() + os.sep + 'pyinstall_normal')
shutil.copy2(os.getcwd() + os.sep + 'requirements.txt', os.getcwd() + os.sep + 'pyinstall_manual')

#todo ********************** 将相关文件移动到 pyinstall_normal以及pyinstall_manual目录 **********************
#
#todo ********************** 清除pyc文件 **********************
#todo 调用清理文件脚本，路径切换到原来路径
os.chdir('./tools')
cmd_status = os.system('python ../machine_scripts/auto_clear_junk_file.py')
if 0 == cmd_status:
    print '\033[32mremove pyc file successfully!!!\033[0m'
#todo 目录路径还原
os.chdir('..')
#todo ********************** 清除pyc文件 **********************

try:
    #todo ********************** 压缩文件 **********************
    machine_config_path = 'machineConfig'
    machine_scripts_path = 'machine_scripts'
    pyinstall_manual_path = 'pyinstall_manual'
    pyinstall_normal_path = 'pyinstall_normal'
    requirement_path = 'requirements.txt'
    install_module_path = 'install_module.py'
    manual_model_path = 'manual_mode_entrance.py'
    machine_model_path = 'machine_model_entrance.py'
    setting_global_path = 'setting_global_variable.py'

    file_path_list = [machine_scripts_path, machine_config_path, install_module_path, machine_model_path,
                       manual_model_path, requirement_path, setting_global_path, pyinstall_normal_path,
                      pyinstall_manual_path]

    tar_object = tarfile.open(name=parent_dir + os.sep + 'machine_program_' + current_time_string + '_.tar.gz', mode='w:gz',)
    for file_path in file_path_list:
        tar_object.add(file_path)

    print '\033[36madd file as the following:\033[0m'
    tar_object.list(verbose=False)
    tar_object.close()
    print '\033[32mcompress the target file successfully!!!\033[0m'
    #todo ********************** 压缩文件 **********************

    #todo ********************** 清理文件 **********************
    shutil.rmtree(os.getcwd() + os.sep + 'pyinstall_normal')
    shutil.rmtree(os.getcwd() + os.sep + 'pyinstall_manual')

    clear_file_list = glob.glob(parent_dir + os.sep + 'tools' + os.sep + '*')
    clear_file_list = [ ele for ele in clear_file_list if not ele.endswith('.py')]
    for file_clear in clear_file_list:
        if os.path.isdir(file_clear):
            shutil.rmtree(file_clear)
        elif os.path.isfile(file_clear):
            os.remove(file_clear)
    #todo ********************** 清理文件 **********************
except:
    traceback_print_info()
    print '\033[31mcompress the target file failed!!!\033[0m'

#todo 删除拷贝至主目录中的文件
machine_scripts_file_list = [os.path.split(element)[-1] for element in machine_scripts_file_list]
for element in glob.glob(os.getcwd() + os.sep + '*.py'):
    if os.path.split(element)[-1] in machine_scripts_file_list:
        print element
        os.remove(element)

os.chdir('./tools')
print time.time() - start