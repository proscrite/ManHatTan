#!/bin/bash

pygui="/Users/pabloherrero/Documents/ManHatTan/pyGUI/"
selLip="/Users/pabloherrero/Documents/ManHatTan/pyGUI/kivy_select_book.py"

lips="$(python $selLip 2>^1)"
echo "Practicing vocabulary from book $lips"

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

  rnd=$(( $RANDOM % 100 ))
  echo "rnd = $rnd"
  if ((rnd <= 15));
  then
    modality=${pygui}widte.py
    echo "Enter 1st 15 percentile"
  elif ((rnd > 15 && rnd <= 30));
  then
    modality=${pygui}wirte.py
    echo "Enter 2nd 15 percentile"
  elif ((rnd > 30 && rnd <= 60));
  then
    modality=${pygui}madte.py
    echo "Enter 3rd 30 percentile"
  elif ((rnd > 60));
  then
    modality=${pygui}marte.py
  fi

  BREAK="$(python $modality $lips)"
  #echo "Script output: $BREAK"
  if [[  $BREAK == *"break"*  ]];
  then
    echo "User cancelled: exiting program"
    break
  fi
done
