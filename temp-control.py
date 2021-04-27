#!/usr/bin/python3 

import subprocess
import pprint
import psutil
import time
from telnetlib import Telnet

# Temp Management Configuration
# Zones defined as dicts
config={
    # Thresholds [ cold, warm, overheat ]
    "thresholds": { "drives":[44,47,50], "cpus":[55, 60, 70] },
    # Max Influence on fans (ie, drives have 0% influence on CPU cooler fans)
    "fan_influence":{ "drives":[0,0,0.6,0.6,0.6,1], "cpus":[1,1,0.4,0.4,0.4,1]},
    # Rate fan speeds change when past thresholds
    "fan_aggression":{"drives":[-0.1,0,0.1,3],"cpus":[-1,0,1,5]},
    # Minimum fan speeds, dynamic values scale between these and 100
    # (zone independant)
    "fan_minimum":[30,30,30,30,30,50]
    }

# Dynamic Cooling rates
cooling_rate={"drives":50.0,"cpus":50.0}

# Get temps for drives and CPUs
def get_temps():
    temps={}

    # Get drive temps from `hddtemp` running as daemon over telnet
    drives_all=[]
    with Telnet('localhost', 7634) as tn:
        drives_all+=str(tn.read_all().decode("ascii", errors="ignore").strip("|") ).split("||")

    # Parse `hddtemp` response into array
    drives={}
    for drive in drives_all:
        data=drive.split("|")
        if ( data[-1] == "C" ):
            drives[data[0]]=int(data[2])

    temps["drives"] = drives
    
    # Get CPU package temps from psutil module
    cpus={}
    sensors=psutil.sensors_temperatures()
    for name, entries in sensors.items():
        if (name == "coretemp"):
            for entry in entries:
                if "Package" in entry.label:
                    cpus[entry.label]=entry.current

    temps["cpus"]=cpus

    return temps

# Check temps to determine threshold range they are in
def check_temps(temps, zone):
    max_state=0
    for name,temp in temps.items():
        if temp > config["thresholds"][zone][2]:
            max_state=3
        elif temp > config["thresholds"][zone][1]:
            max_state=2 if max_state < 2 else max_state
        elif temp > config["thresholds"][zone][0]:
            max_state=1 if max_state < 1 else max_state
    return max_state

# Main cooling feedback loop
while True:
    # Get current temps
    temps=get_temps()

    # Determine cooling rate for zones
    for zone,temp in temps.items():
        # Get range for zone
        temps[zone]["max"]=check_temps(temp,zone)
        # Change fan temp based on threshold
        cooling_rate[zone]+=config["fan_aggression"][zone][temps[zone]["max"]]
        # Bounds limits
        cooling_rate[zone] = cooling_rate[zone] if cooling_rate[zone] > 0 else 0
        cooling_rate[zone] = cooling_rate[zone] if cooling_rate[zone] < 100 else 100

    pprint.pprint(temps)
    pprint.pprint(cooling_rate)

    # Determine fan speeds
    fan_speeds=[]
    for i in range(0, 6):
        speed=0
        # Total speeds for each zone
        for zone,temp in temps.items():
            speed += config["fan_influence"][zone][i]*cooling_rate[zone]
        
        # Map speed from min to 100
        speed=((100.0-config["fan_minimum"][i])/100)*(speed)+config["fan_minimum"][i]
        # Save speed for fan
        fan_speeds.append(speed)
        # Bounds limits
        fan_speeds[i] = fan_speeds[i] if fan_speeds[i] > config["fan_minimum"][i] else config["fan_minimum"][i]

    pprint.pprint(fan_speeds)
    # Set fan speeds on Corsair Commander
    for i in range(0, 6):
        subprocess.call("liquidctl set fan"+str(i+1)+" speed "+str(int(fan_speeds[i])), shell=True)

    # Wait before continuing loop
    time.sleep(1)
