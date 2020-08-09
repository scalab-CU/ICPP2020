#!/bin/sh
#PBS -N temp
#PBS -l select=1:ncpus=16:mem=60gb:ngpus=1:gpu_model=v100,walltime=12:00:00
#PBS -o /scratch3/pzou/temp.o
#PBS -e /scratch3/pzou/temp.e#

module load anaconda3/5.1.0

cd /home/pzou/projects/Power_Signature/data_analysis
python rnnInter_Power.py p100
#python power_parse.py
