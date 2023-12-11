#!/bin/bash

gendir.sh

cat *catalog.dat > cat.dat
cat *classfd.dat > temp.dat
cat *eelke.dat > ev.dat
cat *starlink.dat > sta.dat
cat *oneweb.dat > one.dat

cat ev.dat >> temp.dat
sort temp.dat -n -k 6 > cla.dat


echo Classfd:
residuals -c ~/tle/bulk.tle -d cla.dat
satnames.py cla.dat

echo Catalog:
residuals -c ~/tle/bulk.tle -d cat.dat
satnames.py cat.dat
