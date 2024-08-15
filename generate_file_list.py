#!/usr/bin/env python

#%%
import pandas as pd
import datetime as dt
import sys
import subprocess
import glob

NCAR_ID="1e128d3c-852d-11e8-9546-0a6d4e044368"

variable_tables = glob.glob("variable_tables/*.txt")

try:
    varname = str(sys.argv[1])
except:
    print(f"Usage: {sys.argv[0]} VARNAME [DIRECTORY]")
    print("Where DIRECTORY is the directory in which the variable exists (if it exists in multiple; e.g., z.")
    sys.exit(-1)

try:
    directory = str(sys.argv[2])
except:
    directory = None

#%%
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

# %%
# get the row containing this variable
if directory is None:
    current_row = variable_table.query('Name == @varname')
else:
    current_row = variable_table.query('Name == @varname and Directory == @directory')

if len(current_row) != 1:
    raise RuntimeError(f"Error: query for 'Name == {varname}' returned a table with length {len(current_row)}")
# %%
# construct the path template
table, parameter, _, _, _, _, directory, _ = list(current_row.values[0])
path_template_base = f"/ds633.0/{directory}/{{YYYYMM}}/{directory}.{table:03}_{parameter:03}_{varname}.ll025sc.{{date_range}}.nc"

# modify the filename if the variable is u or v
if varname == "u" or varname == "v":
  path_template_base = path_template_base.replace("ll025sc","ll025uv")

# if the data are on the invariant grid, there is only one file to worry about
if directory == "e5.oper.invariant":
    YYYYMM = "197901"
    date_range = "1979010100_1979010100"
    path = path_template_base.format(YYYYMM = YYYYMM, date_range = date_range)

    print(path)
    sys.exit(0)

# %%
# obtain the first file in the series
check_dir = f"ds633.0/{directory}/197901/"
listing = subprocess.check_output(['globus','ls', f"{NCAR_ID}:{check_dir}"])

#%%
# determine whether files are stored daily or monthly

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

# %%
# create a list of all dates for which files should exist
if files_are_daily:
    freq_arg = 'D'
else:
    freq_arg = 'MS'

# generate the start dates
all_dates_1 = pd.date_range('1979-01-01', '2022-01-01', freq = freq_arg)[:-1]

if files_are_daily:
  # set the end day to be the same as the start date for daily data
  all_dates_2 = all_dates_1
else:
  # set the end day to be the end of the month for monthly data
  all_dates_2 = pd.date_range('1979-01-01', '2022-01-01', freq = 'M')[:-1]

# set the end time to hour 23
all_dates_2 = [ d + dt.timedelta(hours=23) for d in all_dates_2 ]

# %%
# create the list of files
for d1, d2 in zip(all_dates_1, all_dates_2):
    YYYYMM = d1.strftime("%Y%m")
    d1str = d1.strftime("%Y%m%d%H")
    d2str = d2.strftime("%Y%m%d%H")
    date_range = f"{d1str}_{d2str}"

    path = path_template_base.format(YYYYMM=YYYYMM,date_range = date_range)
    print(path)

# %%
