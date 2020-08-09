
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
from decimal import Decimal
from csv import reader
import csv
from tsfresh import extract_features
from tsfresh import select_features
from tsfresh.utilities.dataframe_functions import impute
from tsfresh.utilities.distribution import MultiprocessingDistributor


def readGPU_power_C(fileName, outFile):
 
    data= []
    time_units =0.1

    with open(fileName) as f:
        next(f)
        t=0
        for line in f:
            temp = line.split(',')
            temp_row = [float(i.split()[0]) for i in temp]
            temp_row.insert(0, t)
            data.append(temp_row)
            t+=time_units

    columns= ["time", "power", "memory Used", "u_gpu", "u_memory"]
    df = pd.DataFrame(data=data, columns=columns)
    df.to_csv(outFile,index=False)
    print(outFile)
    
def get_app_list(fileName):
    """get metrics list

    Arguments:
        fileName {string} -- the file name of application file with absolute path

    Returns:
        app {list} -- the app  list
    """
    apps = []
    with open(fileName, "r") as f:
        for line in f.readlines():
            if not line.startswith('#'):
                words = line.strip().split(',')
                app = words[0].strip()
                app_num = words[1].strip()
                apps.append(app+app_num)
        f.close()
    return apps

def Combine_data(pathfolder, app_list, outFile):
    writer = pd.ExcelWriter(outFile,engine='xlsxwriter')
    data = []    
    i = 0
    for app in app_list:
        fileName =  os.path.join(pathfolder, "{}-ori.csv".format(app))
        data_temp = pd.read_csv(fileName)
        data_temp["app"] = app
        data_temp["ID"] = i
        data.append(data_temp)
        i+=1
        if  i%200 == 0 :        
            outData = pd.concat(data)    
            outData.to_excel(writer, sheet_name="{}-{}".format(i-199, i), index=False)
            data = []
        elif i==len(app_list):
            if i >= 200:
                x = i -199
            else:
                x=1
            outData = pd.concat(data)    
            outData.to_excel(writer, sheet_name="{}-{}".format(x, i), index=False)
    writer.save()

   
    
def readGPU_power(pathfolder, app_list):
    for app in app_list:
        fileName = os.path.join(pathfolder, "{}.pwr.txt".format(app))
        outFile = os.path.join(pathfolder, "{}.pwr.csv".format(app))
        readGPU_power_C(fileName, outFile)

def process_Data():
    category = "mybench"
    arch ="k40"
    #for arch in ["K40", "V100"]:
    pathfolder = r"/home/pzou/projects/Power_Signature/results/%s/%s/power-combine"%(category, arch)
    app_list = get_app_list("/home/pzou/projects/Power_Signature/Scripts/applications_%s.csv"%(category))
    #readGPU_power(pathfolder, app_list)
    outFile = "power-combine-%s-%s.xlsx"%(category, arch)
    print("start")
    Combine_data(pathfolder, app_list, outFile)
    print("Done")
    
def extractFeature(dataName, outName):

    Distributor = MultiprocessingDistributor(n_workers=16,
                                         disable_progressbar=False,
                                         progressbar_title="Feature Extraction")

    xlData = pd.ExcelFile(dataName)
    data = []
    for sheets in xlData.sheet_names:
        dataX = xlData.parse( sheet_name=sheets) 
        data.append(dataX)
    data = pd.concat(data)    
    dataX = data.drop(columns=["app"])
    extracted_features = extract_features(dataX, column_id="ID", column_sort="start", distributor=Distributor)
    extracted_features.to_csv(outName, index=False)

arch="k40"

category="mybench"
tFtype = "mem_trace-combine"
dataName = "{}-{}-{}.xlsx".format(tFtype, category,arch)
arch = "k40"
pathfolder = r"/home/pzou/projects/Power_Signature/results/%s/%s/mem_trace-combine"%(category, arch)
app_list = get_app_list("/home/pzou/projects/Power_Signature/Scripts/applications-mem_%s.csv"%(category))


print("start")
Combine_data(pathfolder, app_list, dataName)
print("done combine")
featureName = "{}-feature-{}-{}.csv".format(tFtype, category,arch)

extractFeature(dataName, featureName)
print("done feature")