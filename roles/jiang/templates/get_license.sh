#!/bin/bash
/usr/sbin/ntpdate ntp1.aliyun.com && /sbin/hwclock -w 
curl "http://112.74.28.137/getLicence.php?limit_trunk=500&limit_exten=500&limit_employee=500&used_day=99999&hostid=$(/usr/local/Zend/bin/zendid)&cpuid=$(/usr/sbin/dmidecode -t 4 | grep ID | head -1 | sed 's/ //g' |cut -d':' -f2)&checkContent=$(date +%s)&status=1" 2>/dev/null | base64 -d > /etc/justcall/license.zl && /sbin/service httpd restart
