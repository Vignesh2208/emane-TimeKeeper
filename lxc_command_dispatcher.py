#
# File  : lxc_command_dispatcher.py
# 
# Brief : Dispatches commands to lxcs
#
# authors : Vignesh Babu
#

import sys
import os

def send_command_to_node(node_name,cmd) :

	filename = "/tmp/" + node_name
	with open(filename,"w+") as f :
		f.write(cmd)

arg_list = sys.argv


increase = int(arg_list[1])
node_number = int(arg_list[2])
cmd = ""
i = 3
while i < len(arg_list) :
	cmd = cmd + arg_list[i]
	i = i + 1

send_command_to_node("node-" + str(node_number),cmd)
cwd = os.getcwd()
#if increase == 1 :
#	os.system("sudo lxc-attach -n node-" + str(node_number) + " " + cwd + "/lxc-command/routing_table_reader " + str(node_number))
