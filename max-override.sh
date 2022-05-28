#!/bin/bash

systemctl stop temp-control

for i in {1..6}
do	
	liquidctl set fan$i speed 100
done

read -p "Press Enter to go back to normal..."

systemctl start temp-control

