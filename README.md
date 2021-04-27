# server-fan-control
Control fans on my server with a Corsair Commander Pro

This is a rough release meant to act more as a reference for how to implement
something like this.

## Requirements

 - [liquidctl](https://github.com/liquidctl/liquidctl)
 - [psutil](https://pypi.org/project/psutil/)
 - hddtemp
 
 The script was made for my server which is using a Corsair Commander Pro to
 manage fan speeds. If you were using different hardware to control your fans,
 say your motherboard and AHCI, then you could skip liquidctl and modify the
 `subprocess` line with the command you need to change your fan speeds.

## Setup
This script pulls HDD temps using `hddtemp ` running in daemon mode. The script
launches this as a subprocess before beginning the main cooling loop..

There is a Systemd unit file provided to set it up to run at boot. You will
need to modify the paths in it to where you store the script.
