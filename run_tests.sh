#!/bin/bash
#
# File  : run_test.sh
# 
# Brief : This script runs the large_linear test several times for different iterations.
#
# authors : Vignesh Babu
#


####
# Usage sudo ./run_test.sh <options>
# Options:
#	-e=<value>					:	Enable(1) or Disable(0) TimeKeeper 
#	--starttoposize=<value>		: 	Number of nodes in Topology
#	--topoinc=<value>			:	Increment in the number of nodes in the Topology
#	--maxtoposize=<value> 		:	Maximum number of nodes in Topology
#	--starttdf=<value>			:	Start TDF Value. Valid only if TimeKeeper is enabled
#	--tdfinc=<value>			:	TDF increment step size. Valid only if TimeKeeper is enabled
#	--maxtdf=<value>			:	END TDF Value. Valid only if TimeKeeper is enabled.
#	--repeat=<value>			: 	Number of Times to repeat the whole script 
#


# Default Values
enabled=0
repeat=0

starttoposize=11
topoinc=1
maxtoposize=11

starttdf=1
tdfinc=1
maxtdf=1



for i in "$@"
do

case $i in

    -e=*)
    enabled="${i#*=}"
    shift # past argument
    ;;
    
    --starttoposize=*)
    starttoposize="${i#*=}"
    shift # past argument
    ;;
    
    --topoinc=*)
    topoinc="${i#*=}"
    shift # past argument
    ;;

	--maxtoposize=*)
    maxtoposize="${i#*=}"
    shift # past argument
    ;;

	--starttdf=*)
    starttdf="${i#*=}"
    shift # past argument
    ;;

	--tdfinc=*)
    tdfinc="${i#*=}"
    shift # past argument
    ;;
    
	--maxtdf=*)
   	maxtdf="${i#*=}"
    shift # past argument
    ;;

    --repeat=*)
    repeat="${i#*=}"
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

enabled=$(($enabled+0))
starttoposize=$(($starttoposize+0))
topoinc=$(($topoinc+0))
maxtoposize=$(($maxtoposize+0))
starttdf=$(($starttdf+0))
tdfinc=$(($tdfinc+0))
maxtdf=$(($maxtdf+0))
repeat=$(($repeat+0))

#echo "TIMEKEEPER ENABLED		= " $enabled
#echo "TOPOSIZE					= " $starttoposize
#echo "TOPOINC					= "	$topoinc
#echo "MAXTOPOSIZE				= "	$maxtoposize
#echo "STARTTDF					= "	$starttdf
#echo "TDFINC					= "	$tdfinc
#echo "MAXTDF					= "	$maxtdf
#echo "REPEAT					= " $repeat


i=0
while [ $i -le $repeat ]; do
	j=$(($starttoposize+0))
	echo "Current Iteration number = " $i
	while [	$j -le	$maxtoposize ]; do
		k=$((starttdf+0))
		echo "Current Topology Size = " $j	
		if [ $enabled -eq 1 ]; then
			while [ $k -le $maxtdf ]; do
				echo "Current TDF = " $k
				cd tests/large_linear
				sudo python large_linear.py $j $k
				cd ../../;
				sudo python deploy.py $(pwd)/tests/large_linear
				sleep 30
				
				let k=k+tdfinc
			done
		else
			cd tests/large_linear
			sudo python large_linear.py $j
			cd ../../;
			sudo python deploy.py $(pwd)/tests/large_linear -D
			sleep 30
		fi
		
		let j=j+topoinc
	done
	let i=i+1
done

