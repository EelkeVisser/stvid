#!/bin/bash

while true
do

echo "Run acquire"
cd
cd stvid
./acquire.py -c /home/eelke/stvid/configuration.ini
retVal=$?
echo $retVal
if [ $retVal -ne 0 ]; then
    echo "Error"
    break
fi

echo "sleep"
sleep 60

echo "Run EndOfNight"
cd
cd allsky
./scripts/endOfNight.sh 

#echo "tleupdate"
#cd
#cd stvid
#tleupdate

echo "sleep"
sleep 60

done

