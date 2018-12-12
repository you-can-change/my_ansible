###################################################################
# File Name: test.py
# Author: jiangtao
# mail: vlan945@163.com
# Created Time: 2018年12月12日 星期三 11时23分02秒
# Python version: 3.6.5
#=============================================================
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys, getopt

opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
input_file=""
output_file=""
for op, value in opts:
    if op == "-i":
        print(value)
    elif op == "-o":
        print(value)
    elif op == "-h":
        print(value)
        sys.exit()
