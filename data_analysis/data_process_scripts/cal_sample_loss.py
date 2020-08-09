import os
import sys
import re
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import openpyxl
import pandas as pd
import math
import itertools
import matplotlib.patches as patches
import seaborn as sns
import statistics


def get_app_list(fileName):
    """get metrics list

    Arguments:
        fileName {string} -- the file name of application file with absolute path

    Returns:
        app {list} -- the app  list
    """
    apps = []
    with open(fileName) as f:
        for line in f.readlines():
            if not line.startswith('#'):
                words = line.strip().split(',')
                app = words[0].strip()
                app_num = words[1].strip()
                apps.append([app, app_num])
        f.close()
    return apps


def get_fileLen(filepath):
    dataframe = pd.read_csv(filepath, index_col=0)
    if (dataframe.shape[1] == 4):
        #if dataframe["u_gpu"].sum() == 0:
            #os.remove(filepath)
        #    print("none", filepath)
        #else:
        return dataframe.shape[0]
   

def load_group(sample_rate):

    est_len = 6 * 60 * 1000 // sample_rate
    
    outFile = "combine_results/sample_rate%d.xlsx"%sample_rate
    writer = pd.ExcelWriter(outFile,engine='xlsxwriter')
    for arch in ["k40", "p100", "v100"]:
        y_label = []
        app_label = []
        data_group = []
        category = "mybench"
        pathfolder = '/home/pzou/projects/Power_Signature/results-%d/%s/%s/power-combine'%(sample_rate, category, arch)
        app_list = app_list = get_app_list("/home/pzou/projects/Power_Signature/Scripts/applications-mem_%s.csv"%(category))
        for [app, app_num] in app_list:
            if arch=="k40" and "reductionMultiBlockCG" in app:
                continue
            fileName =app+app_num+"_res.csv"
            sam_rate = get_fileLen(os.path.join(pathfolder, fileName)) / est_len
            data_group.append([app+app_num, sam_rate])


        category = "risky"
        pathfolder = '/home/pzou/projects/Power_Signature/results-%d/%s/%s/power-combine'%(sample_rate, category, arch)
        app_list = app_list = get_app_list("/home/pzou/projects/Power_Signature/Scripts/applications-mem_%s.csv"%(category))
        for [app, app_num] in app_list:
            fileName =app+app_num+"_res.csv"
            sam_rate = get_fileLen(os.path.join(pathfolder, fileName)) / est_len
            data_group.append([app+app_num, sam_rate])

        df = pd.DataFrame(data = data_group, columns = ["app", "rate"])
        df.to_excel(writer, sheet_name=arch, index=False)

        
    writer.save()

if __name__=="__main__":
    for sample_rate in [100, 50, 10]:
        load_group(sample_rate)
