import generate_file_list as gfl
import argparse
import datetime as dt

state_variables = "t q u v z".split()
directory = "e5.oper.an.pl"

parser = argparse.ArgumentParser(description="Generate file lists for ERA5 variables.")
parser.add_argument("--start-date", type=str, default="1979-01-01",
                    help="The start date for the file list (default: 1979-01-01).")
parser.add_argument("--end-date", type=str, default="2025-05-01",
                    help="The end date for the file list (default: 2025-05-01).")

args = parser.parse_args()
start_date_str = args.start_date
end_date_str = args.end_date

# Convert start and end dates to datetime objects
start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d")

for varname in state_variables:
    paths = gfl.generate_file_list(
        varname=varname,
        start_date=start_date,
        end_date=end_date,
        directory=directory,
        verbose=False,
    )
    
    # Save the paths to a file
    with open(f"{varname}_3d.list", "w") as f:
        for path in paths:
            f.write(path + "\n")
    print(f"File list for {varname} saved to {varname}.list")