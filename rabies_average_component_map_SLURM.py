import csv
import numpy as np
import os, os.path
from typing import List
import shutil
import sys
import json
import glob

# Create script which takes in a directory with DR files and a specific
# component (user defined). It then merges all the files at that component and
# averages them as done in RABIES. Then it runs PALM to get the group map to
# compare statistically.

# This script runs FSL PALM. This function can take a long time for large
# groups. Thus it is most efficient running on a cluster such as alliance canada
# and running in parallel. This script is set up for such processing in
# combination with a suitable SLURM script.


#%% FUNCTIONS
def fileskimmer(directory: str, file_ext: str = ''):
    '''
    fileskimmer finds and returns all the files within directory that match the 
    string pattern given by file_ext.

    directory -> Str
    file_ext -> Str
    '''
    # Use glob
    files = glob.glob(os.path.join(directory, '**', '*' + file_ext), recursive=True)
    return files


def csv_organizer(csv_files:List[str]) -> dict:
    '''
    Reads in list of files, and uses BIDS filename convention to organize files
    in an array. Returns dictionary structured as follows:

    {sub1:  {ses1: {run1: <filepath>, run2: <filepath>},
            ses1: {run1: <filepath>, run2: <filepath>}},
     ses2: {ses1: {run1: <filepath>, run2: <filepath>}}}

    '''
    # Initialize dictionary
    sub_dict = {}
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        # Segment file into list based on "_"
        split_file = filename.split('_')
        # Get sub, ses, and run from filename:
        sub = split_file[0]
        ses = split_file[1]
        run = split_file[3]
        # Check if sub in sub_dict, if not - add it:
        if not sub in sub_dict:
            sub_dict.update({sub: {ses: {run: filepath}}})
        else:
            if not ses in sub_dict.get(sub):
                sub_dict.get(sub).update({ses: {run: filepath}})
            else:
                if not run in sub_dict.get(sub).get(ses):
                    sub_dict.get(sub).get(ses).update({run: filepath})
    
    return sub_dict


#%% Helpers for "file_copyer_and_group_map"
def csvread(inputFile):
    with open(inputFile, newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = [row for row in reader]
        data = np.array(data)
        return data

def group_dict_maker(csv_file):
    #Reads in list of files, and uses BIDS filename convention to organize files
    #in an array. Returns dictionary structured as follows:
    #
    #{group1: {sub1: {ses1: {run1: #, run2: #}},
    #                {ses2: {run1: #, run2: #}}},
    # group2: {sub2: {ses1: {run1: #, run2: #}}}}
    #

    # Initialize dictionary
    group_dict = {}
    for col_idx in range(len(csv_file[0])):
        group_label = csv_file[0][col_idx]
        for file in csv_file[1:, col_idx]:
            filename = os.path.basename(file)
            # Segment file into list based on "_"
            split_file = filename.split('_')
            # Get sub, ses, and run from filename:
            sub = split_file[0]
            ses = split_file[1]
            run = split_file[3]
            # Check if sub in group_dict, if not - add it:
            if not group_label in group_dict:
                group_dict.update({group_label: {sub: {ses: {run: 1}}}})
            else:
                if not sub in group_dict.get(group_label):
                    group_dict.get(group_label).update({sub: {ses: {run: 1}}})
                else:
                    if not ses in group_dict.get(group_label).get(sub):
                        group_dict.get(group_label).get(sub).update({ses: {run: 1}})
                    else:
                        # If we have a duplicate file (as needed for bootstrapping WITH replacement but not WITHOUT), just add suffix to run key so dictionary will save it.
                        if run in group_dict.get(group_label).get(sub).get(ses):
                            curr_run_repeats = group_dict.get(group_label).get(sub).get(ses).get(run)
                            new_run_repeats = curr_run_repeats + 1
                            group_dict.get(group_label).get(sub).get(ses).update({run: new_run_repeats})
                        else:
                            group_dict.get(group_label).get(sub).get(ses).update({run: 1}) 
    return group_dict

def file_grouper(run_dict, group_dict, out_dir):
    #Takes in a run_dict (created by getting all the runs from some input directory)
    #and a group_dict (created by converting a sorting csv file into a dictionary)
    #and uses group_dict to create directories and copies the run files from run_dict
    #into the directory correspondingly. 
    file_num = 1 # For progress updates
    for group in group_dict:
        # Make directory for group in output directory
        curr_group_out_dir = os.path.join(out_dir, group)
        if not os.path.exists(curr_group_out_dir):
            os.mkdir(curr_group_out_dir)
        for sub in group_dict.get(group):
            for ses in group_dict.get(group).get(sub):
                for run in group_dict.get(group).get(sub).get(ses):
                    print('Searching for ' + sub + ',' + ses + ',' + run + ' in ' + str(group_dict))
                    # Find the corresponding file in run_dict:
                    # Make sure that the sub, ses, and run exist in run_dict first.
                    print('sub: ' + sub + ' dict: ' + str(run_dict.keys()))
                    if sub in run_dict.keys():
                        if ses in run_dict.get(sub).keys():
                            if run in run_dict.get(sub).get(ses).keys():
                                # PROGRESS UPDATE:
                                print('File # ' + str(file_num))
                                file_num = file_num + 1
                                # Get current file
                                run_file = run_dict.get(sub).get(ses).get(run)
                                basename = os.path.basename(run_file)
                                out_file = os.path.join(curr_group_out_dir, basename)
                                # Copy file to output directory
                                # MAKE sure we account for copying duplicate files to directory (i.e., if sampling WITH replacement)
                                for repeat_idx in range(group_dict.get(group).get(sub).get(ses).get(run)):
                                    if out_file[-7:] == '.nii.gz':
                                        rep_out_file = out_file[:-7] + '_' + str(repeat_idx + 1) + 'repeats.nii.gz'
                                    else:
                                        print('UNANTICIPATED EXTENSION for ' + out_file)
                                        raise NameError('Unanticipated extension.')
                                    shutil.copyfile(run_file, rep_out_file)
                            else:
                                print('RUN NOT IN DICTIONARY')
                        else:
                            print('SES NOT IN DICTIONARY')
                    else:
                        print('SUB NOT IN DICTIONARY')
    print('DONE copying files into groups in ' + out_dir)


def file_copyer_and_group_map(analysis_dir, group, time):
    '''
    Put everything together into function to allow for parallel processing (below).
    '''
    #%% Sort data into groups (if applicable)
    sorting_file = analysis_dir + f'/{group}/{time}/rand_samples_{group}_{time}.csv'
    sorting_data = csvread(sorting_file)
    sorted_dict = group_dict_maker(sorting_data)
    #print(sorted_dict)

    #%% Copy files to directories according to their respective groups
    out_dir = os.path.dirname(sorting_file)
    file_grouper(run_dict, sorted_dict, out_dir)

    #%% Get all folder names containing each group that we want to find average component of
    grouped_nii_files = fileskimmer(out_dir, 'repeats.nii.gz')
    # Get a list with each of the parent directories for each file
    mydirs = []
    for file in grouped_nii_files:
        mydirs.append(os.path.dirname(file))

    count = 1
    for mydir in mydirs:
        # Keep track of which folder we are on (print to console for progress update)
        print('File ' + str(count) + ' of ' + str(len(mydirs)))
        count = count + 1

        # Set up output filenames and output folders before computing average component map and statistics
        outdir = mydir
        ## Based on user input:
        mydir_bottomdirname = os.path.basename(os.path.normpath(mydir))
        mergedname = 'merged_somatomotor_' + mydir_bottomdirname
        avgname = mergedname + '_Tmean'
        statsname = '_1sampleGroupMean'
        uncorrpmaps_suffix = '_vox_p_tstat1'
        ptoz_suffix = '_ptoz'
        ext = '.nii'

        # Create paths
        mergedpath = outdir + os.path.sep + mergedname + ext
        avgfilepath = outdir + os.path.sep + avgname + '.nii.gz'
        zmap_path = outdir + os.path.sep + mergedname + statsname + uncorrpmaps_suffix + ptoz_suffix + ext

        # Get string of all images in directory
        files = fileskimmer(mydir, 'repeats.nii.gz')
        filestr = ' '.join(files)

        # Merge images
        if not os.path.exists(mergedpath): # Make sure file does not already exist
            # Prior components: 5 = Somatomotor, 12 = Visual, 19 = DMN
            os.system('fslmerge -n 5 ' + mergedpath + ' ' + filestr)
            os.system('gunzip ' + mergedpath + '.gz')

        # Average the merged image *** as done in RABIES:
        if not os.path.exists(avgfilepath): # Make sure file does not already exist
            os.system('fslmaths ' + mergedpath + ' -Tmean ' + avgfilepath)

        # Get 1-sample t-test group average maps and convert to z-scores
        if not os.path.exists(zmap_path): # Make sure file does not already exist
            os.system('palm -i ' + mergedpath + ' -o ' + mydir + os.path.sep + mergedname + statsname + ' -zstat -n 5000')
    

if __name__ == "__main__":
    #%% Get all files and organize in sub > ses > run: ### dictionary

    # Specify directory containing dual-regression files:
    dr_dir = '<full-path-to-analysis-dir>/<analysis-dir>/analysis_datasink/dual_regression_nii'
    # Sift through dr_dir directory and save all filenames to list:
    nii_files = fileskimmer(dr_dir, 'maps.nii.gz')
    # Organize list of files into dictionary in form: sub > ses > run: ###
    run_dict = csv_organizer(nii_files)

    # The SLURM file used to run this script should contain - in JSON format - 
    # the paths to all directories you wish to generate group maps of using
    # PALM.
    input_json = json.loads(sys.argv[1])
    analysis_dir = input_json["analysis_dir"]
    group = input_json["group"]
    time = input_json["time"]
    # Specify directory holding csv files for sorting and where groups maps should be stored:
    results = file_copyer_and_group_map(analysis_dir, group, time)
    print("Results:", results)

