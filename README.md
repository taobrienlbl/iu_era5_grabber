This directory contains scripts for mirroring subsets of ERA5 from the NCAR RDA to SCRATCH.

# Instructions

1. Set up the environment with [astral uv](https://docs.astral.sh/uv/getting-started/installation/): `uv sync`
1. Activate the globus endpoints: `uv run bash 0_activate_endpoints.bash`
1. Generate the list of files to transfer, either: 
    * `uv run python3 1_get_state_file_lists.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD`, or
    * `uv run python3 generate_file_list.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD --varname <variable_name> > varname.list`
1. Transfer the files: `uv run python 2_run_era5_transfer.py <file_list1> <file_list2> ... --output-directory <output_directory>`

# Notes

* The NCAR RDA Globus endpoint (`b6b5d5e8-...`) was deleted when the RDA became the
  NSF NCAR Geoscience Data Exchange (GDEX). The scripts now use the
  "NSF NCAR GDEX Dataset Archive" collection, `c4e40965-a024-43d7-bef4-6010f3731b61`,
  which serves the same `/d633000/...` paths.
* The IURT collection (`b2563c13-...`) is a GCS v5 mapped collection; inspect it with
  `globus gcs collection show`, not `globus endpoint show`.
* Transfers use `--sync-level checksum --verify-checksum`. Lustre has silently corrupted
  copies on IU systems, so still read every transferred file back before trusting it.
