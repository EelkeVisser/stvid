#!/bin/bash

for f in *unid_m.dat; 
do 
    ln $f unid/$f;     
done

cd unid

for f in *unid_m.dat; 
do 
    if [ "$(wc -l < $f)" -le 1  ]; then
        echo '1'
    else
        echo 
        echo $f
        satfit -d $f -C -o $f.tle
        cat $f.tle
        satfit -d $f -c ~/tle/classfd.tle -I | sort -nr -k 5 > $f.txt
        tail -10 $f.txt
    fi
done

cd ..
