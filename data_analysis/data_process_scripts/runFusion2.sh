#!/bin/sh
#PBS -N temp
#PBS -l select=24:ncpus=24:mem=60gb,walltime=24:00:00
#PBS -o /scratch3/pzou/fusion.o
#PBS -e /scratch3/pzou/fusion.e

module load anaconda3/5.1.0

cd /home/pzou/projects/Power_Signature/data_analysis

module add gnu-parallel


parallel --sshloginfile $PBS_NODEFILE  -j24  'module load anaconda3/5.1.0; cd /home/pzou/projects/Power_Signature/data_analysis; python rnnClassify_Fusion.py {} {} {}' ::: "k40" ::: "seen" "unseen" ::: 5 6 7 8 9 10 12 15 18 20 3 4
