#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-08-22 22:45
# Author  : MrFiona
# File    : separate_read.py
# Software: PyCharm


# -*- coding: GBK -*-
import urlparse
import datetime
import os
from multiprocessing import Process,Queue,Array,RLock
"""
多进程分块读取文件
"""
WORKERS = 4
BLOCKSIZE = 100000000
FILE_SIZE = 0
def getFilesize(file):
    """
   获取要读取文件的大小
    """
    global FILE_SIZE
    fstream = open(file,'r')
    fstream.seek(0,os.SEEK_END)
    FILE_SIZE = fstream.tell()
    fstream.close()

def process_found(pid,array,file,rlock, FILE_SIZE):
    global JOB
    global PREFIX
    """
    进程处理
    Args:
      pid:进程编号
      array:进程间共享队列，用于标记各进程所读的文件块结束位置
      file:所读文件名称
    各个进程先从array中获取当前最大的值为起始位置startpossition
    结束的位置endpossition (startpossition+BLOCKSIZE) if (startpossition+BLOCKSIZE)<FILE_SIZE else FILE_SIZE
    if startpossition==FILE_SIZE则进程结束
    if startpossition==0则从0开始读取
    if startpossition!=0为防止行被block截断的情况，先读一行不处理，从下一行开始正式处理
    if 当前位置 <=endpossition 就readline
    否则越过边界，就从新查找array中的最大值
  """
    fstream = open(file,'r')
    while True:
        rlock.acquire()
        print 'pid%s'%pid,','.join([str(v) for v in array])
        startpossition = max(array)
        print 'startpossition:\t', startpossition
        print 'FILE_SIZE:\t', FILE_SIZE
        endpossition = array[pid] = (startpossition+BLOCKSIZE) if (startpossition+BLOCKSIZE)<FILE_SIZE else FILE_SIZE
        rlock.release()
        print 'startpossition:\t', startpossition
        if startpossition == FILE_SIZE:#end of the file
            print 'pid%s end'%(pid)
            break
        elif startpossition !=0:
            fstream.seek(startpossition)
            fstream.readline()
        pos = ss = fstream.tell()
        ostream = open(r'C:\Users\Public\newest_machine_program'+str(pid)+'_jobs'+str(endpossition),'w')
        while pos<endpossition:
            #处理line
            line = fstream.readline()
            print 'line:\t', line
            ostream.write(line)
            pos = fstream.tell()
        print 'pid:%s,startposition:%s,endposition:%s,pos:%s'%(pid,ss,pos,pos)
        ostream.flush()
        ostream.close()
        ee = fstream.tell()
        print 'ee:\t', ee
    fstream.close()

def main():
    global FILE_SIZE
    print datetime.datetime.now().strftime("%Y/%d/%m %H:%M:%S")
    # file = "/data/pds/download/scmcc_log/tmp_format_2011004.log"
    # file = r"C:\Users\Public\newest_machine_program\excel_dir\Purley-FPGA_100_2017WW31_36_2017_08_16_02_02_29.xlsx"
    file = r"C:\Users\Public\newest_machine_program\requirements.txt"
    getFilesize(file)
    print FILE_SIZE
    rlock = RLock()
    array = Array('i',WORKERS,lock=rlock)
    threads=[]
    for i in range(WORKERS):
        p=Process(target=process_found, args=[i,array,file,rlock, FILE_SIZE])
        threads.append(p)
    for i in range(WORKERS):
        threads[i].start()
    for i in range(WORKERS):
        threads[i].join()
    print datetime.datetime.now().strftime("%Y/%d/%m %H:%M:%S")


if __name__ == '__main__':
    main()