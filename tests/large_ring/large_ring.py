import os
from os.path import expanduser
import math

################################################# CONFIGURATION ######################################################

dilation = 2
n_nodes = 6

server_node = 1 		# > 1
client_node = 5			# > 1, client_node - server_node should be even



# server node and client node must be separated by even number of links


# Current configuration - server_node runs server, client_node runs client which sends ping to server.
# if server node is even - every other even node runs cmd, every other odd node runs alt_cmd
# if server node is odd - every other even node runs alt_cmd, every other odd node runs cmd

# All even id nodes assigned to cpu 0 or cpu 1
# All odd id nodes assigned to cpu 2 or cpu 3

cmd = "/home/babu3/emane-Timekeeper/lxc-command/routing_table_monitor "
alt_cmd = "/home/babu3/emane-Timekeeper/dilation-code/scripts/print_time"





run_time = 200				# virtual run time (in secs)



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

distance = 0.02
#theta = float(360)/float(n_nodes)

theta = float(2.0*math.pi)/float(n_nodes)

radius = distance/(2*math.sin(theta/2.0))
altitude = 3


radio_IP_addr_start = "10.100.0.0"
node_IP_addr_start = "10.99.0.0"

HOSTS_FILE = "/etc/hosts"



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


server_node_IP = Int2IP(IP2Int(radio_IP_addr_start) + server_node) 
client_node_IP = Int2IP(IP2Int(radio_IP_addr_start) + client_node) 

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

		curr_lattitude = radius*math.cos((i-1)*theta)
		curr_longitude = radius*math.sin((i-1)*theta)
		curr_altitude = altitude

		if i == 1 :
			curr_cmd = home + "/emane-Timekeeper/lxc-command/server 25000 10"
		elif i == n_nodes :
			curr_cmd = home + "/emane-Timekeeper/lxc-command/client node-1 25000 10"
		else :
			curr_cmd = alt_cmd

		if i == server_node :
			curr_cmd = home + "/emane-Timekeeper/lxc-command/server 25000 10 emane0 " + str(client_node_IP) + " " + str(server_node_IP)
			
		elif i == client_node :

			curr_cmd = home + "/emane-Timekeeper/lxc-command/client radio-1 25000 50 emane0 " + str(server_node_IP) + " " + str(client_node_IP)
		else :

			if i % 2 == 1 :
				if server_node % 2 == 0 :
					curr_cmd = alt_cmd
				else :
					curr_cmd = cmd + Int2IP(IP2Int(radio_IP_addr_start) + i)  + " " + str(n_nodes) + " " + str(run_time - 30)
			else :
				if server_node % 2 == 0 :

					curr_cmd = cmd + Int2IP(IP2Int(radio_IP_addr_start) + i)  + " " + str(n_nodes) + " " + str(run_time - 30)				
				else :
					curr_cmd = alt_cmd

		
		curr_line = str(i) + "," + str(curr_lattitude) + "," + str(curr_longitude) + "," + str(curr_altitude) + "," + str(dilation) + "," + curr_cmd + "\n"
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

	



