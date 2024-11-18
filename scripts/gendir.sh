#!/bin/bash

function gendir()
{
mkdir $curdir

cat *$curdir.dat > $curdir/$curdir.dat

for f in *$curdir.png; 
do 
    ln $f $curdir/$f; 
    
    g=${f%%_*}_0.png;
    ln $g $curdir/$g;
    
    g=${f%%_*}.fits;
    ln $g $curdir/$g;
done



for f in *${curdir}_m.dat; 
do 
    ln $f $curdir/$f; 
done

}


curdir='catalog'
gendir
curdir='classfd'
gendir
curdir='unid'
gendir
curdir='eelke'
gendir

