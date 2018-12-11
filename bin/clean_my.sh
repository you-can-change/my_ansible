###################################################################
# File Name: clean_my.sh
# Author: jiangtao
# mail: vlan945@163.com
# Created Time: 2018年12月11日 星期二 14时29分35秒
#=============================================================
#!/bin/bash
for i in $(grep ansible /etc/ansible/bin/filepath.yaml | awk -F '[ */]' '{print $NF}' );do
	touch /etc/ansible/bin/src/$i;
done
mkdir -p /etc/ansible/bin/src/ytotts/ && mv /etc/ansible/bin/src/*wav /etc/ansible/bin/src/ytotts/
rm -rf /etc/ansible/bin/src/bak/*
find /etc/ansible/roles/*/{files,templates} -name bak | xargs rm -rf
find /etc/ansible/roles/*/{files,templates} -type f | xargs rm -rf
