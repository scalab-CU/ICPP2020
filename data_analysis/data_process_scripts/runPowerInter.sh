#!/bin/sh
#PBS -N temp
#PBS -l select=12:ncpus=24:mem=60gb,walltime=24:00:00
#PBS -o /scratch3/pzou/temp.o
#PBS -e /scratch3/pzou/temp.e

module load anaconda3/5.1.0

cd /home/pzou/projects/Power_Signature/data_analysis

module add gnu-parallel


parallel --sshloginfile $PBS_NODEFILE  -j24  'module load anaconda3/5.1.0; cd /home/pzou/projects/Power_Signature/data_analysis; python rnnInter_Power.py {} {} {}' ::: "k40" "v100" "p100" ::: "unseen" "seen" :::  1 2 5 8 10 20 50
