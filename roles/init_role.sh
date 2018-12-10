###################################################################
# File Name: init_role.sh
# Author: jiangtao
# mail: vlan945@163.com
# Created Time: 2018年12月03日 星期一 10时50分27秒
#=============================================================
#!/bin/bash
root_dir="/etc/ansible/roles"
file_name="main.yaml"
pwd_list=(files templates tasks handlers vars defaults meta)

init(){
	for i in ${pwd_list[@]};do
		mkdir -p ${root_dir}/${1}/${i}
		touch ${root_dir}/${1}/${i}/${file_name}
	done
	touch ${root_dir}/${1}/{hosts,${1}.yaml}
	echo -e "\033[42mmkdir ${root_dir}/${1} :\033[0m"
	[ -f "/usr/bin/tree" ] && /usr/bin/tree ${root_dir}/${1} || ls -R ${root_dir}/${1}
}

[ -z "$1" ] && echo -e "\033[32mUsage: $0 role_name\033[0m" && exit
[ -d "${root_dir}/${1}" ] && echo "\033[32m${root_dir}/${1} director is exits."
init "$1"
