#!/bin/bash

NEWTIME=$1
CONTINUE=true
CUMDEPTH=0
SHORTREP=0
LONGREP=0

while $CONTINUE; do

  for ((c=$NEWTIME; c>=1; c--))
  do
      clear
      printf "\\n\\n\\n\\n"
      echo "$c mins left" | fmt -c
      sleep 60
  done

  OUTPUT="$(osascript ~/Documents/autism/countdown/countdownPromptSnooze.scpt 2>&1)"
  if [[  $OUTPUT == *"User cancelled"*  ]];
  then
    echo "User cancelled: exiting program"
    break
  fi

  read -r NEWTIME WEIGHT <<< $(awk -F " " '{print $1,$2}' <<< $OUTPUT)
  # Separate using awk the output from osascript and read it into newtime and depth weight.

  OLDTIME=$NEWTIME

  if (($NEWTIME==0));
  then
      CONTINUE=false
  fi

  # Account for snoozes (short time intervals) and warn about 3 consecutive ones
  if (($NEWTIME<30));
  then
    ((SHORTREP+=1))
  else
    ((LONGREP+=1))
  fi

  if ((SHORTREP==3));
  then
    osascript ~/Documents/autism/countdown/stopSnooze.scpt 2>&1
    CONTINUE=false
  fi
done
