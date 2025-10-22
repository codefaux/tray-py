#!/bin/bash
echo This is the script. Arguments passed to the script were:
echo \' $* \'
echo Entering infinite loop...
while true
do
	echo -n "Still Alive ... "
	sleep 15
done

