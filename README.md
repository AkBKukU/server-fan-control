# server-fan-control
Control fans on my server with a Corsair Commander Pro

This is a rough release meant to act more as a refrence for how to impliment something like this.

## Requirements

 - [liquidctl](https://github.com/liquidctl/liquidctl)
 - [psutil](https://pypi.org/project/psutil/)
 - hddtemp
 
 The script was made for my server which is using a Corsair Commander Pro to manage fan speeds. If you were using different hardware to control your fans, say your motherboard and AHCI, then you could skip liquidctl and modify the `subprocess` line with the command you need to change your fan speeds.

## Setup
This script pulls HDD temps using `hddtemp ` running in daemon mode. Starting it with `hddtemp -d /dev/sd*` will most likely work. It must be running to retrieve HDD temps.

There is a Systemd unit file provided to set it up to run at boot. You will need to modify the paths in it to where you store the script. It's running as a `oneshot` mode but the python script continues to run, so I'm probably not doing it right but so far it's working fine.
