#!/bin/bash

for f in *unid_m.dat; 
do 
    ln $f unid/$f;     
done

cd unid

for f in *unid_m.dat; 
do 
    echo 
    echo $f
    satfit -d $f -c ~/tle/bulk.tle -I | sort -nr -k 5 > $f.txt
    tail -10 $f.txt
done

cd ..
