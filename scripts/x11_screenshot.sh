#!/bin/bash
if [ $# -eq 0 ]
	then
		echo "Usage: $0 <IP> <DISPLAY>"
		echo "eg: $0 10.10.10.10 0 /outputfolder"
		exit
	else
		IP="$1"
fi

if [ "$2" == "" ]
	then
		DSP="0"
	else
		DSP="$2"
fi

if [ "$3" == "" ]
	then
		OUTFOLDER="/tmp"
	else
		OUTFOLDER="$3"
fi

xwd -root -screen -silent -display $IP:$DSP > $OUTFOLDER/x11screenshot-$IP.xwd

if [ -f $OUTFOLDER/x11screenshot-$IP.xwd ]; then
	convert $OUTFOLDER/x11screenshot-$IP.xwd $OUTFOLDER/x11screenshot-$IP.jpg
	base64 $OUTFOLDER/x11screenshot-$IP.jpg
fi