import string
import os
import subprocess
import math
import re
import sys
import time
import glob
from random import shuffle
# ====================================== Configuration ========================================

DEVICE=0
NVPROFPATH = os.environ['NVPROFPATH']
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



def get_a_mem(app, app_num, exe, pathfolder):
    os.environ['COMPUTE_PROFILE'] = "0"
    cmd = NVPROFPATH +  " --csv --normalized-time-unit s --print-gpu-trace --timeout 1800 "+ exe 
  
    
    print(cmd.split())
    temp =subprocess.run(cmd.split() ,stderr=subprocess.PIPE)
    values= temp.stderr.decode()
    return values


apps = get_apps()
shuffle(apps)
benchFolder = os.environ['BENCHDIR']  
resultFolder = os.environ['TMPDIR']
for ar in apps:
    app = ar[0]
    app_num = int(ar[1])
    exe = ar[2]
    os.chdir(os.path.join(benchFolder,type))
    os.chdir(app)
    fileName=os.path.join(resultFolder, "%s.mem_output"%(app+str(app_num)))
    with open(fileName, 'w+') as file:
        value = get_a_mem(app, app_num,exe, resultFolder)  
        file.write(value)
        file.close()
    subprocess.call("rm -f core.*", shell=True)
    os.chdir("..")
    time.sleep(5)
