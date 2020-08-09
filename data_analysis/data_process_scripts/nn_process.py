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


cg_index = [501, 502, 503, 504, 505, 506, 507, 508, 509]
train_end = 683

def read_testAccuracy(fileM, model_eval):

    datafileName = "%s-%s-testAccuracy.xlsx"%(fileM, model_eval)
    ratios = [1, 2, 5, 8, 10, 20, 50]
    ratios = [8]
    pathfolder = "combine_results"

    writer = pd.ExcelWriter(os.path.join(pathfolder,datafileName),engine='xlsxwriter')
    for arch in ["p100"]:
        data = []

        for index_label in range(1, 6):
            row = []
            for ratio in ratios:
                fileName = "%s/%s-%s-%s-%d-W%d-testAccurcy.txt"%(arch,fileM ,arch, model_eval, index_label, ratio)
                if os.path.exists(fileName):
                    with open(fileName) as f:
                        row.append(float(f.readline()))
                        f.close()
                else:
                    print(fileName)
                    row.append(-1)
            data.append(row)
        data = np.asarray(data)
        dicData={}
        dicData["index"] = range(1, 6)
        for i in range(len(ratios)):
            dicData[ratios[i]] = data[:, i]
        dfData = pd.DataFrame(dicData, columns= ["index"] + ratios)
        dfData.to_excel(writer, sheet_name= arch, index=False)
    writer.close()

def read_CM(fileM, model_eval):
    datafileName = "%s-%s-testCM.xlsx"%(fileM, model_eval)
    ratios = [1, 2, 5, 8, 10, 20, 50]
    ratios = [8]
    pathfolder = "combine_results"

    writer = pd.ExcelWriter(os.path.join(pathfolder,datafileName),engine='xlsxwriter')
    for arch in [ "p100"]:
        data = []

        for index_label in range(1, 6):
            row_tp = []
            row_fp = []
            row_fn = []
            row_tn = []
            row_fnr = []
            row_fpr = []
            row = []
            for ratio in ratios:
                fileName = "%s/%s-%s-%s-%d-W%d-test.csv"%(arch,fileM ,arch, model_eval, index_label, ratio)

                tp, fp, fn, tn, fpr, fnr = cal_FM(fileName, arch)
                row_tp.append(tp)
                row_fp.append(fp)
                row_fn.append(fn)
                row_tn.append(tn)

                row_fnr.append(fnr)
                row_fpr.append(fpr)


            row = [index_label] + row_fpr + [index_label] + row_fnr  + [index_label] + row_tp + [index_label] + row_fp + [index_label] + row_fn + [index_label] + row_tn
            data.append(row)
        data = np.asarray(data)
        dfData = pd.DataFrame(data, columns=  ["FPR"] + ratios +  ["FNR"] + ratios + ["TP"] + ratios+ ["FP"] + ratios + ["FN"] + ratios + ["TN"] + ratios )
        dfData.to_excel(writer, sheet_name= arch, index=False)
    writer.close()

def cal_FM(fileName, arch):
  
    data = pd.read_csv(fileName)
    real_label = data['y_real'].values
    predict_label = data['predict'].values


    n = len(real_label)
    if n != len(predict_label):
        print("error")
        return -1, -1, -1, -1, -1, -1


    total_true = 0
    total_false = 0

    tp = 0
    fp = 0
    fn = 0
    tn = 0
    for i in range(n):
        if real_label[i] == 1:
            total_true += 1
            if predict_label[i] == 1:
                tp += 1
            else:
                fn += 1
        else:

            total_false += 1
            if predict_label[i] == 1:
                fp += 1
            else:
                tn += 1

    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)
    return tp, fp, fn, tn, fpr, fnr

if __name__=="__main__":
    fileM = "nnPerf"
    model_eval = "seen"
    #fileM = "resAll-100"
    #for fileM in ["resAll-Inter-100", "Fusion", "DoubleLSTM", "resAll-100" ]: #"DoubleLSTM", "resAll-100", "resAll-Inter-100"
    for model_eval in ["seen", "unseen"]:
            read_testAccuracy(fileM, model_eval)
            read_CM(fileM, model_eval)
