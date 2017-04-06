#
# File  : large_linear.py
# 
# Brief : This script generates a node.conf and emane.conf file for a semi-linear topology where each node can directly talk to three closest neighbour.
#	  The TDF, number of nodes, experiment run time are specified in the configuration section of the script
#
# authors : Vignesh Babu
#



import os
from os.path import expanduser
import math
import sys
script_path = os.path.dirname(os.path.realpath(__file__))
script_path_list = script_path.split('/')

root_directory = "/"
for entry in script_path_list :
	
	if entry == "emane-TimeKeeper" :
		root_directory = root_directory + "emane-TimeKeeper"
		break
	else :
		if len(entry) > 0 :
			root_directory = root_directory + entry + "/"


conf_directory = root_directory + "/conf"
tests_directory = root_directory + "/tests"
cmd_directory  = root_directory + "/lxc-command"



################################################# CONFIGURATION ######################################################

dilation 					= 2
n_nodes 					= 40	
run_time 					= 50					# virtual run time (in secs)
routing_monitor_run_time 	= 150					# used only when routing monitor is run as the alt_cmd

lattitude 					= 40.0310751857906			# lattitude of all nodes in the linear topology
longitude_start 			= -74.5235179912516			# longitude of first node in the topology
altitude 					= 3							# altitude in meters
longitude_increment 		= -0.01						# increment applied to longitude of other nodes. longitude(node_id) = longitude_start + longitude_increment*(node_id - 1)

radio_IP_addr_start 		= "10.100.0.0"				# IP address internally visible to applications/routing protocols
node_IP_addr_start 			= "10.99.0.0"				# IP address used by Emane for broadcasting/unicasting messages
msg_send_timeout 			= 1000000					# periodic msg send timeout used by client

alt_cmd = root_directory + "/dilation-code/scripts/bin/print_time"
cmd = "sudo nice -n -20 su -c " + root_directory + "/dilation-code/scripts/bin/print_time"


# Current configuration - node-1 runs server, last node runs client which sends ping to server.
# Every other even id node runs cmd defined in variable cmd.
# Every other odd id node runs cmd defined in variable alt_cmd


arg_list = sys.argv
if len(arg_list) == 2 :
	n_nodes = int(arg_list[1])
elif len(arg_list) == 3 : 
	n_nodes = int(arg_list[1])
	dilation = int(arg_list[2])
	

config = """otamanagerdevice		=	eth1
otamanagergroup						=	224.1.2.4:45702
otamanagerttl						=	1
otamanagerloopback					=	false
eventmanagerdevice					= 	eth1
eventmanagergroup					=	224.1.2.4:45703
eventmanagerttl						=	1
antennaprofilemanifesturi			=
transportdef						=	transvirtual
macdef								=	rfpipe
phydef								=	universalphy
bandwidth							=	1000000
min_pkt_size						=	1200
n_nodes								=	"""  + str(n_nodes) + "\n" + "run_time			= 	" + str(run_time) + "\n"


################################################# CONFIGURATION ######################################################

home = expanduser("~")
HOSTS_FILE = "/etc/hosts"

	
#if n_nodes % 2 == 0 :
#	n_nodes = n_nodes + 1


def IP2Int(ip):
    o = map(int, ip.split('.'))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res


def Int2IP(ipnum):
    o1 = int(ipnum / 16777216) % 256
    o2 = int(ipnum / 65536) % 256
    o3 = int(ipnum / 256) % 256
    o4 = int(ipnum) % 256
    return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()

def deg2rad(deg) :
   return deg * (math.pi/180)


def getDistanceFromLatLonInm(lat1,lon1,lat2,lon2):
    R = 6371 # Radius of earth
    dLat = deg2rad(lat2-lat1)
    dLon = deg2rad(lon2 - lon1)
    a = math.sin(dLat/2)*math.sin(dLat/2) + math.cos(deg2rad(lat1))*math.cos(deg2rad(lat2))*math.sin(dLon/2)*math.sin(dLon/2)
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    d = R*c # Distance in KM
    print "Distance (meters) = ", d*1000.0
    return d*1000.0

server_node_IP = Int2IP(IP2Int(radio_IP_addr_start) + 1) 
client_node_IP = Int2IP(IP2Int(radio_IP_addr_start) + n_nodes) 



with open("node.conf", "w") as f :
	pass

with open("emane.conf","w") as f :
	pass

with open(HOSTS_FILE,"w") as f :
	pass

hosts_content = ""

with open("temp_hosts","r") as f :
	hosts_content = f.read()

i = 1
with open("node.conf", "a") as f :
	f.write("# Node_ID,	lattitude,		longitude,		altitude,	TDF,		Command <space separated args list>\n")
	while i <= n_nodes :		

		if i == 1 :
			curr_cmd = cmd_directory + "/server 25000 " + str(run_time) +  " emane0 " + str(client_node_IP) + " " + str(server_node_IP)
			curr_dilation = dilation
			
		elif i == n_nodes :
			curr_cmd = cmd_directory + "/client radio-1 25000 " + str(run_time) + " emane0 " + str(server_node_IP) + " " + str(client_node_IP) + " " + str(msg_send_timeout)
			curr_dilation = dilation
		else :

			if i % 2 == 1 :
				curr_cmd = alt_cmd
				curr_dilation = dilation			
			else :
				curr_cmd = cmd				
				curr_dilation = dilation
	
		curr_line = str(i) + ",		" + str(lattitude) + ",		" + str(longitude_start + i*longitude_increment) + ",		" + str(altitude) + ",		" + str(curr_dilation) + ",		" + curr_cmd + "\n"
		f.write(curr_line)
		i = i + 1

with open("emane.conf","a") as f:	
	f.write(config)
	

with open(HOSTS_FILE,"a") as f :
	f.write(hosts_content)
	f.write("\n")
	i = 1
	while i <= n_nodes :
		curr_line = Int2IP(IP2Int(radio_IP_addr_start) + i) + " " + "radio-" + str(i) + "\n"
		f.write(curr_line)
		curr_line = Int2IP(IP2Int(node_IP_addr_start) + i) + " " + "node-" + str(i) + "\n"
		f.write(curr_line)
		i = i + 1

	



