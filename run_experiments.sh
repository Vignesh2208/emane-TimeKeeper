#!/bin/bash
#
# File  : run_experiments.sh
# 
# Brief : This script runs the large_linear test several times for different iterations. The user specifies the 
#	  number of iterations for each TDF and the number of TDFs to test/ experiment with.
#
# authors : Vignesh Babu
#


N_iterations=1			# number of iterations for each TDF
TDF_COUNTER=5			# Start TDF
TDF_STEP_SIZE=2			# TDF increment value
MAX_TDF=11			# End TDF of Experiment
i=0
while [ $i -lt $N_iterations ]; do
	while [ $TDF_COUNTER -lt $MAX_TDF ]; do
        	echo The current TDF is $TDF_COUNTER
		cd tests/large_linear 
		sudo python large_linear.py $TDF_COUNTER
		cd ../../; 
		sudo python deploy.py $(pwd)/tests/large_linear
		let TDF_COUNTER=TDF_COUNTER+TDF_STEP_SIZE
	done
	let i=i+1
done

