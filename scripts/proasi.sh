#!/bin/bash
source /home/eelke/.venv/bin/activate

PATH="/home/eelke/sattools:$PATH"
PATH="/home/eelke/stvid:$PATH"
PATH="/home/eelke/hough3d-code:$PATH"

export ST_DATADIR=/home/eelke/sattools
export ST_TLEDIR=/home/eelke/tle
export ST_COSPAR=0794
export ST_LOGIN="identity=eelkevisser@hotmail.com&password=4Y8sQRfjN4GFBq4"
export ST_OBSDIR=/home/eelke/obs

#tleupdate
update_tle.py -c /home/eelke/stvid/configuration.ini

process.py -c /home/eelke/stvid/configuration.ini &
PID=$!
sleep 23h
kill $PID
#read -p "Press enter to continue"
