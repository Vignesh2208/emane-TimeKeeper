import os
import subprocess
import commands
import statistics
from statistics import mean
from statistics import stdev
import matplotlib
import matplotlib.pyplot as plt

tk_disabled_dir = os.path.dirname(os.path.realpath(__file__)) +"/../../experiment-data/TimeKeeper_Disabled"
tk_enabled_dir = os.path.dirname(os.path.realpath(__file__)) +"/../../experiment-data/TimeKeeper_Enabled"

def run_command(cmd) :
	return commands.getstatusoutput(cmd)

def replace_spaces_and_colons(dir_name) :
	name = ""
	for c in dir_name :
		if c == " " :
			name = name + "\ "
		elif c == ":" :
			name = name + "\:"
		else :
			name = name + c
	return name

def get_number_of_nodes(dir_name) :
	exp_info_file = dir_name + "/exp-info.txt"
	exp_info_file = "\"" + exp_info_file + "\""
	get_n_nodes_cmd = "grep -nr " +  "\"N_nodes\" " + str(exp_info_file) + " | " + "cut -d \':\' -f 3"
	out = run_command(get_n_nodes_cmd)
	return int(out[1])


def get_number_received_pkts(dir_name) :
	
	search_dir_path = "\"" + dir_name  + "\""
	cmd = "grep -nr " + "\"server received datagram no\" " + search_dir_path + " | tail -1 | cut -d \' \' -f 6" 
	out = run_command(cmd)
	return int(out[1])

def get_number_txmit_pkts(dir_name) :
	
	search_dir_path = "\"" + dir_name  + "\""
	cmd = "grep -nr " + "\"Sent ping message no\" " + search_dir_path + " | tail -1 | cut -d \' \' -f 6" 
	out = run_command(cmd)
	return int(out[1])

def get_avg_txmit_time(dir_name) :
	
	search_dir_path = "\"" + dir_name + "\""
	cmd = "grep -nr " + "\"Avg Transmit time (sec)\" " + search_dir_path + " | tail -1 | cut -d \' \' -f 7" 
	out = run_command(cmd)
	return float(out[1])

def get_stdev_txmit_time(dir_name) :
	
	search_dir_path = "\"" + dir_name + "\""
	cmd = "grep -nr " + "\"Std Dev Transmit time (sec)\" " + search_dir_path + " | tail -1 | cut -d \' \' -f 8" 
	out = run_command(cmd)
	return float(out[1])

def get_tdf_from_path_name(dir_name) :
	pattern = "TDF_"
	idx = dir_name.find(pattern)
	val_idx = idx + len(pattern)
	
	tdf = ""
	i = val_idx
	while i < len(dir_name) and dir_name[i] >= "0" and dir_name[i] <= "9" :
		tdf = tdf + dir_name[i]
		i = i + 1

	return int(tdf)




def get_all_directories(directory_name):
	return [ x[0] for x in os.walk(directory_name) ]


def get_stats(src_dir,timekeeper_enabled=False) :
	
	stats = {}
	stats["topo"] = []
	stats["tdfs"] = []

	for subdir, dirs, files in os.walk(src_dir):
		for dir_name in dirs:
			sub_dir_path = os.path.join(subdir, dir_name)
			if len(get_all_directories(sub_dir_path)) == 1 :

				try:
					n_nodes = get_number_of_nodes(sub_dir_path)
					n_rx_pkts = get_number_received_pkts(sub_dir_path)
					n_tx_pkts = get_number_txmit_pkts(sub_dir_path)
					if n_tx_pkts < n_rx_pkts :
						n_tx_pkts = n_rx_pkts
					avg_tx_time = get_avg_txmit_time(sub_dir_path)
					stdev_tx_time = get_stdev_txmit_time(sub_dir_path)
					if timekeeper_enabled == True :
						tdf = get_tdf_from_path_name(sub_dir_path)
				except:
					print "Exception in File: ", sub_dir_path
					continue

				throughput = float(n_rx_pkts)*100.0/float(n_tx_pkts)

				if n_nodes not in stats.keys() :
					stats[n_nodes] = {}
					stats["topo"].append(n_nodes)
					stats["topo"] = sorted(stats["topo"])

					if timekeeper_enabled == False :
						stats[n_nodes]["throughput"] = []
						stats[n_nodes]["avg_delay"] = []
						stats[n_nodes]["std_delay"] = []
						stats[n_nodes]["throughput"].append(throughput)
						stats[n_nodes]["avg_delay"].append(avg_tx_time)
						stats[n_nodes]["std_delay"].append(stdev_tx_time)

				elif timekeeper_enabled == False :
					stats[n_nodes]["throughput"].append(throughput)
					stats[n_nodes]["avg_delay"].append(avg_tx_time)
					stats[n_nodes]["std_delay"].append(stdev_tx_time)

					
					
				
				if timekeeper_enabled == True :
					if tdf not in stats["tdfs"] :
						stats["tdfs"].append(tdf)
						stats["tdfs"] = sorted(stats["tdfs"])

					if tdf not in stats[n_nodes].keys() :
						stats[n_nodes][tdf] = {}
						stats[n_nodes][tdf]["throughput"] = []
						stats[n_nodes][tdf]["avg_delay"] = []
						stats[n_nodes][tdf]["std_delay"] = []
						stats[n_nodes][tdf]["throughput"].append(throughput)
						stats[n_nodes][tdf]["avg_delay"].append(avg_tx_time)
						stats[n_nodes][tdf]["std_delay"].append(stdev_tx_time)
					else :
						stats[n_nodes][tdf]["throughput"].append(throughput)
						stats[n_nodes][tdf]["avg_delay"].append(avg_tx_time)
						stats[n_nodes][tdf]["std_delay"].append(stdev_tx_time)
			

	return stats


def plot_stats(stats_enabled, stats_disabled) :
	topo_sizes = stats_enabled["topo"]

	throughput = {}
	delay = {}
	throughput_err = {}
	delay_err = {}
	valid_tdfs = []

	line_styles = ['-.', '--', '-', ':']
	marker = ['o', '+', '^', '<', '>']
	
	matplotlib.rcParams.update({'font.size':15})

	

	if "D" not in throughput.keys() :
		throughput["D"] = []
		throughput_err["D"] = []
		delay["D"] = []
		delay_err["D"] = []
		valid_tdfs.append("D")
	
	for tdf in stats_enabled["tdfs"] :
		is_present = 0
		for size in topo_sizes :
			if tdf in stats_enabled[size].keys() :
				is_present = is_present + 1
		if is_present == len(topo_sizes) :
			valid_tdfs.append(tdf)
			throughput[tdf] = []
			throughput_err[tdf] = []
			delay[tdf] = []
			delay_err[tdf] = []
				

	for tdf in valid_tdfs :
		for size in topo_sizes :
			if tdf == "D" :
				throughput[tdf].append(mean(stats_disabled[size]["throughput"]))
				if len(stats_disabled[size]["throughput"]) == 1 :
					throughput_err[tdf].append(0.0)
				else:
					throughput_err[tdf].append(stdev(stats_disabled[size]["throughput"]))
				delay[tdf].append(mean(stats_disabled[size]["avg_delay"]))
				delay_err[tdf].append(min(stats_disabled[size]["std_delay"]))
			else :
				throughput[tdf].append(mean(stats_enabled[size][tdf]["throughput"]))
				if len(stats_enabled[size][tdf]["throughput"]) == 1 :
					throughput_err[tdf].append(0.0)
				else:
					throughput_err[tdf].append(stdev(stats_enabled[size][tdf]["throughput"]))
				delay[tdf].append(mean(stats_enabled[size][tdf]["avg_delay"]))
				delay_err[tdf].append(min(stats_enabled[size][tdf]["std_delay"]))

				
	print valid_tdfs
	if len(valid_tdfs) > 0 :
		plt.figure()
		i = 0		
		for tdf in valid_tdfs :
			if tdf == "D" :
				label = "Best Effort"
			else :
				label = "TDF = " + str(tdf)
			
			style = line_styles[i % len(line_styles)]
			mark = marker[i % len(marker)]
				
			plt.errorbar(x=topo_sizes,y=throughput[tdf],xerr=0, yerr=throughput_err[tdf],label=label,linestyle=style, marker=mark, linewidth=2)
			
			i = i + 1
			
		plt.title("Observed Throughput vs Topology Size")
		plt.legend(loc='best')
		plt.xlabel("Number of Nodes")
		plt.ylabel("Throughput (%)")
		plt.show()
		
		plt.figure()
		i = 0		
		for tdf in valid_tdfs :
			if tdf == "D" :
				label = "Best Effort"
			else :
				label = "TDF = " + str(tdf)
				
			style = line_styles[i % len(line_styles)]
			mark = marker[i % len(marker)]
			plt.errorbar(x=topo_sizes,y=delay[tdf],xerr=0, yerr=delay_err[tdf],label=label,linestyle=style, marker=mark, linewidth=2)
			i = i + 1
		plt.title("End To End Packet Transmission time")
		plt.legend(loc='best')
		plt.xlabel("Number of Nodes")
		plt.ylabel("Latency (sec)")
		plt.show()
					
	

timekeeper_disabled_stats = get_stats(tk_disabled_dir,False)
timekeeper_enabled_stats = get_stats(tk_enabled_dir,True)
plot_stats(timekeeper_enabled_stats,timekeeper_disabled_stats)		



		
		
