import string
import subprocess
import os
import math
import re
import csv
import time
import glob
from random import shuffle
import sys
import fcntl
# ====================================== Configuration ========================================

DEVICE=0
NVPROFPATH = os.environ['NVPROFPATH']
type= os.environ['BENCHTYPE']
arch = os.environ['ARCH']

metrics_file="./metrics.csv"
if len(sys.argv) >=2:
    metrics_file=sys.argv[1]
    
    
applications_file="./applications_%s.csv"%(type)
if len(sys.argv) >=3:
    applications_file=sys.argv[2]    

curDirPath = os.getcwd()
metrics_finished_file=os.path.join(curDirPath, "metric_finished_{}_{}.csv".format(type, arch))


def get_apps():
    apps = []
    fin = open(applications_file,"r")
    for line in fin.readlines():
        if not line.startswith('#'):
            words = line.split(',')
            if words[-1] == '\n':
                del words[-1]
            app = words[0].strip()
            app_num = words[1].strip()
            exe = str("./") + words[2].strip()
            if len(words) == 4:
                exe += " " + words[3].strip()
            apps.append([app,app_num,exe])
    fin.close()
    return apps 

def get_metric():
    metrics = []
    fin = open(metrics_file, "r")
    for line in fin.readlines():
        if not line.startswith('#'):
            words = line.split(',')
            metric = words[0].strip()
            metrics.append(metric)
    fin.close()
    return metrics

def get_finished_metric():
    metrics = []
    fin = open(metrics_finished_file, "r")
    for line in fin.readlines():
        words = line.split(',')
        metric = words[0].strip()
        metrics.append(metric)
    fin.close()
    return metrics
    
def update_finished_metric(metric):
    with open(metrics_finished_file, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(metric)
        f.write("\n")
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
        
def delete_finished_metric(metric):
    with open(metrics_finished_file, 'r') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        lines = f.readlines()
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
    with open(metrics_finished_file, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        for line in lines:
            if line.strip("\r\n") != metric:
                f.write(line)
                f.write("\n")
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
def get_a_metric(app, exe, metric):
    os.environ['COMPUTE_PROFILE'] = "0"
    cmd = NVPROFPATH + str(" --csv ") + \
            " --metrics " + str(metric) + " --timeout 1800 " + exe 
    print(cmd)
    temp = subprocess.run(cmd.split(),stderr=subprocess.PIPE)
    #print(temp)
    values= temp.stderr.decode()
    
    return values
        
def get_kernel_names(app, exe):
    cmd = NVPROFPATH + str(" --csv --devices ") + str(DEVICE) + \
            " --metrics inst_per_warp " + exe 
          
    
    
    temp = subprocess.run(cmd.split(),stderr=subprocess.PIPE)

    values= temp.stderr.decode()
    values= values.split('\n')

    items_count = len(values)
    kernel_names = []
    for line in values:
        if 'inst_per_warp' in line:
            temp = line.split(',')[1]
            if '(' in temp:
                temp = temp.split('(')[0]            
            if temp[0] == "\"":
                temp = temp[1:]
            if '<' in temp:
                temp = temp.split('<')[0]
            if ' ' in temp:
                temp = temp.split(' ')[1]
            kernel_names.append(temp)
        
    return kernel_names

apps = get_apps()
shuffle(apps)
metrics = get_metric()
shuffle(metrics)

def get_finishList(pathfolder, fileType):
    owd = os.getcwd()
    os.chdir(pathfolder)
    app_lists = [ f.split('.')[0] for f in glob.glob("*.%s"%fileType) ]
    os.chdir(owd)
    return app_lists

#finished_list = get_finishList(r"/home/pzou/projects/Power_Signature/results/mybench/P100/node0017-2019-04-24-21-41", "csv")

def chk_gpu_error():
    out = subprocess.check_output(['nvidia-smi'])
    if 'ERR!' in out.decode():
        return True
    else:
        return False
for ar in apps:
    app = ar[0]
    app_num = int(ar[1])
    exe = ar[2]
    resultFolder = os.environ['TMPDIR']
    if not os.path.exists(os.path.join(resultFolder, app+str(app_num))):
        os.mkdir(os.path.join(resultFolder, app+str(app_num)))
   
   
   
benchFolder = os.environ['BENCHDIR']   
resultFolder = os.environ['TMPDIR']
for mtc in metrics:
    if chk_gpu_error():
        break
    print(mtc)
    metrics_finished = get_finished_metric()
    if mtc in metrics_finished:
        continue
    else:
        update_finished_metric(mtc)
    for ar in apps:
        app = ar[0]
        app_num = int(ar[1])
        exe = ar[2]        
        os.chdir(os.path.join(benchFolder, type))
        os.chdir(app)
        
        fileName=os.path.join(resultFolder, app+str(app_num), "%s.perf.txt"%(mtc))
        value = get_a_metric(app, exe,  str(mtc)) #profile a metric
        with open(fileName, 'w+') as file:            
            file.write(value)
            file.close()
        time.sleep(0.5)
        subprocess.call("rm -f core.*", shell=True)
        os.chdir("..")
    time.sleep(5)
    if chk_gpu_error():
        delete_finished_metric(metric)
        break


