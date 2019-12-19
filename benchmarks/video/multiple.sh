#!/bin/bash

for i in 1 2 4 8 16 32 48 56 64 72 96 112
do

	python -m unittest discover --pattern=video*.py > times_$i.log &
	for k in $(seq 1 $i)
	do
   		python -m unittest discover --pattern=video*.py &
		echo "$i $k"
	done
	wait
	rm /tmp/*.mp4
	rm /tmp/*.avi
done
