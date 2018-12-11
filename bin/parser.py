###################################################################
# File Name: parse.py
# Author: jiangtao
# mail: vlan945@163.com
# Created Time: 2018年12月10日 星期一 11时36分23秒
# Python version: 3.6.5
#=============================================================
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import yaml
import os
import time
import shutil

class ParserBase(object):
    def __init__(self, filename='filepath.yaml', timeout=60, run=True, echo=True):
        with open(filename, 'r') as f:
            self.conf = yaml.load(f)
        self.conf_servers = {i for i in self.conf}
        self.groups = {'newivrservers', 'oldivrservers', 'ivrservers', 'assignservers', 'agentservers', 'pbxservers'}
        self.roles = {'pbx', 'cti', 'agi', 'crond'}
        self.rootpath = '/etc/ansible/roles'
        self.srcpath='/etc/ansible/bin/src'
        self.time = time.time()
        self.timeout = timeout  # 超时时间、用于计算文件是否为刚复制过去的、
        self.time_dir = "bak/%s_%s/" % (time.strftime('%Y%m%d_%H%M'), os.getpid())
        self.run = run  # 是否执行复制/移动文件、
        self.echo = echo  # 写入日志时、是否同时在控制台打印、
        self.logname = "copy.log"  # 日志文件名

    @staticmethod
    def mksure_dir(dirpath):
        """确保目录存在"""
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)

    def _getsubgroup(self, group):
        """根据group返回包含的subgroup"""
        self.wlog('[ %s ]' % group)
        if group == 'pbxservers':
            subgroups = ['newivrservers', 'oldivrservers', 'assignservers', 'agentservers']
        elif group == 'ivrservers':
            subgroups = ['newivrservers', 'oldivrservers']
        else:
            subgroups = [group, ]
        return subgroups

    @staticmethod
    def _replacepath(role, subfile_values):
        """根据role和要复制到远程机器上的路径、替换目录"""
        if role == 'pbx':
            dest_path = subfile_values.replace('/data/justcall/pbx/', '')
        elif role == 'cti':
            dest_path = subfile_values.replace('/data/justcall/just_cti_server/', '')
        elif role == 'agi':
            dest_path = subfile_values.replace('/data/justcall/justagi/', '')
        elif role == 'crond':
            if subfile_values.replace('/data/justcall/crontab/', 'justcall/') == subfile_values:
                dest_path = subfile_values.replace('/data/public/crontab/', 'public/')
            else:
                dest_path = subfile_values.replace('/data/justcall/crontab/', 'justcall/')
        return dest_path


    def wlog(self, logstr):
        """写日志"""
        time_logstr = time.strftime('[ %Y-%m-%d %H:%M:%S ] ') + logstr
        if self.echo:
            print(time_logstr)
        if self.run:
            with open(self.logname, 'a+') as f:
                f.write(time_logstr + '\n')


    def baksrc(self, srcpath):
        """备份源文件"""
        src_list = os.listdir(srcpath)
        if len(src_list) > 1:
            self.wlog(' BACK SRC FILE '.center(50, '*'))
        for f in src_list:
            if f == 'bak': continue
            src_bak_dir = os.path.join(srcpath, self.time_dir, os.path.split(f)[0])
            src_bak_src = os.path.join(srcpath, f)
            src_bak_dest = os.path.join(srcpath, self.time_dir, f)
            self.mksure_dir(src_bak_dir)
            if self.run and os.path.exists(src_bak_src):
                shutil.move(src_bak_src, src_bak_dest)
            self.wlog('< backup src > mv %s %s' % (src_bak_src, src_bak_dest)) # backup src 


    def mycp(self, onlyclean=False):
        """执行复制/移动的函数、onlyclean-用于清空源文件和目标目录文件、"""
        src_bak_dir = os.path.join(self.srcpath, self.time_dir)
        self.mksure_dir(src_bak_dir)
        if bool(self.conf_servers - self.groups):
            slef.wlog("ERROR: Unknown group.", self.conf_servers - self.groups)
            exit(2)

        for group in self.conf_servers:
            subgroups = self._getsubgroup(group)
            for role, role_values in self.conf.get(group).items():
                for filepath, filepath_values in role_values.items():
                    for subfile, subfile_values in filepath_values.items():
                        src = subfile # ansible_sip.conf
                        for subgroup in subgroups:
                            dest_path = self._replacepath(role, subfile_values)
                            dest = os.path.join(self.rootpath, role, filepath, subgroup, dest_path)
                            dest_dir = os.path.dirname(dest)
                            for i in os.listdir(dest_dir):
                                dest_bak_dir = os.path.join(dest_dir, self.time_dir, os.path.split(i)[0]) # 备份目标的目标目录、
                                dest_bak_src = os.path.join(dest_dir,i) # 备份目标的源文件、
                                dest_bak_dest = os.path.join(dest_dir, self.time_dir, i) # 备份目标的目标文件、
                                self.mksure_dir(dest_bak_dir)
                                if i == 'bak' or self.time - os.lstat(dest_bak_src).st_mtime < self.timeout:
                                    continue
                                if self.run and os.path.exists(dest_bak_src):
                                    shutil.move(dest_bak_src, dest_bak_dest)
                                self.wlog('< backup dest > mv %s %s' % (dest_bak_src, dest_bak_dest))  # backup dest 
                            src_abs = os.path.join(self.srcpath, src)
                            if self.run and onlyclean and os.path.exists(src_abs):
                                if not os.path.exists(src_abs):
                                    self.wlog('< file not exist > %s' % src_abs)
                                    exit(127)
                                shutil.copy(src_abs, dest)
                            self.wlog('< cp file > cp %s %s' % (src_abs, dest))  # copy
        self.baksrc(self.srcpath)

if __name__ == '__main__':
    my = ParserBase(filename='filepath.yaml', timeout=60, run=True)
    my.mycp(onlyclean=False)





