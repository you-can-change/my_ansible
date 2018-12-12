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
import sys
import getopt

class ParserBase(object):
    def __init__(self, filename='filepath.yaml', stdfile='stddir.yaml', timeout=60, run=True, echo=True):
        with open(filename, 'r') as f:
            self.conf = yaml.load(f)
        with open(stdfile, 'r') as f:
            self.std = yaml.load(f)
        self.conf_servers = {i for i in self.conf}
        self.groups = {'newivrservers', 'oldivrservers', 'ivrservers', 'assignservers', 'agentservers', 'pbxservers'}
        self.roles = {'pbx', 'cti', 'agi', 'crond'}
        self.rootpath = '/etc/ansible/roles'
        self.srcpath='/etc/ansible/bin/src'
        self.time = time.time()
        self.timeout = timeout  # 超时时间(s)、用于计算文件是否在timeout时间范围内复制过去的、如果不是则将其移到备份目录下、
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
        time_logstr = "%s < %s > %s\n" % (time.strftime('[ %Y-%m-%d %H:%M:%S ] ') , os.getpid(), logstr)
        if self.echo:
            print(time_logstr)
        if self.run:
            with open(self.logname, 'a+') as f:
                f.write(time_logstr)


    def baksrc(self, sub_run=True):
        """备份源文件"""
        src_list = os.listdir(self.srcpath)
        if len(src_list) <= 1:
            return 
        for f in src_list:
            if f == 'bak': continue
            src_bak_dir = os.path.join(self.srcpath, self.time_dir, os.path.split(f)[0])
            src_bak_src = os.path.join(self.srcpath, f)
            src_bak_dest = os.path.join(self.srcpath, self.time_dir, f)
            self.mksure_dir(src_bak_dir)
            if self.run and sub_run and os.path.exists(src_bak_src):
                shutil.move(src_bak_src, src_bak_dest)
                self.wlog('< backup src > mv %s %s' % (src_bak_src, src_bak_dest)) # backup src 

    def back_role(self, sub_run=True):
        """备份roles中的files和templates目录、将这个2个目录完全移走到/etc/ansible/roles/{pbx,cti,agi,crond}/bak/xxxxxx/下、"""
        file_path = ['files', 'templates']
        for role, role_values in self.std.items(): 
            for filepath, filepath_values in role_values.items():
                if filepath in file_path:
                    file_bak_src = os.path.join(self.rootpath, role, filepath)
                    file_bak_dir = os.path.join(self.rootpath, role, self.time_dir)  # /etc/ansible/roles/pbx/bak/xxxxxxx/
                    file_bak_dest = os.path.join(file_bak_dir, filepath)
                    self.mksure_dir(file_bak_dir)
                    if self.run and sub_run and os.path.exists(file_bak_src):
                        shutil.move(file_bak_src, file_bak_dest)
                        self.wlog("move %s %s" % (file_bak_src, file_bak_dest))
        
    def create_role(self, path, mydict, sub_run=True):
        """根据传入的mydict、(只能传入self.std)中定义的目录结构递归创建roles和templates目录"""
        tmp_path = path
        if mydict is not None:
            for key, value in mydict.items():
                path = os.path.join(tmp_path, key)
                self.create_role(path, value, sub_run=sub_run)
        else:
            if self.run and sub_run:
                os.makedirs(path)
                self.wlog("create dir %s" % path)
    
    def mycp(self, sub_run=True):
        """执行复制/移动的函数、onlyclean-仅备份源文件和目标目录文件、不复制、"""
        if bool(self.conf_servers - self.groups):
            slef.wlog("ERROR: Unknown group.", self.conf_servers - self.groups)
            exit(2)

        for group in self.conf_servers:
            subgroups = self._getsubgroup(group)
            for role, role_values in self.conf.get(group).items():
                for filepath, filepath_values in role_values.items():
                    for subfile, subfile_values in filepath_values.items():
                        src = subfile  # ansible_sip.conf
                        for subgroup in subgroups:
                            dest_path = self._replacepath(role, subfile_values)
                            dest = os.path.join(self.rootpath, role, filepath, subgroup, dest_path)
                            #dest_dir = os.path.dirname(dest)
                            #for i in os.listdir(dest_dir):
                            #    dest_bak_dir = os.path.join(dest_dir, self.time_dir, os.path.split(i)[0])  # 备份目标的目标目录、
                            #    dest_bak_src = os.path.join(dest_dir,i)  # 备份目标的源文件、
                            #    dest_bak_dest = os.path.join(dest_dir, self.time_dir, i) # 备份目标的目标文件、
                            #    self.mksure_dir(dest_bak_dir)
                            #    if i == 'bak' or self.time - os.lstat(dest_bak_src).st_mtime < self.timeout:
                            #        continue
                            #    if self.run and os.path.exists(dest_bak_src):
                            #        shutil.move(dest_bak_src, dest_bak_dest)
                            #    self.wlog('< backup dest > mv %s %s' % (dest_bak_src, dest_bak_dest))  # backup dest 
                            src_abs = os.path.join(self.srcpath, src)
                            if self.run and sub_run and os.path.exists(src_abs):
                                if not os.path.exists(src_abs):
                                    self.wlog('< file not exist > %s' % src_abs)
                                    exit(127)
                                shutil.copy(src_abs, dest)
                                self.wlog('< cp file > cp %s %s' % (src_abs, dest))  # copy

        

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'f:s:', ['baksrc=', 'mycp=', 'back_role=', 'create_role'])
    print(type(opts))
    for i in opts:
        print(i)
#    myexec = ParserBase(filename='filepath.yaml', stdfile='stddir.yaml', timeout=60, run=True, echo=False)
#    myexec.baksrc(sub_run=False)
#    myexec.baksrc(sub_run=False)
#    myexec.mycp(sub_run=False)
#    myexec.mycp(sub_run=True)
#    myexec.back_role(sub_run=False)
#    myexec.back_role(sub_run=False)
#    myexec.create_role(myexec.rootpath, myexec.std, sub_run=False)
#    myexec.create_role(myexec.rootpath, myexec.std, sub_run=False)






