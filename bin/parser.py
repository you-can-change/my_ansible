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
    def __init__(self, filename='filepath.yaml'):
        with open(filename, 'r') as f:
            self.conf = yaml.load(f)
        self.conf_servers = {i for i in self.conf}
        self.groups = {'newivrservers', 'oldivrservers', 'ivrservers', 'assignservers', 'agentservers', 'pbxservers'}
        self.roles = {'pbx', 'cti', 'agi', 'crond'}
        self.rootpath = '/etc/ansible/roles'
        self.srcpath='/etc/ansible/bin/src'

    def mycp(self):
        file_list = []
        time_dir = "bak/%s_%s/" % (time.strftime('%Y%m%d_%H%M'), os.getpid())
        if not os.path.isdir(time_dir):
            os.makedirs(os.path.join(self.srcpath, time_dir))
        if bool(self.conf_servers - self.groups):
            print(self.conf_servers - self.groups)
            exit(222)

        for group in self.conf_servers:
            print(group)
            if group == 'pbxservers':
                subgroups = ['newivrservers', 'oldivrservers', 'assignservers', 'agentservers']
            elif group == 'ivrservers':
                subgroups = ['newivrservers', 'oldivrservers']
            else:
                subgroups = [group, ]

            for role, role_values in self.conf.get(group).items():
                for filepath, filepath_values in role_values.items():
                    for subfile, subfile_values in filepath_values.items():
                        src = subfile
                        for subgroup in subgroups:
                            if role == 'pbx':
                                dest_path = subfile_values.replace('/data/justcall/pbx/', '')
                            elif role == 'cti':
                                dest_path = subfile_values.replace('/data/justcall/just_cti_server/', '')
                            elif role == 'agi':
                                dest_path = subfile_values.replace('/data/justcall/justagi/', '')
                            elif role == 'crond':
                                if subfile_values.replace('/data/justcall/crontab/', '') == subfile_values:
                                    dest_path = subfile_values.replace('/data/public/crontab/', '')
                                else:
                                    dest_path = subfile_values.replace('/data/justcall/crontab/', '')

                            dest = os.path.join(self.rootpath, role, filepath, subgroup, dest_path)
                            dest_dir = os.path.dirname(dest)
                            for i in os.listdir(dest_dir):
                                if i == 'bak': continue
                                if not os.path.isdir(os.path.join(dest_dir, time_dir, os.path.split(i)[0])):
                                  os.makedirs(os.path.join(dest_dir, time_dir, os.path.split(i)[0]))
                                shutil.copy(os.path.join(dest_dir,i), os.path.join(dest_dir, time_dir, i))
                                print('backup dest: mv %s %s' % (os.path.join(dest_dir,i), os.path.join(dest_dir, time_dir, i)))  # backup dest 
                                
                            shutil.copy(os.path.join(self.srcpath, src), dest)
                            print('cp %s %s' % (os.path.join(self.srcpath, src), dest))  # copy

                            if not os.path.isdir(os.path.join(self.srcpath, time_dir, os.path.split(src)[0])):
                                os.makedirs(os.path.join(self.srcpath, time_dir, os.path.split(src)[0]))
                            shutil.move(os.path.join(self.srcpath, src), os.path.join(self.srcpath, time_dir, src))
                            print('backup src: mv %s %s' % (os.path.join(self.srcpath, src), os.path.join(self.srcpath, time_dir, src))) # backup src 


if __name__ == '__main__':
    ParserBase().mycp()
