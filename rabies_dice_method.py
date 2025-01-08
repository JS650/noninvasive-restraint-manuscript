import numpy as np
import SimpleITK as sitk
import glob
import csv
import os


# This script compares a group map (e.g., generated from PALM) and compares it
# it with a prior network to determine the Dice Similarity Coefficient (DSC).


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


# HELPERS
# RABIES approach:
def percent_threshold(array): # set threshold to be the top 4% of all voxels
    flat=array.flatten()
    flat.sort()
    idx=int((0.96)*len(flat))
    threshold = flat[idx]
    return threshold

def dice_coefficient(mask1,mask2):
    dice = np.sum(mask1*mask2)*2.0 / (np.sum(mask1) + np.sum(mask2))
    return dice


# Modified from RABIES code:
def eval_relationships_percentThresh(map1, map2):
    dataset_stats = {}
    
    threshold1 = percent_threshold(map1)
    mask1=np.abs(map1)>=threshold1 # taking absolute values to include negative weights
    threshold2 = percent_threshold(map2)
    mask2=np.abs(map2)>=threshold2 # taking absolute values to include negative weights
    dataset_stats[f'Overlap: Prior'] = dice_coefficient(mask1,mask2)

    return dataset_stats


# Modified from RABIES code:
def eval_relationships_zThresh(map1, map2, zVal_prior, zVal_group):
    dataset_stats = {}
    
    mask1=np.abs(map1)>=zVal_prior # taking absolute values to include negative weights
    mask2=np.abs(map2)>=zVal_group # taking absolute values to include negative weights
    dataset_stats[f'Overlap: Prior'] = dice_coefficient(mask1,mask2)

    return dataset_stats



if __name__ == '__main__':
    #%% USER INPUT
    # Specify all directories holding group maps
    dirs = []

    # Specify prior image full path
    # (make sure prior image is in same space as group maps)
    prior = ''
    
    # Specify z-value thresholds
    zVal_prior = 3.1 # for prior network
    zVal_group = 3.0 # for group network


    #%% 
    # Get data from prior image
    prior_data = sitk.GetArrayFromImage(sitk.ReadImage(prior))

    # Cycle through all user-specified directories, find group map files (suffix = '_ztstat_c1.nii') and get DSC values
    for dir in dirs:
        fileLocation = os.path.join(dir, 'DSC_results.csv')

        allfiles = fileskimmer(dir, '_ztstat_c1.nii')

        # Cycle through all files
        for file in allfiles:
            network = file
            network_data = sitk.GetArrayFromImage(sitk.ReadImage(network))

            print('Loaded in image data...')

            dice_overlap_top4perc_dict = eval_relationships_percentThresh(prior_data, network_data) # RABIES method
            dice_overlap_top4perc = dice_overlap_top4perc_dict.get('Overlap: Prior') 
            dice_overlap_z31_dict = eval_relationships_zThresh(prior_data, network_data, zVal_prior=zVal_prior, zVal_group=zVal_group) # z-value method
            dice_overlap_z31 = dice_overlap_z31_dict.get('Overlap: Prior')

            print('Got DICE score...')
            print('File: ' + file)
            print('Top 4%: ' + str(dice_overlap_top4perc))
            print('z >= 3.1: ' + str(zVal_group) + ' DICE: ' + str(dice_overlap_z31))
            print('')
            
            # Get parent directory to be used as group in DSC spreadsheet
            parent_dir = os.path.basename(os.path.dirname(file))
            
            if not os.path.exists(fileLocation):
                with open(fileLocation, 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',')
                    spamwriter.writerow(['Group', 'File', 'DICE_4perc', 'zThresh', 'DICE_zThresh'])

            with open(fileLocation, 'a', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                spamwriter.writerow([parent_dir, file, dice_overlap_top4perc, str(zVal_group), dice_overlap_z31])

