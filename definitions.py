#
# File  : definitions.py
# 
# Brief : Resolves some paths prior to compilation
#
# authors : Vignesh Babu
#

import os
import sys


script_path = os.path.dirname(os.path.realpath(__file__))
script_path_list = script_path.split('/')

root_directory = "/"
for entry in script_path_list :
	
	if entry == "emane-Timekeeper" :
		root_directory = root_directory + "emane-Timekeeper"
		break
	else :
		if len(entry) > 0 :
			root_directory = root_directory + entry + "/"


conf_directory = root_directory + "/conf"
tests_directory = root_directory + "/tests"
exp_directory = root_directory + "/experiment-data"


definitions = """
#ifndef __DEFINITIONS_H__
#define __DEFINITIONS_H__


""" 

definitions = definitions + "#define PATH_TO_EXPERIMENT_DATA  " + "\"" + exp_directory + "\"\n"
definitions = definitions + "#define EMANE_TIMEKEEPER_DIR " + "\"" + root_directory + "\"\n"
definitions = definitions + """

#endif /*__DEFINITIONS_H__*/
"""

with open(root_directory + "/definitions.h","w") as  f:
	f.write(definitions)
