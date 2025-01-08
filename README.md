# noninvasive-restraint-manuscript
Functions and scripts used in analysis steps and for generating figures for the non-invasive restraint manuscript.

After running images through RABIES, one can further analyze motion and network-related metrics using the following functions:

### Motion-Related Functions
  * motionParamPlotter_RABIES.m - Plots the motion parameters or frame-wise displacement (FD) values depending on whether a motion parameters file or FD file was inputted.
  * motionBroadCompare_FD_RABIES.m - Plots a histogram representing the motion of multiple runs.

### Network-Related Functions
  * rabies_average_component_map_SLURM.py - Generates group maps for user-specified dual-regression files. Requires PALM (from FSL).
    *   https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/PALM.html
    *   Winkler AM, Ridgway GR, Webster MA, Smith SM, Nichols TE. Permutation inference for the general linear model. NeuroImage, 2014;92:381-397
  * rabies_dice_method.py - Calculates the Dice Similarity Coefficient (DSC) between a group network and the corresponding prior network.
  * amplitude_correlations.py - Calculates the amplitude correspondence between a group network and the corresponding prior network.
