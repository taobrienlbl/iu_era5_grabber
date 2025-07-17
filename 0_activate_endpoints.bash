#!/bin/bash

# NOTE: chage this to the full path to globus if globus isn't in your $PATH
GLOBUS=globus

NCAR_ID="b6b5d5e8-eb14-4f6b-8928-c02429d67998"
IURT_ID="b2563c13-063e-444b-8946-823f642d9f2f"

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
