import sys
import os
import re
import shutil
from timekeeper_functions import *
import time
from emanesh.events import EventService
from emanesh.events import LocationEvent
from emanesh.events import PathlossEvent
from datetime import datetime
import subprocess
import signal

ENABLE_TIMEKEEPER = 1


platformendpoint_base = 8201
transportendpoint_base = 8301
transport_base_address ="10.100.0.0"

cwd = os.getcwd()
lxc_files_dir = "/tmp/emane/lxc"
experiment_dir = cwd + "/conf/experiment"


conf_file = cwd + "/conf/emane.conf"
node_conf_file = cwd + "/conf/node.conf"
script_interrupted = 0
max_tdf = -1


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

def generate_ARP_table(n_nodes):

	#02:02:00:00:XX:XX
	arp_table = ""
	i = 1
	while i <= n_nodes :
		curr_entry_IP = Int2IP(IP2Int(transport_base_address) + i)
		nemid_hex = str(hex(i))
		nemid_hex = nemid_hex[2:]
		while len(nemid_hex) < 4 :
			nemid_hex = "0" + nemid_hex
		nemid_hex = nemid_hex[0:2] + ":" + nemid_hex[2:]

		curr_entry_mac = "02:02:00:00:" + nemid_hex
		arp_table = arp_table + curr_entry_IP + " " + curr_entry_mac + "\n"
		i = i + 1
		
	with open(experiment_dir + "/arp_table.txt","w") as f :
		f.write(arp_table)


def generate_platformxml(nem_id,otamanagerdevice,otamanagergroup,otamanagerttl,otamanagerloopback,eventmanagerdevice,eventmanagergroup,eventmanagerttl,transportdef,macdef,phydef) :
	platformxmlheader = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE platform SYSTEM "file:///usr/share/emane/dtd/platform.dtd">"""

	platformxml = platformxmlheader
	platformxml = platformxml + \
	"""
<platform> """
	platformxml += \
	"""	
	<param name="otamanagerchannelenable" value="on"/>
	<param name="otamanagerdevice" value=""" + "\"" + otamanagerdevice + "\"/>"

	platformxml += \
	"""
	<param name="otamanagergroup" value=""" + "\"" + otamanagergroup + "\"/>"

	#platformxml += \
	#"""
	#<param name="otamanagerttl" value=""" + "\"" + otamanagerttl + "\"/>"


	#platformxml += \
	#"""
	#<param name="otamanagerloopback" value=""" + "\"" + otamanagerloopback + "\"/>"

	platformxml += \
	"""
	<param name="eventservicegroup" value=""" + "\"" + eventmanagergroup + "\"/>"

	platformxml += \
	"""
	<param name="eventservicedevice" value=""" + "\"" + eventmanagerdevice + "\"/>"

        platformxml += \
        """
        <param name="controlportendpoint" value="0.0.0.0:47000"/>"""

	platformxml += \
	"""
	<nem id=\"""" + str(nem_id) + "\" definition=\"expnem.xml\">" 
    	
	platformxml += \
	"""
		<param name="platformendpoint" value=""" + "\"localhost:" + str(platformendpoint_base) + "\"/>"

	platformxml += \
	"""
		<param name="transportendpoint" value=""" + "\"localhost:" + str(transportendpoint_base) + "\"/>"

	platformxml += \
	"""
		<transport definition=""" + "\"" + transportdef + ".xml\">"

	platformxml += \
	"""
			<param name="address" value=""" + "\"" + str(Int2IP(IP2Int(transport_base_address) + nem_id)) + "\"/>"

	# was 255.255.0.0 before

	platformxml += \
	"""
			<param name="mask" value=""" + "\"255.255.0.0\"/>" 

	platformxml += \
	"""
		</transport>
	</nem>
</platform>
	"""	

	return platformxml

def generate_transportdaemonxml(nem_id,transportdef) :

	transportdaemonheader = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE transportdaemon SYSTEM "file:///usr/share/emane/dtd/transportdaemon.dtd">"""

	transportdaemonxml = transportdaemonheader
	transportdaemonxml += \
	"""
<transportdaemon>
	<instance nemid=""" + "\"" + str(nem_id) + "\">"

	transportdaemonxml += \
	"""
		<param name="platformendpoint" value=""" + "\"localhost:" + str(platformendpoint_base) + "\"/>"

	transportdaemonxml += \
	"""
		<param name="transportendpoint" value=""" + "\"localhost:" + str(transportendpoint_base) + "\"/>"

	transportdaemonxml += \
	"""
		<transport definition=""" + "\"" + transportdef + ".xml\">"

	transportdaemonxml += \
	"""
			<param name="address" value=""" + "\"" + str(Int2IP(IP2Int(transport_base_address) + nem_id)) + "\"/>"

	# was 255.255.0.0 before

	transportdaemonxml += \
	"""
			<param name="mask" value=""" + "\"255.255.0.0\"/>" 
	

	transportdaemonxml += \
	"""
		</transport>
	</instance>
</transportdaemon>
	"""	
	return transportdaemonxml

def generate_expnemxml(transportdef,macdef,phydef) :
	expnemxmlheader = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nem SYSTEM "file:///usr/share/emane/dtd/nem.dtd">"""

	expnemxml = expnemxmlheader
	expnemxml += \
	"""
<nem name="EXP NEM">
	<mac definition=""" + "\"" + macdef + ".xml\"/>"
	expnemxml += \
	"""
	<phy definition=""" + "\""+ phydef + ".xml\"/>"
	expnemxml += \
	"""
	<transport definition=""" + "\""+ transportdef + ".xml\"/>"
	expnemxml += \
	"""
</nem>
	"""
	return expnemxml

def generate_deploymentxml(n_nodes) :

	deploymentxmlheader = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE deployment SYSTEM "file:///usr/share/emane/dtd/deployment.dtd">\n
"""
	deploymentxml = deploymentxmlheader
	deploymentxml += "<deployment>"
	
	
	nem_id = 1
	while nem_id <= n_nodes :
		
		deploymentxml += \
		"""
	<platform id=""" + "\"" + str(nem_id) +  "\">"

		deploymentxml += \
		"""
		<nem id=""" + "\"" + str(nem_id) +  "\"/>"
		deploymentxml += \
		"""
	</platform>
		"""
		nem_id += 1
	deploymentxml += "</deployment>"
	return deploymentxml

def generate_gpsdlocationxml(nemid) :

	gpsdlocationxmlheader = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE eventagent SYSTEM "file:///usr/share/emane/dtd/eventagent.dtd">"""

	gpsdlocationxml = gpsdlocationxmlheader
	gpsdlocationxml += \
	"""
<eventagent name="gpsdlocationagent" library="gpsdlocationagent">
	<param name="gpsdconnectionenabled" value="no"/>
	<param name="pseudoterminalfile" value="/tmp/emane/lxc/""" + str(nemid) + """/var/lib/gps.pty\"/>
</eventagent>
	"""
	return gpsdlocationxml

def generate_eventdaemonxml(nemid, eventmanagergroup, eventmanagerdevice) :

	eventdaemonxmlheader = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE eventdaemon SYSTEM "file:///usr/share/emane/dtd/eventdaemon.dtd">
"""

	eventdaemonxml = eventdaemonxmlheader
	eventdaemonxml += \
	"""
<eventdaemon name="EMANE Event Daemon """ +  str(nemid) + """\" nemid = \"""" + str(nemid) + """\">"""
	eventdaemonxml += \
	"""
	<param name="eventservicegroup" value=\"""" + str(eventmanagergroup) + """\"/>"""
	eventdaemonxml +=\
	"""
	<param name="eventservicedevice" value=\"""" + str(eventmanagerdevice) + """\"/>"""
	eventdaemonxml += \
	"""
	<agent definition="gpsdlocationagent""" + str(nemid) + """.xml\"/>"""
	eventdaemonxml += \
	"""
</eventdaemon>
	"""
	
	return eventdaemonxml

def generate_emulationscriptgeneratorxml(experiment_dir)  :
	emulationscriptgeneratorxml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE eventgenerator SYSTEM "file:///usr/share/emane/dtd/eventgenerator.dtd">
<eventgenerator library="emulationscriptgenerator">"""

	emulationscriptgeneratorxml +=\
	"""
	<param name="inputfile" value=\"""" + experiment_dir + """/location.xml\"/>"""
	emulationscriptgeneratorxml += \
	"""
	<param name="repeatcount" value="0"/>
	<param name="schemalocation" value="file:///usr/share/doc/emane-gen-emulationscript/EmulationScriptSchema.xsd"/> 
</eventgenerator>"""

	# there was a 0.8.1 here
	return emulationscriptgeneratorxml

def generate_eventservicexml(eventservicegroup) :

	eventservicexml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE eventservice SYSTEM "file:///usr/share/emane/dtd/eventservice.dtd">
<eventservice>"""

	eventservicexml += \
"""
	<param name="eventservicegroup" value=\"""" + eventservicegroup + """\"/>
	<param name="eventservicedevice" value="br0"/>
	<generator name="Emulation Script Generator" definition="emulationscriptgenerator.xml"/>
</eventservice>"""

	return eventservicexml

def write_files(nemid,dest_dir,platformxml,transportdaemonxml,eventdaemonxml,gpsdlocationxml) :

	with open(dest_dir + "/platform" + str(nemid) +".xml","w+") as f :
		f.write(platformxml)

	with open(dest_dir + "/transportdaemon" + str(nemid) +".xml","w+") as f :
		f.write(transportdaemonxml)

	with open(dest_dir + "/eventdaemon" + str(nemid) +".xml","w+") as f :
		f.write(eventdaemonxml)

	with open(dest_dir + "/gpsdlocationagent" + str(nemid) +".xml","w+") as f :
		f.write(gpsdlocationxml)
	
def ERROR(msg,log=False) :
	print msg
	if log == True :
		pass
	sys.exit(-1)


def validate_params(otamanagerdevice,otamanagergroup,otamanagerttl,otamanagerloopback,eventmanagerdevice,eventmanagergroup,eventmanagerttl,transportdef,macdef,phydef):

	regexp_otamanagerdevice = r'[a-z]+[0-9]*$'
	regexp_otamanagergroup = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):[0-9]{5}$'
	regexp_otamanagerttl = r'[1-9]+$'
	regexp_otamanagerloopback = r'[Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee]$'
	regexp_eventmanagerdevice = r'[a-z]+[0-9]*$'
	regexp_eventmanagergroup = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):[0-9]{5}$'
	regexp_eventmanagerttl = r'[1-9]+$'
	regexp_transportdef = r'\w+$'
	regexp_macdef = r'\w+$'
	regexp_phydef = r'\w+$'

	searchobj =  re.search(regexp_otamanagerdevice, otamanagerdevice)
	if searchobj is None :
		ERROR("Improper format Otamanager device %s" %otamanagerdevice)

	searchobj =  re.search(regexp_otamanagergroup, otamanagergroup)
	if searchobj is None :
		ERROR("Improper format Otamanager Group %s" %otamanagergroup)


	searchobj =  re.search(regexp_otamanagerttl, otamanagerttl)
	if searchobj is None :
		ERROR("Improper format Otamanager ttl %s" %otamanagerttl)

	searchobj =  re.search(regexp_otamanagerloopback, otamanagerloopback)
	if searchobj is None :
		ERROR("Improper format Otamanager loopback %s" %otamanagerloopback)

	searchobj =  re.search(regexp_eventmanagerdevice, eventmanagerdevice)
	if searchobj is None :
		ERROR("Improper format Eventmanager device %s" %eventmanagerdevice)

	searchobj =  re.search(regexp_eventmanagergroup, eventmanagergroup)
	if searchobj is None :
		ERROR("Improper format Eventmanager group %s" %eventmanagergroup)


	searchobj =  re.search(regexp_eventmanagerttl, eventmanagerttl)
	if searchobj is None :
		ERROR("Improper format Eventmanager ttl %s" %eventmanagerttl)		


	searchobj =  re.search(regexp_transportdef, transportdef)
	if searchobj is None :
		ERROR("Improper format Transport Definition %s" %transportdef)		


	searchobj =  re.search(regexp_macdef, macdef)
	if searchobj is None :
		ERROR("Improper format Mac Definition %s" %macdef)		


	searchobj =  re.search(regexp_phydef, phydef)
	if searchobj is None :
		ERROR("Improper format Phy Definition %s" %phydef)		

def configure() :

	global conf_file
	global node_conf_file
	global ENABLE_TIMEKEEPER

	# dictionary containing each node's configuration read from node.conf
	Node= {}
	with open(conf_file) as f :
		content = f.readlines()
		for line in content :
			
			param_list = line.split("=")
			param_name = param_list[0].strip(' \t\n\r')
			if len(param_list) == 1 :
				param_value = None
			else :
				param_value = param_list[1].strip(' \t\n\r')
				if len(param_value) == 0 :
					param_value = None
		
			"""
				Valid params
	
				otamanagerdevice		:		<NONE>
				otamanagergroup			:		<NONE>
				otamanagerttl			:		1
				otamanagerloopback		:		FALSE
				eventmanagerdevice		:		<NONE> 
				eventmanagergroup		:		<REQUIRED>
				eventmanagerttl			:		1		
				antennaprofilemanifesturi	:		<NONE>
				transportdef			:		<NONE>
				macdef				:		<NONE>
				phydef				:		<NONE>
				bandwidth			:		1000000
				min_pkt_size			:		1024

			"""


			if param_name == "otamanagerdevice" :
				if not param_value == None :
					otamanagerdevice = param_value
				else :
					otamanagerdevice = "eth0"
	
			elif param_name == "otamanagergroup" :
				if not param_value == None :
					otamanagergroup = param_value 
				else :
					otamanagergroup = "224.1.2.4:45702"
				
			elif param_name == "otamanagerttl" :
				if not param_value == None :
					otamanagerttl = param_value
				else :
					otamanagerttl = "1"
	
			elif param_name == "otamanagerloopback" :
				if not param_value == None :
					otamanagerloopback = param_value
				else :
					otamanagerloopback = "false"
		
			elif param_name == "eventmanagerdevice" :
				if not param_value == None :
					eventmanagerdevice = param_value
				else :
					eventmanagerdevice = "eth0"
	
			elif param_name == "eventmanagergroup" :
				if not param_value == None :
					eventmanagergroup = param_value 
				else :
					eventmanagergroup = "224.1.2.4:45703"
			
			elif param_name == "eventmanagerttl" :
				if not param_value == None :
					eventmanagerttl = param_value
				else :
					otamanagerttl = "1"
	
			elif param_name == "antennaprofilemanifesturi" :
				if not param_value == None :
					antennaprofilemanifesturi = param_value
				else :
					antennaprofilemanifesturi = None
	
			elif param_name == "transportdef" :
				if not param_value == None :
					transportdef = param_value
				else :
					transportdef = "transvirtual"
	
			elif param_name == "macdef" :
				if not param_value == None :
					macdef = param_value
				else :
					macdef = "rfpipe"
	
			elif param_name == "phydef" :
				if not param_value == None :
					phydef = param_value
				else :
					phydef = "universalphy"
	
			elif param_name == "n_nodes":
				if not param_value == None :
					n_nodes = int(param_value)
				else :
					n_nodes = 10
			elif param_name == "run_time" :
				if not param_value == None:
					run_time = float(param_value)
				else :
					run_time = 1.0 		# 1 secs
			elif param_name == "bandwidth" :
				if not param_value == None:
					bandwidth = float(param_value)
				else :
					bandwidth = 1000000.0

			elif param_name == "min_pkt_size" :
				if not param_value == None:
					min_pkt_size = int(param_value)
				else :
					min_pkt_size = 1024
			

			else :
				print "Unrecognized parameter: ", param_name
				sys.exit(-1)
	
	timeslice = int((min_pkt_size*8/bandwidth)*1000000000)

	print "Timeslice value = ", timeslice
	if timeslice < 10000000 :
		print "Warning. Computed Timeslice value < 10ms. Force setting it to 10ms. Could increase propagation delay error"
		timeslice = 10000000

	validate_params(otamanagerdevice,otamanagergroup,otamanagerttl,otamanagerloopback,eventmanagerdevice,eventmanagergroup,eventmanagerttl,transportdef,macdef,phydef)
	transport_base_address_int = IP2Int(transport_base_address)

	# Clean up the experiment-conf directory
	for the_file in os.listdir(cwd + "/conf/experiment"):
		file_path = os.path.join(cwd + "/conf/experiment", the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path): 
				shutil.rmtree(file_path)
		except Exception, e:
        		print e

	# Clean up /tmp/emane/lxc directory
	if os.path.isdir(lxc_files_dir) == True :

		for the_file in os.listdir(lxc_files_dir):
			file_path = os.path.join(lxc_files_dir, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path): 
					shutil.rmtree(file_path)
			except Exception, e:
				print e

	# Clean up experiment-data directory
	if os.path.isdir(cwd + "/experiment-data") == True :
		for the_file in os.listdir(cwd + "/experiment-data"):
			file_path = os.path.join(cwd + "/experiment-data", the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path): 
					pass
			except Exception, e:
				print e

	transportdef_file = cwd + "/conf/models/"+ transportdef + ".xml"
	macdef_file = cwd + "/conf/models/"+ macdef + ".xml"
	phydef_file = cwd + "/conf/models/" + phydef + ".xml"

	if not os.path.isfile(transportdef_file) :
		ERROR("Transport definition file does not exist")
	else :
		shutil.copy(transportdef_file, cwd + "/conf/experiment")

	if not os.path.isfile(macdef_file) :
		ERROR("MAC definition file does not exist")
	else :
		shutil.copy(macdef_file, cwd + "/conf/experiment")


	if not os.path.isfile(phydef_file) :
		ERROR("Phyisical layer definition file does not exist")
	else :
		shutil.copy(phydef_file, cwd + "/conf/experiment")


	# Generate deploymentxml
	deploymentxml = generate_deploymentxml(n_nodes) # For use by event generators.
	# Generate expnemxml
	expnemxml = generate_expnemxml(transportdef,macdef,phydef)
	# Generate emulationscriptgeneratorxml
	emulationscriptgeneratorxml = generate_emulationscriptgeneratorxml(experiment_dir)
	# Generate eventservicexml
	eventservicexml = generate_eventservicexml(eventmanagergroup)


	# write deploymentxml and expnemxml into experiment directory
	#with open(experiment_dir + "/deployment.xml","w+") as f :
	#	f.write(deploymentxml)

	with open(experiment_dir + "/expnem.xml","w+") as f :
		f.write(expnemxml)

	#with open(experiment_dir + "/emulationscriptgenerator.xml","w+") as f :
	#	f.write(emulationscriptgeneratorxml)

	#with open(experiment_dir + "/eventservice.xml","w+") as f :
	#	f.write(eventservicexml)
	
	nem_id = 1
	while nem_id <= n_nodes :

		# Generate platform.xml
		platformxml = generate_platformxml(nem_id,otamanagerdevice,otamanagergroup,otamanagerttl,otamanagerloopback,eventmanagerdevice,eventmanagergroup,eventmanagerttl,transportdef,macdef,phydef)
		# Generate transportdaemonxml
		transportdaemonxml = generate_transportdaemonxml(nem_id,transportdef)
		
		# Generate evendaemonxml
		eventdaemonxml = generate_eventdaemonxml(nem_id, eventmanagergroup, eventmanagerdevice)
		# Generate gpsdlocationxml
		gpsdlocationxml = generate_gpsdlocationxml(nem_id)

		write_files(nem_id,experiment_dir,platformxml,transportdaemonxml,eventdaemonxml,gpsdlocationxml)
	
		nem_id += 1    


	# Node configurations
	try :
		lines = [line.rstrip('\n') for line in open(node_conf_file)]
	except IOError :
		ERROR("Could not open node.conf file")
	locationxml = 	\
"""<?xml version="1.0" encoding="UTF-8"?>
<EmulationScript xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="file:///usr/share/doc/emane-gen-emulationscript-0.5.3/EmulationScriptSchema.xsd">
	<Event>
	<time>0</time>
	"""
	# there was a 0.5.3 here

	line_no = 0
	for line in lines :
		line_no += 1
		if line.startswith("#") :
			continue
		
		params = line.split(",")
		if len(params) != 6 :
			ERROR("Node conf parser: Invalid number of configurations. Line_no %s" %line_no)
		try:
			node_id = int(params[0])
			if node_id <= 0 or node_id > n_nodes :
				ERROR("Node conf parser: node_id out of bounds. Line_no %s" %line_no)

			lattitude = float(params[1])
			longitude = float(params[2])
			altitude = float(params[3])

			tdf = int(params[4])
			if tdf < 1 :
				ERROR("Node conf parser: tdf must be >= 1. Line_no %s"  %line_no)
 
			cmd = params[5]
			Node[node_id] = {}
			Node[node_id]["lattitude"] = lattitude
			Node[node_id]["longitude"] = longitude
			Node[node_id]["altitude"] = altitude
			Node[node_id]["tdf"] = tdf
			Node[node_id]["cmd"] = cmd

			locationxml += \
		"""
		<Node id=\"""" + str(node_id) + """\">"""
		
			locationxml += \
		"""
			<location>""" + str(lattitude) + "," + str(longitude) + "," + str(altitude) + "</location>" 
			locationxml += \
		"""
		</Node>
		"""
			
		except (RuntimeError, TypeError, NameError) as e:
			print e
			ERROR("Node conf parser: Error at Line_no %s" %line_no)
		
		
	locationxml += \
	"""	</Event>
</EmulationScript>
	"""

	# write locationxml in to the experiment directory
	#with open(experiment_dir + "/location.xml","w+") as f :
	#	f.write(locationxml)


	# Generate routing confs for the olsr routing protocol <experimental>

	routing_template_file = cwd + "/conf/templates/routing.conf.template"
	lxc_node_start_template_file =  cwd + "/conf/templates/lxc-node-start.sh.template"
	lxc_node_stop_template_file = cwd + "/conf/templates/lxc-node-stop.sh.template"
	lxc_init_template_file	= cwd + "/conf/templates/lxc-init.sh.template"

	if ENABLE_TIMEKEEPER == 1 :
		lxc_config_template_file = cwd + "/conf/templates/lxc-config.template.timekeeper"	
	else :
		lxc_config_template_file = cwd + "/conf/templates/lxc-config.template"

	exp_start_file	= cwd + "/conf/templates/exp-start.sh.template"
	exp_stop_file = cwd + "/conf/templates/exp-stop.sh.template"
	PATH_TO_READER = cwd + "/lxc-command/reader " + experiment_dir
	ROUTING_COMMAND = "olsrd -f "
	
	with open(routing_template_file) as f :
		routing_template = f.read()
	
	with open(lxc_node_start_template_file) as f :
		lxc_node_start_template = f.read()

	with open(lxc_init_template_file) as f :
		lxc_init_template = f.read()
	
	with open(lxc_config_template_file) as f:
		lxc_config_template = f.read()
	
	with open(lxc_node_stop_template_file) as f :
		lxc_node_stop_template = f.read()

	with open(exp_start_file) as f :
		exp_start_template = f.read()

	with open(exp_stop_file) as f :
		exp_stop_template = f.read()

	nemid = 1
	while nemid <= n_nodes :
		temp = routing_template
		temp = temp.replace("@NODEID@",str(nemid))
		with open(experiment_dir + "/routing" + str(nemid) + ".conf","w+") as f :
			f.write(temp)
		# create lxc directories
		os.system("mkdir -p " + lxc_files_dir + "/" + str(nemid))
		os.system("mkdir -p " + lxc_files_dir + "/" + str(nemid) + "/var/lib")
		os.system("mkdir -p " + lxc_files_dir + "/" + str(nemid) + "/var/log")
		os.system("mkdir -p " + lxc_files_dir + "/" + str(nemid) + "/var/run")

		temp = lxc_node_start_template
		temp = temp.replace("@NODEID@",str(nemid))
		temp = temp.replace("@LXCNODEROOT@",lxc_files_dir + "/" + str(nemid))

		with open(lxc_files_dir + "/"+ str(nemid) + "/lxc-node-start.sh","w+") as f :
			f.write(temp)

		temp = lxc_init_template
		temp = temp.replace("@EMANEEXPROOT@",experiment_dir)
		temp = temp.replace("@NODEID@",str(nemid))
		temp = temp.replace("@LXCNODEROOT@",lxc_files_dir + "/" + str(nemid))
		temp = temp.replace("@ROUTINGCOMMAND@",ROUTING_COMMAND)

		if len(Node[nemid].keys()) != 0 :
			#temp = temp.replace("@LXC_COMMAND@",Node[nemid]["cmd"] + " " + str(nemid)) # pass nemid as last argument
			temp = temp.replace("@LXC_COMMAND@",PATH_TO_READER)
		else:
			temp = temp.replace("@LXC_COMMAND@","")

		with open(lxc_files_dir + "/"+ str(nemid) + "/init.sh","w+") as f :
			f.write(temp)

		temp = lxc_node_stop_template
		temp = temp.replace("@NODEID@",str(nemid))
	
		with open(lxc_files_dir + "/" + str(nemid) + "/lxc-node-stop.sh","w+") as f :
			f.write(temp)
		

		temp = lxc_config_template
		temp = temp.replace("@NODEIDIP@",str(Int2IP(IP2Int("10.99.0.0") + nemid)))
		temp = temp.replace("@NODEID@",str(nemid))

		if ENABLE_TIMEKEEPER == 0 :
			if nemid % 2 == 0 :
				temp = temp.replace("@CPU1@",str(0))
				temp = temp.replace("@CPU2@",str(1))
			else :
				temp = temp.replace("@CPU1@",str(2))
				temp = temp.replace("@CPU2@",str(3))

		nemid_hex = str(hex(nemid))
		nemid_hex = nemid_hex[2:]
		while len(nemid_hex) < 4 :
			nemid_hex = "0" + nemid_hex
		nemid_hex = nemid_hex[0:2] + ":" + nemid_hex[2:]

		temp = temp.replace("@NODEIDHEX@",nemid_hex)
		temp = temp.replace("@OTAMANAGERDEVICE@",otamanagerdevice)
		
		with open(lxc_files_dir + "/" + str(nemid) + "/config","w+") as f :
			f.write(temp)
		
		temp = exp_start_template
		temp = temp.replace("@EXPERIMENT_DIR@", experiment_dir)

		with open(experiment_dir + "/exp-start.sh","w+") as f :
			f.write(temp)

		temp = exp_stop_template
		temp = temp.replace("@EXPERIMENT_DIR@",experiment_dir)
			
		with open(experiment_dir + "/exp-stop.sh","w+") as f :
			f.write(temp)
		
		nemid += 1

	generate_ARP_table(n_nodes)

	os.system("chmod -R 777 " + experiment_dir)
	os.system("chmod -R 777 " + lxc_files_dir)


	return Node,run_time,n_nodes,eventmanagergroup,timeslice

def send_command_to_node(node_name,cmd) :

	filename = "/tmp/" + node_name
	with open(filename,"w+") as f :
		f.write(cmd)



# call exp_start_script here
def start_LXCs() :
	if ENABLE_TIMEKEEPER == 1 :
		print "Removing Timekeeper module"
		os.system("rmmod " + cwd + "/dilation-code/TimeKeeper.ko")
		time.sleep(1)
		print"Inseting Timekeeper module"
		os.system("insmod " + cwd + "/dilation-code/TimeKeeper.ko")
		time.sleep(1)

	print "Starting LXCs"
	script_path = experiment_dir + "/exp-start.sh"
	os.system(script_path)
	print"LXC's Started"

# call exp_stop_script here
def stop_LXCs(max_tdf = None) :

	global node_conf_file
	global conf_file

	print "Stopping LXCs"
	script_path = experiment_dir + "/exp-stop.sh"
	os.system(script_path)
	time.sleep(2)
	print "LXCs stopped"
	print "Storing Experiment Logs ... "
	
	dt = datetime.now()
	
	exp_name = str(dt)


	if ENABLE_TIMEKEEPER == 1 and max_tdf != None:
		exp_name = "TimeKeeper_Enabled/E_TDF_" + str(max_tdf) + "_Timestamp_" + exp_name
	else :
		exp_name = "TimeKeeper_Disabled/D_Timestamp_" + exp_name

	dest = cwd + "/experiment-data/" + exp_name

	if not os.path.exists(dest):
		os.makedirs(dest)

	if not os.path.exists(dest):
		os.makedirs(dest)

	for the_file in os.listdir(cwd + "/experiment-data"):
		file_path = os.path.join(cwd + "/experiment-data", the_file)
		try:
			if os.path.isfile(file_path):
				shutil.copy(file_path, dest)
				os.unlink(file_path)
			elif os.path.isdir(file_path): 
				pass
		except Exception, e:
			print e
	
	file_path = os.path.join(node_conf_file)
	try:
		if os.path.isfile(file_path):
			shutil.copy(file_path, dest)
			os.unlink(file_path)
		elif os.path.isdir(file_path): 
			pass
	except Exception, e:
		print e

	file_path = os.path.join(conf_file)
	try:
		if os.path.isfile(file_path):
			shutil.copy(file_path, dest)
			os.unlink(file_path)
		elif os.path.isdir(file_path): 
			pass
	except Exception, e:
		print e	

	os.system("chmod -R 777 " + cwd + "/experiment-data")
	

def main():

	global conf_file
	global node_conf_file
	global ENABLE_TIMEKEEPER
	global max_tdf

	if is_root() == 0 :
		print "Must be run as root"
		sys.exit(-1)

	arg_list = sys.argv

	if len(arg_list) == 1 :
		conf_file = cwd + "/conf/emane.conf"
		node_conf_file = cwd + "/conf/node.conf"
	else :
		i = 1
		while i < len(arg_list) :
			if arg_list[i] == "-D" :
				ENABLE_TIMEKEEPER = 0
			else :
				ENABLE_TIMEKEEPER = 1
				conf_files_dir = arg_list[1]
				if os.path.isdir(conf_files_dir) == True :
					conf_file = conf_files_dir + "/emane.conf"
					node_conf_file = conf_files_dir + "/node.conf"
					if os.path.exists(conf_file) == False or os.path.exists(node_conf_file) == False :
						print "Config files do not exist"
						sys.exit(-1)
				else :
					print "Config directory specified is incorrect"
					sys.exit(-1)
			i = i + 1

	Node,run_time,n_nodes,eventmanagergroup,timeslice  = configure()
	# create experiment-data directory

	with open(cwd + "/experiment-data/exp-info.txt","w") as f :
		f.write("Conf file path : " + conf_file + "\n")
		f.write("Node Conf file : " + node_conf_file + "\n")
		f.write("Run time       : " + str(run_time) + "\n")
		f.write("N_nodes        : " + str(n_nodes) + "\n")

	# copy node_config file and emane_conf file


	os.system("mkdir -p " + cwd + "/experiment-data")
	start_LXCs()
	print "Timeslice = ", timeslice
        print "Setting initial location values to all lxcs ..."
	nemid = 1
        temp_list = eventmanagergroup.split(":")
        eventmanagergroupaddress = temp_list[0]
        eventmanagergroupport = int(temp_list[1])
        service = EventService((eventmanagergroupaddress,eventmanagergroupport,'br0'))
        event = LocationEvent()

	i = 1
	
	while i <= n_nodes:
		pathlossevt = PathlossEvent()
		j = 1
		while j <= n_nodes:
			if i != j:
				pathlossevt.append(j,forward=90,reverse=90)
			#service.publish(i,pathlossevt)
			j  = j + 1	
		i = i + 1
		
        
        while nemid <= n_nodes :
            event.append(nemid,latitude=Node[nemid]["lattitude"],longitude=Node[nemid]["longitude"],altitude=Node[nemid]["altitude"])
            nemid = nemid + 1
        service.publish(0,event)

        time.sleep(2)
        print "Location events published. All nodes set to initial positions. Waiting for 25 sec for routing updates to stabilize"
	time.sleep(30)

	# Timekeeper portion
	freeze_quantum = timeslice/2 		  # in nano seconds
	freeze_quantum = freeze_quantum/1000000   # in micro seconds
	nemid = 1
	
	
	
	while nemid <= n_nodes :
		pid = getpidfromname("node-" + str(nemid))
		print "PID of node ",nemid, " = ", pid, " TDF = ", Node[nemid]["tdf"]
		if pid != -1 and ENABLE_TIMEKEEPER == 1:
			dilate_all(pid,Node[nemid]["tdf"])
			addToExp(pid)
		if max_tdf < Node[nemid]["tdf"] :
			max_tdf = Node[nemid]["tdf"]

		nemid += 1

	if ENABLE_TIMEKEEPER == 1 and max_tdf >= 1 :
		set_cbe_experiment_timeslice(freeze_quantum*max_tdf)

	print "Set freeze_quantum = ", freeze_quantum*max_tdf;

	if ENABLE_TIMEKEEPER == 1 :
		if os.path.exists(cwd + "/exp_finished.txt") :
			os.unlink(cwd + "/exp_finished.txt")
		#process = subprocess.Popen(["python","synchronizer.py",str(int(run_time))])
		#print  "Synchronizer pid", process.pid
		#dilate_all(process.pid,max_tdf)
		#addToExp(process.pid)
	

		print "Timekeeper synchronizing ..."
		synchronizeAndFreeze()

	# wait for sometime for the containers to be frozen
	time.sleep(2)
	
	
	# send commands to execute to each LXC
	nemid = 1
	while nemid <= n_nodes :
		if nemid % 2 == 0 :
			process = subprocess.Popen(["python","lxc_command_dispatcher.py",str(0),str(nemid), Node[nemid]["cmd"]])
		else :
			process = subprocess.Popen(["python","lxc_command_dispatcher.py",str(1),str(nemid), Node[nemid]["cmd"]])
		#send_command_to_node("node-" + str(nemid), Node[nemid]["cmd"]) 
		nemid += 1

	# Start Exp
	if ENABLE_TIMEKEEPER == 1 :
		print "Synchronized CBE experiment started ..."
		pid = getpidfromname("node-" + str(1))
		start_time = int(subprocess.check_output([cwd + "/lxc-command/gettimepid", str(pid)]))
		prev_time = start_time
		print "Experiment start time", start_time
		startExp()
	else :
		print "Experiment Started with TimeKeeper disabled - Ignoring TDF settings"

	try :

		k = 0		
		while True :

			if ENABLE_TIMEKEEPER == 1 :
				#if os.path.exists(cwd + "/exp_finished.txt") :
				#	os.unlink(cwd + "/exp_finished.txt")
				
				#	break
				pid = getpidfromname("node-" + str(1))
				curr_time = int(subprocess.check_output([cwd + "/lxc-command/gettimepid", str(pid)]))

				if curr_time - start_time >= run_time :					
					break;
				else :
					if curr_time - prev_time >= 1 :
						k = k + (curr_time - prev_time)
						print k," secs elapsed"
						prev_time = curr_time
						

			else :
				if k >= run_time :
					break
				k= k + 1
			# sleep until runtime expires	
			time.sleep(1)
			
			
				

	except KeyboardInterrupt:
		pass	
	
	# stop Exp
	print "Stopping Synchronized experiment"
	if ENABLE_TIMEKEEPER == 1 :
		stopExp()	
		time.sleep(30)
	
	stop_LXCs(max_tdf)


def interrupt_handler(signum, frame):
	#print "Interrupted. Stopping Experiment!!!"
	global script_interrupted
	global max_tdf
	global ENABLE_TIMEKEEPER
	if script_interrupted == 0 :
		script_interrupted = 1
		print "Interrupted. Stopping Experiment"
		if ENABLE_TIMEKEEPER == 1 :
			stopExp()
			time.sleep(30)

		stop_LXCs(max_tdf)
		sys.exit(0)
		
	



if __name__ == "__main__" :
	signal.signal(signal.SIGINT, interrupt_handler)	
	main()


