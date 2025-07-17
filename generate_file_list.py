#!/usr/bin/env python
import pandas as pd
import datetime as dt
import sys
import subprocess
import glob
import datetime as dt




def parse_variable_tables(variable_tables_dir):
    """ Parse the variable tables and return a DataFrame. """
    variable_tables = glob.glob(f"{variable_tables_dir}/*.txt")
    if len(variable_tables) == 0:
        raise RuntimeError(f"Error: no variable tables found in {variable_tables_dir}. Please check the directory.")
    
    # parse the variable tables
    variable_table = None
    for table in variable_tables:
        tmp = pd.read_fwf(table, skiprows=[0,1,2,3,4,6]).drop('Unnamed: 0', axis = 1)

        # get the directory name
        dirname = '.'.join(table.split(".")[2:][:-4])

        # add this as a column
        tmp['Directory'] = dirname

        if variable_table is None:
            variable_table = tmp
        else:
            variable_table = pd.concat([variable_table, tmp])

    return variable_table

def generate_file_list(
        varname,
        start_date,
        end_date,
        NCAR_ID = "b6b5d5e8-eb14-4f6b-8928-c02429d67998",
        directory=None,
        variable_tables_dir="variable_tables",
        verbose = True,
        ):

    def vprint(*args, **kwargs):
        """ Print only if verbose is True. """
        if verbose:
            print(*args, **kwargs)

    variable_table = parse_variable_tables(variable_tables_dir)

    if directory is None:
        current_row = variable_table.query('Name == @varname')
    else:
        current_row = variable_table.query('Name == @varname and Directory == @directory')

    if len(current_row) != 1:
        raise RuntimeError(f"Error: query for 'Name == {varname}' returned a table with length {len(current_row)}")

    # construct the path template
    table, parameter, _, _, _, _, directory, _ = list(current_row.values[0])
    path_template_base = f"/d633000/{directory}/{{YYYYMM}}/{directory}.{table:03}_{parameter:03}_{varname}.ll025sc.{{date_range}}.nc"

    # modify the filename if the variable is u or v
    if varname == "u" or varname == "v":
        path_template_base = path_template_base.replace("ll025sc","ll025uv")

    # if the data are on the invariant grid, there is only one file to worry about
    if directory == "e5.oper.invariant":
        YYYYMM = "197901"
        date_range = "1979010100_1979010100"
        path = path_template_base.format(YYYYMM = YYYYMM, date_range = date_range)

        vprint(path)
        sys.exit(0)

    YYYYMM = dt.datetime.strftime(start_date, "%Y%m")
    check_dir = f"d633000/{directory}/{YYYYMM}/"
    listing = subprocess.check_output(['globus','ls', f"{NCAR_ID}:{check_dir}"])

    # get the list of files that match
    search_str = f"{table}_{parameter}_{varname}"
    matching_files = []
    for ffile in listing.decode('UTF-8').split("\n"):
        if ffile[-3:] == ".nc":
            search_str = f"{table:03}_{parameter:03}_{varname}"
            if search_str in ffile:
                matching_files.append(ffile)

    # sort the list
    matching_files = sorted(matching_files)
    vprint(matching_files)

    # extract the dates from the first file
    d1str, d2str = matching_files[0].split('.')[-2].split('_')

    # parse the dates and get the difference
    d1 = dt.datetime.strptime(d1str, "%Y%m%d%H")
    d2 = dt.datetime.strptime(d2str,"%Y%m%d%H")
    time_diff = d2 - d1
    if time_diff.days > 1:
        files_are_daily = False
    else:
        files_are_daily = True

    # create a list of all dates for which files should exist
    if files_are_daily:
        freq_arg = 'D'
    else:
        freq_arg = 'MS'

    # generate the start dates
    all_dates_1 = pd.date_range(start_date, end_date, freq = freq_arg)[:-1]

    if files_are_daily:
        # set the end day to be the same as the start date for daily data
        all_dates_2 = all_dates_1
    else:
        # set the end day to be the end of the month for monthly data
        all_dates_2 = pd.date_range(start_date, end_date, freq = 'M')[:-1]

    # set the end time to hour 23
    all_dates_2 = [ d + dt.timedelta(hours=23) for d in all_dates_2 ]

    # create the list of files
    paths = []
    for d1, d2 in zip(all_dates_1, all_dates_2):
        YYYYMM = d1.strftime("%Y%m")
        d1str = d1.strftime("%Y%m%d%H")
        d2str = d2.strftime("%Y%m%d%H")
        date_range = f"{d1str}_{d2str}"

        path = path_template_base.format(YYYYMM=YYYYMM,date_range = date_range)

        paths.append(path) 

    return paths

def main(varname, directory, NCAR_ID, variable_tables_dir, start_date, end_date, verbose):
    paths = generate_file_list(
        varname = varname,
        directory= directory,
        NCAR_ID = NCAR_ID,
        variable_tables_dir = variable_tables_dir,
        start_date = start_date,
        end_date = end_date,
        verbose = verbose,
    )
    for path in paths:
        print(path)

if __name__ == "__main__":
    import argparse

    # use argparse to parse the command line arguments
    parser = argparse.ArgumentParser(description="Generate a list of files for a given variable.")
    parser.add_argument("varname", type=str, help="The name of the variable to generate the file list for.")
    parser.add_argument("directory", type=str, nargs='?', default=None,
                        help="The directory in which the variable exists (if it exists in multiple; e.g., z).")
    parser.add_argument("--variable-tables", type=str, default="variable_tables",
                        help="The directory containing the variable tables (default: variable_tables).")
    parser.add_argument("--ncar-id", type=str, default=None,
                        help="The NCAR Globus ID (default: b6b5d5e8-eb14-4f6b-8928-c02429d67998).")
    parser.add_argument("--start-date", type=str, default="1979-01-01",
                        help="The start date for the file list (default: 1979-01-01).")
    parser.add_argument("--end-date", type=str, default="2022-01-01",
                        help="The end date for the file list (default: 2022-01-01).")
    parser.add_argument("--verbose", action='store_true', help="Print verbose output.")
    args = parser.parse_args()

    varname = args.varname
    directory = args.directory
    NCAR_ID = args.ncar_id
    variable_tables_dir = args.variable_tables
    start_date_str = args.start_date
    end_date_str = args.end_date
    verbose = args.verbose

    # convert start and end dates to datetime objects
    start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d")

    # if no NCAR ID is provided, use the default
    if NCAR_ID is None:
        NCAR_ID="b6b5d5e8-eb14-4f6b-8928-c02429d67998"

    main(varname, directory, NCAR_ID, variable_tables_dir, start_date, end_date, verbose)