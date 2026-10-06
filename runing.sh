#!/bin/bash
#SBATCH --job-name=projec
#SBATCH --chdir=.
#SBATCH --error=projec.err
#SBATCH --output=projec.out
#SBATCH --account=bsc21
#SBATCH --qos=gp_debug
##SBATCH --qos=gp_bsccase
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:25:00
##SBATCH --time=48:00:00
#
# Load modules for the executable
#
module load hdf5 python
#
# Launches 
#
python main-new.py

