#!/bin/bash

NEWTIME=$1
CONTINUE=true

while $CONTINUE; do
      for ((c=$NEWTIME; c>=1; c--))
      do
          clear
          printf "\\n\\n\\n\\n"
          echo "$c mins left" | fmt -c
          sleep 60
      done
      
      NEWTIME="$(osascript ~/Documents/autism/countdown/countdownPrompt.scpt 2>&1)"
      if [$NEWTIME -eq ""];
      then
          CONTINUE=false
      fi
done
