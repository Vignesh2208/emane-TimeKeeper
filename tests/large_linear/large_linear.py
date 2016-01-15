import os
from os.path import expanduser
import math
import sys

################################################# CONFIGURATION ######################################################

dilation = 1
n_nodes = 41			# Converted to nearest odd number

if n_nodes % 2 == 0 :
	n_nodes = n_nodes + 1

alt_cmd = "/home/vignesh/Desktop/emane-Timekeeper/lxc-command/routing_table_monitor "

cmd = "sudo nice -n -20 su -c /home/vignesh/Desktop/emane-Timekeeper/dilation-code/scripts/print_time"

#alt_cmd = "echo NoCommand"
#cmd = "echo NoCommand"

# Current configuration - node-1 runs server, last node runs client which sends ping to server.
# Every other even id node runs cmd defined in variable cmd.
# Every other odd id node runs cmd defined in variable alt_cmd

# All even id nodes assigned to cpu 0 or cpu 1
# All odd id nodes assigned to cpu 2 or cpu 3


run_time = 200				# virtual run time (in secs)
routing_monitor_run_time = 150


config = """otamanagerdevice		=	eth1
otamanagergroup			=	224.1.2.4:45702
otamanagerttl			=	1
otamanagerloopback		=	false
eventmanagerdevice		= 	eth1
eventmanagergroup		=	224.1.2.4:45703
eventmanagerttl			=	1
antennaprofilemanifesturi	=
transportdef			=	transvirtual
macdef				=	ieee80211abgmac
phydef				=	universalphy
bandwidth			=	1000000
min_pkt_size			=	1200
n_nodes				=	"""  + str(n_nodes) + "\n" + "run_time			= 	" + str(run_time) + "\n"


################################################# CONFIGURATION ######################################################

home = expanduser("~")
#home = os.getcwd()

lattitude = 40.0310751857906
longitude_start = -74.5235179912516
altitude = 3
longitude_increment = -0.01

radio_IP_addr_start = "10.100.0.0"
node_IP_addr_start = "10.99.0.0"
msg_send_timeout = 1000000


HOSTS_FILE = "/etc/hosts"

arg_list = sys.argv
if len(arg_list) > 1 :
	dilation = int(arg_list[1])

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

	while i <= n_nodes :		

		if i == 1 :
			curr_cmd = home + "/Desktop/emane-Timekeeper/lxc-command/server 25000 1000 emane0 " + str(client_node_IP) + " " + str(server_node_IP)
			curr_dilation = 1
			curr_dilation = dilation
			
		elif i == n_nodes :
			curr_cmd = home + "/Desktop/emane-Timekeeper/lxc-command/client radio-1 25000 1000 emane0 " + str(server_node_IP) + " " + str(client_node_IP) + " " + str(msg_send_timeout)
			curr_dilation = 1
			curr_dilation = dilation
		else :

			if i % 2 == 1 :
				curr_cmd = alt_cmd + Int2IP(IP2Int(radio_IP_addr_start) + i)  + " " + str(n_nodes) + " " + str(routing_monitor_run_time)
				curr_dilation = dilation # was 1
				#curr_dilation = 1 # was 1
			else :
				curr_cmd = cmd				
				curr_dilation = dilation
	
		curr_line = str(i) + "," + str(lattitude) + "," + str(longitude_start + i*longitude_increment) + "," + str(altitude) + "," + str(curr_dilation) + "," + curr_cmd + "\n"

		#if i > 1 :
		#	dist = getDistanceFromLatLonInm(lattitude,(i-1)*longitude_increment,lattitude,i*longitude_increment)
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

	



