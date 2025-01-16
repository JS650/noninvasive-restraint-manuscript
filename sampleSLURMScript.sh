#!/bin/bash
#SBATCH --time=00-0:01:00 # DD-HH:MM:SS#SBATCH

# Load modules
module load python/3.8
source ~/dev/venvs/myenv/bin/activate
module load gcc/8.3.0
module load openblas/0.3.7
module load mkl/2019u4
module load fsl/6.0.4
module load octave/5.2.0
PATH=$PATH:~/dev/palm-alpha119

inputs=(
'{"analysis_dir": "/scratch/r/rmenon/jlaxer2/python_work", "group": "motionGroup5", "time": "30min"}'
'{"analysis_dir": "/scratch/r/rmenon/jlaxer2/python_work", "group": "motionGroup5", "time": "60min"}'
'{"analysis_dir": "/scratch/r/rmenon/jlaxer2/python_work", "group": "motionGroup5", "time": "90min"}'
'{"analysis_dir": "/scratch/r/rmenon/jlaxer2/python_work", "group": "motionGroup5", "time": "120min"}'
'{"analysis_dir": "/scratch/r/rmenon/jlaxer2/python_work", "group": "motionGroup5", "time": "150min"}'
'{"analysis_dir": "/scratch/r/rmenon/jlaxer2/python_work", "group": "motionGroup5", "time": "180min"}'
'{"analysis_dir": "/scratch/r/rmenon/jlaxer2/python_work", "group": "motionGroup5", "time": "210min"}'
)

# Select the inputs for this array job
input="${inputs[$SLURM_ARRAY_TASK_ID]}"

python /home/r/rmenon/jlaxer2/dev/rabies_extensions/rabies_average_component_map_SLURM.py "$input"
