import os, os.path
import sys
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


def file_copyer_and_group_map(group_dir):
    '''
    Put everything together into function to allow for parallel processing (below).
    '''
    # Prior components: 5 = Somatomotor, 12 = Visual, 19 = DMN  ;  If not dealing with RABIES ICA maps, can still just use 0 or whichever component needed
    component = 0
    
    # Keep track of which folder we are on (print to console for progress update)

    # Set up output filenames and output folders before computing average component map and statistics
    outdir = group_dir
    
    ## Based on user input:
    mydir_bottomdirname = os.path.basename(os.path.normpath(group_dir))
    # Prior components: 5 = Somatomotor, 12 = Visual, 19 = DMN
    if component == 5:
        mergedname = 'merged_somatomotor_' + mydir_bottomdirname
    elif component == 12:
        mergedname = 'merged_visual_' + mydir_bottomdirname
    elif component == 19:
        mergedname = 'merged_DMN_' + mydir_bottomdirname
    elif component == 0:
        mergedname = 'merged_' + mydir_bottomdirname
    else:
        ValueError('UNKNOWN COMPONENT! Check code to make sure correct component is being merged.')

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
    #files = fileskimmer(group_dir, 'maps.nii.gz')
    files = fileskimmer(group_dir, 'map.nii.gz')
    #files = fileskimmer(group_dir, 'repeats.nii.gz')
    filestr = ' '.join(files)
    
    # Merge images
    if not os.path.exists(mergedpath): # Make sure file does not already exist
        # Prior components: 5 = Somatomotor, 12 = Visual, 19 = DMN
        if component == 5:
            print('Merging all SOMATOMOTOR networks.')
        elif component == 12:
            print('Merging all VISUAL networks.')
        elif component == 19:
            print('Merging all DMN networks.')
        elif component == 0:
            print('Merging all networks.')
        else:
            print('UNKNOWN COMPONENT! Check code to make sure correct component is being merged.')
        os.system('fslmerge -n ' + str(component) + ' ' + mergedpath + ' ' + filestr)
        os.system('gunzip ' + mergedpath + '.gz')

    # Average the merged image *** as done in RABIES:
    if not os.path.exists(avgfilepath): # Make sure file does not already exist
        os.system('fslmaths ' + mergedpath + ' -Tmean ' + avgfilepath)

    # Get 1-sample t-test group average maps and convert to z-scores
    if not os.path.exists(zmap_path): # Make sure file does not already exist
        os.system('palm -i ' + mergedpath + ' -o ' + group_dir + os.path.sep + mergedname + statsname + ' -zstat -n 5000')


if __name__ == "__main__":
    #%% Get all files and organize in sub > ses > run: ### dictionary

    # The SLURM file used to run this script should contain - in JSON format - 
    # the paths to all directories you wish to generate group maps of using
    # PALM.
    group_dir = sys.argv[1]
    # Specify directory holding csv files for sorting and where groups maps should be stored:
    results = file_copyer_and_group_map(group_dir)
    print("Results:", results)

