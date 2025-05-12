#!/bin/bash

NEWTIME=$1
CONTINUE=true
CUMDEPTH=0

while $CONTINUE; do
  OLDTIME=$NEWTIME

  for ((c=$NEWTIME; c>=1; c--))
  do
      #clear
      printf "\\n\\n\\n\\n"
      echo "$c mins left" | fmt -c
      sleep 5
  done

  OUTPUT="$(osascript ~/Documents/autism/countdown/countdownPromptV2.scpt 2>&1)"
  read -r NEWTIME WEIGHT <<< $(awk -F " " '{print $1,$2}' <<< $OUTPUT)
  # Separate using awk the output from osascript and read it into newtime and depth weight.

  echo "OUTPUT = $OUTPUT"
  echo "NEWTIME = $NEWTIME"
  echo "WEIGHT = $WEIGHT"
  echo "OLDTIME = $OLDTIME"


  CUMDEPTH=$(echo $CUMDEPTH + $OLDTIME*$WEIGHT | bc)
  # Compute cumulative depth time in the session multiplying OLDTIME by WEIGHT
  echo "CUMDEPTH = $CUMDEPTH"

  if [$NEWTIME -eq ""];
  then
      CONTINUE=false
  fi
done
echo "You accumulated $CUMDEPTH deep minutes, congratulations!"
