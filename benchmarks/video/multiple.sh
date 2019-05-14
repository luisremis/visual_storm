#!/bin/bash

vdms 2> log.log &

wait 1

for i in {1..100}
do

	python -m unittest discover --pattern=video*.py > times_$i.log &
	for k in $(seq 1 $i)
	do
   		python -m unittest discover --pattern=video*.py &
		echo "$i $k"
	done
	wait
	sudo pkill vdms
	rm /tmp/*.mp4
	rm /tmp/*.avi
done
