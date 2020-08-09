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
import pandas as pd
# ====================================== Configuration ========================================

DEVICE=0
NVPROFPATH = os.environ['NVPROFPATH']
type= os.environ['BENCHTYPE']
arch = os.environ['ARCH']

errorFile = "perfError-%s-%s.csv"%(type, arch)
errorFile = os.path.join(r"/home/pzou/projects/Power_Signature/results/data_analysis", errorFile)
applications_file="./applications_%s.csv"%(type)


def get_apps():
    apps = {}
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
            apps[app+str(app_num)] =[app, app_num, exe]
    fin.close()
    return apps 

def get_error_metric():
    df = pd.read_csv(errorFile, header=0)
    df =df.drop(df[df["errorType"] == "No metric"].index)
    return df


def get_a_metric(app, exe, metric):
    os.environ['COMPUTE_PROFILE'] = "0"
    cmd = NVPROFPATH + str(" --csv ") + \
            " --metrics " + str(metric) + " --timeout 1800 " + exe 
    print(cmd)
    temp = subprocess.run(cmd.split(),stderr=subprocess.PIPE)
    #print(temp)
    values= temp.stderr.decode()
    
    return values

apps = get_apps()

error_metrics = get_error_metric()



#finished_list = get_finishList(r"/home/pzou/projects/Power_Signature/results/mybench/P100/node0017-2019-04-24-21-41", "csv")

def chk_gpu_error():
    out = subprocess.check_output(['nvidia-smi'])
    if 'ERR!' in out.decode():
        return True
    else:
        return False
for app_id in apps.keys():

    resultFolder = os.environ['TMPDIR']
    if not os.path.exists(os.path.join(resultFolder, app_id)):
        os.mkdir(os.path.join(resultFolder, app_id))
   
   
   
benchFolder = os.environ['BENCHDIR']   
resultFolder = os.environ['TMPDIR']
for index, row in error_metrics.iterrows():
    if chk_gpu_error():
        break
    print(row)
    
    app_id =row[0]
    app = apps[app_id][0]
    app_num = apps[app_id][1]
    exe = apps[app_id][2]
    mtc = row[1]
    os.chdir(os.path.join(benchFolder, type, app))

    fileName=os.path.join(resultFolder, app+str(app_num), "%s.perf.txt"%(mtc))
    value = get_a_metric(app, exe,  str(mtc)) #profile a metric
    with open(fileName, 'w+') as file:            
        file.write(value)
        file.close()
    time.sleep(0.5)
    subprocess.call("rm -f core.*", shell=True)


    


