import csv
import subprocess
import os

def merge_files_from_csv(csv_file, output_file, merge_type="n"):
    """
    Merges files listed in a CSV file using FSL's fslmerge.

    Args:
        csv_file (str): Path to the CSV file containing file paths.
        output_file (str): Path for the merged output file.
        merge_type (str): Type of merge for fslmerge (default is 't' for time-series).
    """
    # Read file paths from the CSV file
    with open(csv_file, mode="r") as file:
        reader = csv.reader(file)
        file_list = [row[0] for row in reader]  # Assuming one file path per row

    # Check if files exist
    missing_files = [f for f in file_list if not os.path.exists(f)]
    if missing_files:
        print("The following files are missing:")
        for f in missing_files:
            print(f)
        return

    # Build the fslmerge command (Prior components: 5 = Somatomotor, 12 = Visual, 19 = DMN)
    command = ["fslmerge", f"-{merge_type}", '19', output_file] + file_list

    # Run the command using subprocess
    try:
        subprocess.run(command, check=True)
        print(f"Merged files successfully into {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during merging: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Example usage
    csv_file = "/Volumes/menon_data$/slaxer/data/ds-IsoAttn/derivatives/group_stats/ICA/dual_regression_files.csv"          # Path to your CSV file
    output_file = "/Volumes/menon_data$/slaxer/data/ds-IsoAttn/derivatives/group_stats/ICA/merged_dual_regression_files_comp19.nii"  # Path for the output file
    merge_files_from_csv(csv_file, output_file)

