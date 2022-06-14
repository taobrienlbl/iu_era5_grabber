#!/bin/bash

# NOTE: chage this to the full path to globus if globus isn't in your $PATH
GLOBUS=globus

useage=$(cat << EOF
    usage: $0 FILEPATHLIST.txt [OUTPUT_DIRECTORY]\n
\n

    Takes a list of NCAR RDA files as input and initiates a globus transfer to copy\n
    the files to the output directory. The directory structure on NCAR RDA\n
    is replicated in the output directory.\n
\n
    Since Globus is used, authentication is necessary--but only for the first\n
    exectuion of this program in a session, which is approximately 1 day. \n
    
    Please run activate_endpoints.bash to log in. \n

    FILEPATHLIST.txt should simple list a set of valid paths to files on NCAR RDA.
\n
EOF
); usage=${usage%a}

FILEPATHLIST=$1
OUTPUT_DIRECTORY=$2

if [ "$FILEPATHLIST" == "" ]; then
#|| "$FILEPATHLIST" == "--help" || "$FILEPATHLIST" == "-h" ]
    echo -e $useage
    exit -1
fi

if [ "$OUTPUT_DIRECTORY" == "" ]; then
    OUTPUT_DIRECTORY="/N/scratch/${USER}/ERA5/"
fi

transfer_name=${FILEPATHLIST//./_}
transfer_name=${transfer_name//\//_}

#*******************************************************************************
#*******************************************************************************
#********************** CONSTRUCT THE TRANFSER FILE LIST ***********************
#*******************************************************************************
#*******************************************************************************

# parse the file list
FILEPATHS=`cat $FILEPATHLIST`

batch_transfer_list=""
for filepath in $FILEPATHS
do
    batch_transfer_list="${batch_transfer_list}${filepath} ${OUTPUT_DIRECTORY}/${filepath}\n"
done

#*******************************************************************************
#*******************************************************************************
#****************** GLOBUS AUTHENTICATION AND PASSING **************************
#*******************************************************************************
#*******************************************************************************



NCAR_ID="1e128d3c-852d-11e8-9546-0a6d4e044368"
IURT_ID="b287987e-b433-11e8-8241-0a3b7ca8ce66"

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# form the transfer list

# initiate the transfer
echo ""
echo -e "$batch_transfer_list" | $GLOBUS transfer --sync-level checksum --preserve-mtime $NCAR_ID:/ $IURT_ID:/ --batch - --label "$transfer_name"
