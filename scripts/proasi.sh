#!/bin/bash
PATH="/home/pi/sattools:$PATH"
PATH="/home/pi/stvid:$PATH"
PATH="/home/pi/hough3d-code:$PATH"

export ST_DATADIR=/home/pi/sattools
export ST_TLEDIR=/home/pi/tle
export ST_COSPAR=0794
export ST_LOGIN="identity=eelkevisser@hotmail.com&password=4Y8sQRfjN4GFBq4"
export ST_OBSDIR=/home/pi/obs

tleupdate

process.py -c /home/pi/stvid/configuration.ini &
PID=$!
sleep 23h
kill $PID
#read -p "Press enter to continue"
