#!/usr/bin/python3 

import subprocess
import pprint
import psutil
import time
from telnetlib import Telnet

# Temp Thresholds
# [ nominal, warm, overheat ]
config={
    "thresholds": { "drives":[44,47,50], "cpus":[55, 60, 70] },
    "fan_reliance":{ "drives":[0,0,0.6,0.6,0.6,1], "cpus":[1,1,0.4,0.4,0.4,1]},
    "fan_minimum":[30,30,30,30,30,50],
    "fan_aggression":{"drives":[-0.1,0,0.1,3],"cpus":[-1,0,1,5]}
    }

cooling_rate={"drives":50.0,"cpus":50.0}

def get_temps():
    temps={}

    #result = subprocess.run(['telnet 127.0.0.1 7634'], shell=True, stdout=subprocess.PIPE)
    drives_all=[]
    with Telnet('localhost', 7634) as tn:
        drives_all+=str(tn.read_all().decode("ascii", errors="ignore").strip("|") ).split("||")

    drives={}
    for drive in drives_all:
        data=drive.split("|")
        if ( data[-1] == "C" ):
            drives[data[0]]=int(data[2])

    temps["drives"] = drives

    cpus={}
    sensors=psutil.sensors_temperatures()
    for name, entries in sensors.items():
        if (name == "coretemp"):
            for entry in entries:
                if "Package" in entry.label:
                    cpus[entry.label]=entry.current

    temps["cpus"]=cpus

    return temps

def check_temps(temps, subject):
    max_state=0
    for name,temp in temps.items():
        if temp > config["thresholds"][subject][2]:
            print(name+" is overheating!")
            max_state=3
        elif temp > config["thresholds"][subject][1]:
            print(name+" is warm")
            max_state=2 if max_state < 2 else max_state
        elif temp > config["thresholds"][subject][0]:
            print(name+" is nominal")
            max_state=1 if max_state < 1 else max_state
        else:
            print(name+" is cool!")
    return max_state

count=0;
while True:
    temps=get_temps()
    for name,temp in temps.items():
        temps[name]["max"]=check_temps(temp,name)
        cooling_rate[name]+=config["fan_aggression"][name][temps[name]["max"]]
        cooling_rate[name] = cooling_rate[name] if cooling_rate[name] > 0 else 0
        cooling_rate[name] = cooling_rate[name] if cooling_rate[name] < 100 else 100

    pprint.pprint(temps)
    pprint.pprint(cooling_rate)
    fan_speeds=[]
    for i in range(0, 6):
        speed_drives = config["fan_reliance"]["drives"][i]*cooling_rate["drives"]
        speed_cpus = config["fan_reliance"]["cpus"][i]*cooling_rate["cpus"]
        fan_speeds.append(((100.0-config["fan_minimum"][i])/100)*(speed_drives + speed_cpus)+config["fan_minimum"][i])
        #fan_speeds.append((100.0-config["fan_minimum"][i])*(speed_drives + speed_cpus)+config["fan_minimum"][i])
        fan_speeds[i] = fan_speeds[i] if fan_speeds[i] > config["fan_minimum"][i] else config["fan_minimum"][i]

    pprint.pprint(fan_speeds)
    for i in range(0, 6):
        subprocess.call("liquidctl set fan"+str(i+1)+" speed "+str(int(fan_speeds[i])), shell=True)

    time.sleep(1)
