#!/bin/bash

modality="/Users/pabloherrero/Documents/ManHatTan/pyGUI/kivy_multipleAnswer.py"
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
      sleep 1
    done

  BREAK="$(python $modality $lips)"
  #echo "Script output: $BREAK"
  if [[  $BREAK == *"break"*  ]];
  then
    echo "User cancelled: exiting program"
    break
  fi
done
