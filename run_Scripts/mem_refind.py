import string
import os
import subprocess
import math
import re
import sys
import time
import glob
import numpy as np
from random import shuffle
# ====================================== Configuration ========================================

type = "risky"
arch = "K40"
fileName = arch + "_memtrace_resecue_risky.txt"

re_runList = []

def get_apps():
    apps = []
    fin = open("./applications_%s.csv"%(type),"r")
    for line in fin.readlines():
        if not line.startswith('#'):
            words = line.split(',')
            if words[-1] == '\n':
                del words[-1]
            app = words[0].strip()
            app_num = words[1].strip()
            apps.append([app,app_num,line])
    fin.close()
    return apps 


re_runList = []
app_list = get_apps()
with open(fileName, "r") as f:
    for line in f.readlines():
        for app_item in app_list:
            app_name = app_item[0] + str(app_item[1])
            if app_name == line.split('/')[-1].split('.')[0]:
                re_runList.append(app_item)

outFileName =  arch + "_memtrace_rerun_risky.csv"   
with open(outFileName, "w+") as f:
    for i in re_runList:
        f.write(i[2])
 
    f.close()
