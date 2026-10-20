#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse

# Globus endpoint IDs
# NSF NCAR GDEX Dataset Archive (formerly the NCAR RDA endpoint b6b5d5e8-..., deleted by 2026-10)
NCAR_ID = "c4e40965-a024-43d7-bef4-6010f3731b61"
IURT_ID = "b2563c13-063e-444b-8946-823f642d9f2f"

# Globus command
GLOBUS = "globus"  # Change this to the full path if globus isn't in your $PATH

USAGE = '''\
usage: {} FILEPATHLIST.txt [OUTPUT_DIRECTORY]\n
Takes a list of NCAR RDA files as input and initiates a globus transfer to copy
    the files to the output directory. The directory structure on NCAR RDA
    is replicated in the output directory.

Since Globus is used, authentication is necessary--but only for the first
    execution of this program in a session, which is approximately 1 day. 

Please run activate_endpoints.bash to log in. 

FILEPATHLIST.txt should simply list a set of valid paths to files on NCAR RDA.
'''.format(sys.argv[0])

parser = argparse.ArgumentParser(description="Transfer ERA5 files using Globus.", usage=USAGE)
parser.add_argument("--output-directory", type=str, default="/project/obrienta_startup/datasets/ERA5/",
                    help="The directory to transfer files to (default: /project/obrienta_startup), relative to globus paths")
# allow multiple arguments for file paths
parser.add_argument("filepaths", nargs='+', help="List of file paths to transfer.")

args = parser.parse_args()

for filepathlist in args.filepaths:
    if not os.path.isfile(filepathlist):
        print(f"Error: {filepathlist} does not exist or is not a file.")
        sys.exit(1)
    transfer_name = filepathlist.replace('.', '_').replace('/', '_')

    # Construct the transfer file list
    try:
        with open(filepathlist, 'r') as f:
            filepaths = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file list: {e}")
        sys.exit(1)

    # construct the batch transfer list to pass to glubs
    batch_transfer_list = ""
    for filepath in filepaths:
        batch_transfer_list += f"{filepath} {args.output_directory}/{filepath}\n"


    # Set environment variables
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["LANG"] = "C.UTF-8"

    # Initiate the transfer
    try:
        proc = subprocess.run([
            GLOBUS, "transfer",
            "--sync-level", "checksum",
            "--verify-checksum",
            "--preserve-mtime",
            f"{NCAR_ID}:/",
            f"{IURT_ID}:/",
            "--batch", "-",
            "--label", transfer_name
        ], input=batch_transfer_list.encode('utf-8'), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Globus transfer failed: {e}")
        sys.exit(e.returncode)
