This directory contains scripts for mirroring subsets of ERA5 from the NCAR RDA to SCRATCH.

# Instructions

1. Set up the environment with [astral uv](https://docs.astral.sh/uv/getting-started/installation/): `uv sync`
1. Activate the globus endpoints: `uv run bash 0_activate_endpoints.bash`
1. Generate the list of files to transfer, either: 
    * `uv run python3 1_get_state_file_lists.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD`, or
    * `uv run python3 generate_file_list.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD --varname <variable_name> > varname.list`
1. Transfer the files: `uv run bash 2_run_era5_transfer.py <file_list1> <file_list2> ... --output-directory <output_directory>`