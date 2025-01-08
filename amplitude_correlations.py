import numpy as np
import SimpleITK as sitk
import glob
import csv
import os
import matplotlib.pyplot as plt

# This script compares a group map (e.g., generated from PALM) and compares it
# it with a prior network to determine the amplitude correspondence.

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

# Modified from RABIES code:
def eval_relationships_zThresh_masked(prior_data, group_data, zVal_prior, group, time):
    dataset_stats = {}
    
    masked_prior=prior_data[np.abs(prior_data)>=zVal_prior] # taking absolute values to include negative weights
    masked_group=group_data[np.abs(prior_data)>=zVal_prior] # taking absolute values to include negative weights
    dataset_stats[f'AmplitudeCorr'] = amplitude_corr(masked_prior,masked_group, group, time)

    return dataset_stats

# Modified from RABIES code:
def eval_relationships_zThresh(prior_data, group_data):
    dataset_stats = {}
    
    dataset_stats[f'AmplitudeCorr'] = amplitude_corr(prior_data,group_data)

    return dataset_stats


def amplitude_corr(array1, array2):
    array1_flat = array1.flatten()
    array2_flat = array2.flatten()
    correlation = np.corrcoef(array1_flat, array2_flat)[0, 1]
    # OPTIONAL: Plot array1 vs array2
    plot_bool = False # Switch to True if you want to save plot. Edit "fullpltpath" path below to change where it saves to.
    if plot_bool:
        fullpltpath = ''
        
        plt.rcParams['font.family'] = 'Helvetica'
        plt.figure()
        plt.plot(array1_flat, array2_flat, marker='.', linestyle='', markersize=8)
        plt.xlim([-6, 23])
        plt.ylim([-5, 8])
        fs = 40 # Font Size
        plt.text(9, -4, f"r = {round(correlation, 3)}", fontsize=fs, ha="left", va="bottom")
        # Customize tick thickness and font size
        ax = plt.gca()  # Get current axes
        ax.tick_params(axis='both', width=4, length=7, labelsize=fs)
        # Increase bounding box (spines) linewidth
        ax.spines['top'].set_linewidth(4)    # Top border
        ax.spines['right'].set_linewidth(4)  # Right border
        ax.spines['bottom'].set_linewidth(4) # Bottom border
        ax.spines['left'].set_linewidth(4)   # Left border
        plt.savefig(fullpltpath, format = 'png', dpi=300, bbox_inches='tight')
        #plt.show() # Uncomment this line to show plot rather than just saving it
    return correlation



if __name__ == '__main__':
    
    #%% User input
    # Specify which directories hold the group maps to be analyzed
    dirs = []

    # Specify prior image full path
    # (make sure prior image is in same space as group maps)
    prior = ''
    
    #%%
    
    prior_data = sitk.GetArrayFromImage(sitk.ReadImage(prior))
    
    allfiles = fileskimmer(dir, '_ztstat_c1.nii')
    
    for dir in dirs:
        
        # csv file to store amplitude results
        fileLocation = os.path.join(dir, 'DSC_results.csv')

        #for zVal in np.arange(0.5, 5, 0.1):
        for file in allfiles:
            network = file
            network_data = sitk.GetArrayFromImage(sitk.ReadImage(network))

            print('Loaded in image data...')

            #maps = get_maps(prior_data, network_data)

            print('Generated maps variable...')

            #dice_overlap_top4perc_dict = eval_relationships_percentThresh(prior_data, network_data)
            #dice_overlap_top4perc = dice_overlap_top4perc_dict.get('Overlap: Prior')
            zVal_prior = 3.1
            masked_amp_corr_z31_dict = eval_relationships_zThresh_masked(prior_data, network_data, zVal_prior)
            masked_amp_corr_z31 = masked_amp_corr_z31_dict.get('AmplitudeCorr')
            #amp_corr_z31_dict = eval_relationships_zThresh(prior_data, network_data)
            #amp_corr_z31 = amp_corr_z31_dict.get('AmplitudeCorr')

            print('Got Amplitude Correlation...')
            print('File: ' + file)
            #print('Top 4%: ' + str(dice_overlap_top4perc))
            print('Masked Amplitude Correlation: ' + str(masked_amp_corr_z31))
            #print('Whole Brain Amplitude Correlation: ' + str(amp_corr_z31))
            print('')
            
            # Get parent directory to be used as group
            parent_dir = os.path.basename(os.path.dirname(file))
            #continue # Only run for first sample per grouping
            if not os.path.exists(fileLocation):
                with open(fileLocation, 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',')
                    spamwriter.writerow(['Folder', 'File', 'Group', 'CumulativeAcqTime', 'Masked_Amp_Corr_zThresh'])#, 'Amp_Corr_zThresh'])

            with open(fileLocation, 'a', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                spamwriter.writerow([parent_dir, file, masked_amp_corr_z31])#, amp_corr_z31])
        



