#!/usr/bin/python3 

import subprocess
import pprint
import psutil
from telnetlib import Telnet

temps={}

#result = subprocess.run(['telnet 127.0.0.1 7634'], shell=True, stdout=subprocess.PIPE)
drives_all=[]
with Telnet('localhost', 7634) as tn:
    drives_all+=str(tn.read_all().decode("ascii", errors="ignore").strip("|") ).split("||")

drives={}
for drive in drives_all:
    data=drive.split("|")
    if ( data[-1] == "C" ):
        drives[data[0]]=data[2]

temps["drives"] = drives

cpus={}
sensors=psutil.sensors_temperatures()
for name, entries in sensors.items():
    if (name == "coretemp"):
        for entry in entries:
            if "Package" in entry.label:
                cpus[entry.label]=entry.current

temps["cpus"]=cpus
#drives=str(result.stdout).split("||")
#pprint.pprint(psutil.sensors_temperatures())
#pprint.pprint(drives[0])


pprint.pprint(temps)

