import string
import os
import subprocess
import math
import re
import sys
import time
import glob
from random import shuffle
import sys
# ====================================== Configuration ========================================
DEVICE=0
type= os.environ['BENCHTYPE']  
applications_file="./applications_%s.csv"%(type)
if len(sys.argv) >=2:
    applications_file=sys.argv[1]

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



def get_a_power(app, exe, fileName):
    os.environ['COMPUTE_PROFILE'] = "0"
    cmd = str("nvidia-smi -i ") + str(DEVICE) + " --loop-ms=50 --format=csv --query-gpu=power.draw,memory.used,utilization.gpu,utilization.memory"

    with open(fileName, 'w+') as out:
        print(cmd.split())
        p = subprocess.Popen(cmd.split(), stdout=out)
        start = time.time()
        exe = "timeout 360 " + exe 
        subprocess.run(exe.split())
        end = time.time()
        elapsed = end - start
        p.kill()        
        out.write(str(elapsed))        
        out.close()

    print(app)

def get_finishList(pathfolder, fileType):

    owd = os.getcwd()
    os.chdir(pathfolder)
    app_lists = [ f.split('.')[0] for f in glob.glob("*.%s"%fileType) ]

    os.chdir(owd)
    return app_lists

#finished_list = get_finishList(r"/home/pzou/projects/Power_Signature/results/mybench/P100/node0691-2019-05-06-14-54", "pwr.txt")

apps = get_apps()
#shuffle(apps)

benchFolder = os.environ['BENCHDIR']
resultFolder = os.environ['TMPDIR']
for ar in apps:
    app = ar[0]
    app_num = int(ar[1])
    exe = ar[2]
   # if app+str(app_num) in finished_list:
   #     continue
   
    os.chdir(os.path.join(benchFolder, type))
    os.chdir(app)   
    fileName=os.path.join(resultFolder, "%s%d.pwr.txt"%(app,app_num))
    get_a_power(app,exe, fileName)
    subprocess.call("rm -f core.*", shell=True)
    os.chdir("..")
    time.sleep(10)
