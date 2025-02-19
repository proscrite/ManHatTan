#!/bin/bash
dialog="/Users/pabloherrero/Documents/ManHatTan/applescripts/usingBundle.scpt"
pyupdate="/Users/pabloherrero/Documents/ManHatTan/python_scripts/test_update_lipstick.py"
selGota="/Users/pabloherrero/Documents/ManHatTan/applescripts/selectGota.scpt"
#gota="/Users/pabloherrero/Documents/ManHatTan/GOTAs/Die_Verwandlung.got"
gota="$(osascript $selGota 2>^1)"
echo "Practicing vocabulary from book $gota"

min=$((24 * 60))
rmin=$(( $RANDOM % $min ))
#at -f "$dialog" now+${rmin}min
rmin=$1
CONTINUE=true
while $CONTINUE; do

  for ((c=$rmin; c>=1; c--))
  do
      sleep 60
    done

  OUTPUT="$(osascript $dialog $gota)"

  if [[  $OUTPUT == *"User cancelled"*  ]];
  then
    echo "User cancelled: exiting program"
    break
  else
      echo "Output from dialog: $OUTPUT"
      python $pyupdate $gota $OUTPUT
  fi


done
