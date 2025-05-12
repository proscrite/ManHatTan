#!/bin/bash
manager="/Users/pabloherrero/Documents/ManHatTan/bash_scripts/storeDialogPerformance.sh"
min=$((24 * 60))
rmin=$(( $RANDOM % $min ))
#at -f "$dialog" now+${rmin}min
at -f $manager now+5s
