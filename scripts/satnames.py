#!/usr/bin/env python3
import sys
import os
import subprocess


def main():
    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print("File path {} does not exist. Exiting...".format(filepath))
        sys.exit()
   
    bag_of_words = {}
    with open(filepath) as fp:
        for line in fp:
            words = line.strip().split(' ')
            if(words[0] != ''):
                #print(words[0])
                #os.process()
                #p = subprocess.Popen("tleinfo -n -i " + words[0], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                #for tleline in p.stdout.readlines():
                #    print(words[0] + ' ' )
                #    print(tleline)
                   
                result = subprocess.run(["/home/eelke/sattools/bin/tleinfo", "-n", "-i", words[0]], capture_output=True, text=True, universal_newlines=True)
                #print(result)
                print(words[0] + ' ' + result.stdout.strip('\n'))
                
                #for rline in result.stdout:
                #    print(rline)
                """
                if "stackoverflow-logo.png" in result.stdout:
                    print("You're a fan!")
                else:
                    print("You're not a fan?")
                """
            
            
if __name__ == '__main__':
    main()
