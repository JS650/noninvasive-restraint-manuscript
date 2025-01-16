#!/bin/bash
#SBATCH --time=00-0:01:00 # DD-HH:MM:SS#SBATCH
#SBATCH --array=0-2 # Change this range to 0 - <number of directories in 'inputs' minus 1>
# -- Likely need more SBATCH commands (i.e., specify memory/cores/email notification/etc)

# Load modules
module load python/3.8
source ~/dev/venvs/myenv/bin/activate
module load gcc/8.3.0
module load openblas/0.3.7
module load mkl/2019u4
module load fsl/6.0.4
module load octave/5.2.0
PATH=$PATH:~/dev/palm-alpha119

# Enter all directories holding dual-regression files to be analyzed by PALM:
inputs=(
" "
)

# Select the inputs for this array job
input="${inputs[$SLURM_ARRAY_TASK_ID]}"

python /home/r/rmenon/jlaxer2/dev/rabies_extensions/rabies_average_component_map_SLURM.py "$input"
