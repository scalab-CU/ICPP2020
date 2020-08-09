#!/bin/sh
#PBS -N rp_perf
#PBS -l select=1:ncpus=10:mem=60gb:ngpus=1:gpu_model=p100,walltime=72:00:00
#PBS -o /scratch3/pzou/perfp100.risky.o
#PBS -e /scratch3/pzou/perfp100.risky.e

###############configuration#############
# set environment varialbe TMPDIR // to save files in tmp folder and then sync them to host folder
# set environment varialbe NVPROFPATH // define the path of nvprof 
# set environment varialbe BENCHDIR // the path of benchfolder 
# set environment varialbe BENCHTYPE // mybench or risky
module rm cuda-toolkit/8.0.44
module load cuda-toolkit/9.0.176 cuDNN/9.0v7.3.0 nccl/2.1.2-1 anaconda3/5.1.0

#TMPDIR was defined in palmetto
export NVPROFPATH="/software/cuda-toolkit/9.0.176/bin/nvprof"
export BENCHDIR="/scratch3/pzou/Power_Signature/monitor_peng"
export BENCHTYPE="risky"
export ARCH="p100"

#DEFINE architecture
arch=p100

#types mybench or risky
type=risky


#define scratch_folder for save results
scratch_results=/scratch3/pzou/Power_Signature/results/
home_results=/home/pzou/projects/Power_Signature/results/

cd $PBS_O_WORKDIR


#export CUDA_VISIBLE_DEVICES=0

#for palmetto only
nodeName=$( cat /proc/sys/kernel/hostname )
nodeName="$(cut -d'.' -f1 <<<"$nodeName")"


current_date_time="$(date +'%Y-%m-%d-%H-%M')"
mkdir ${scratch_results}/risky/p100/perf-temp
mkdir ${home_results}/risky/p100/perf-temp


python ./perf_Error.py &
#python ./mem_trace.py risky &
#python ./power.py risky &

pid=$!


sleep 10
#export CUDA_VISIBLE_DEVICES=1
#python ./perf.py ./metrics.csv ./applications_mybench_re.csv &
#pid2=$!

while ps -p $pid >/dev/null 2>&1; do
	sleep 600
    rm $TMPDIR/CUPTI*
	rsync -az $TMPDIR/ ${scratch_results}/risky/p100/perf-temp
    rsync -az $TMPDIR/ ${home_results}/risky/p100/perf-temp
    
done

#while ps -p $pid2 >/dev/null 2>&1; do
#	sleep 600
#done

rm $TMPDIR/CUPTI*
rsync -az $TMPDIR/ ${scratch_results}/risky/p100/perf-temp
rsync -az $TMPDIR/ ${home_results}/risky/p100/perf-temp

