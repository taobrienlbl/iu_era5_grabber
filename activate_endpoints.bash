#!/bin/bash

GLOBUS=/N/slate/obrienta/software/bigred200/miniconda3/bin/globus

NCAR_ID="1e128d3c-852d-11e8-9546-0a6d4e044368"
IURT_ID="b287987e-b433-11e8-8241-0a3b7ca8ce66"

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# login
echo ""
echo "Please follow the instructions below to log in to globus"
$GLOBUS login

# activate NCAR
echo ""
echo "If not already activated, please go to the following url to activate the NCAR RDA endpoint"
$GLOBUS endpoint activate --web $NCAR_ID
read  -n 1 -p "Hit any key to continue" dum

# activate IURT
echo ""
echo "If not already activated, please go to the following url to activate the IURT endpoint"
$GLOBUS endpoint activate --web $IURT_ID
read  -n 1 -p "Hit any key to continue" dum
