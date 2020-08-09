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
import glob
import csv
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import sklearn.svm 
import sklearn.metrics
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.neural_network import MLPClassifier
from matplotlib.animation import FuncAnimation
import pickle
import subprocess
import multiprocessing  
import time
import tensorflow as tf
from tensorflow import feature_column
from tensorflow.keras import layers
import h5py
import matplotlib.cm as cmx
import matplotlib.colors as colors
from tensorflow.keras import backend as K

def load_resource_file(filepath, max_len):
    
    dataframe = pd.read_csv(filepath, index_col=0)
    if (dataframe.shape[1] == 4 and dataframe.shape[0] >=max_len):
        #if dataframe["u_gpu"].sum() == 0:
            #os.remove(filepath)
        #    print(filepath)
        #else:
        return dataframe.values[:max_len,:]
    else:
        print(filepath)
        
def drawResource(app, q):
    
    
    
    fig =  plt.figure()
    fig.set_size_inches(8, 6)  
    sample_rate = 0.1
    
    x_len = 80
    
    ax1 = fig.add_subplot(3, 1, 1)   
    ax1.set_ylim([0, 250])
    ax1.set_xlim([0, x_len])
    ax1.set_ylabel("Watts")
    
    
    ax2 = fig.add_subplot(3, 1, 2)       
    ax2.set_ylim([0, 120])
    ax2.set_xlim([0, x_len])
    ax2.set_ylabel("%")
    
    
    ax3 = fig.add_subplot(3, 1, 3)       
    ax3.set_ylim([0, 120])
    ax3.set_xlim([0, x_len])
    ax3.set_ylabel("%")
    
   # plt.show()
    
    fig.suptitle('%s'%app, fontsize=16)
    
    
    # sample_rate = 0.1  
    # data = np.asarray(data)
    # power = data[:,0]
    # gpu_utili = data[:, 1]
    # mem_utili = data[:, 2]
    
    # x= range(len(power))
    # x = [i*sample_rate for   i in x] 
    
    
    line1, = ax1.plot([], [], ls = '-.', color="C1", lw=2) 
    line2, = ax2.plot([], [], ls = '-.', color="C2", lw=2) 
    line3, = ax3.plot([], [], ls = '-.', color="C4", lw=2) 
    
    txt1 = ax1.text(0, 0, 'Power', color="C1")
    txt2 = ax2.text(0, 0,  'Graphic Unti.', color="C2")    
    txt3 = ax3.text(0, 0,  'Mem. Util.', color="C3")  
    
    
    # line1, = ax1.plot(x, power, ls = '-.', color="C1", lw=2) 
    # line2, = ax2.plot(x, gpu_utili, ls = '-.', color="C2", lw=2) 
    # line3, = ax3.plot(x, mem_utili, ls = '-.', color="C4", lw=2) 
    
    # txt1 = ax1.text(x[-1]+0.5, power[-1], 'Power', color="C1")
    # txt2 = ax2.text(x[-1]+0.5, gpu_utili[-1], 'Graphic Unti.', color="C2")    
    # txt3 = ax3.text(x[-1]+0.5, mem_utili[-1], 'Mem. Util.', color="C3")  
    #time.sleep( 5)
    
    quedata = []
    max_len = int(x_len/sample_rate)-1
    def animate(i):
        nonlocal max_len
        while not q.empty():
            quedata.append(q.get())
        #datafileName = "/home/pzou/projects/Power_Signature/results/demo/CoMD1.pwr.txt"
        #quedata = np.genfromtxt(datafileName, skip_header =1 )    
        
        if i == max_len:
            plt.pause(2)
            plt.close(fig)
            
        data = np.asarray(quedata)
        
        if data[-1, 0] == -1:
            max_len = len(data[:, 0]) -1
            data = data[:max_len, :]
        
        if i <= len(data[:, 0]):
            y1 = data[:i,0]
            y2 = data[:i,2]
            y3 = data[:i,3]
            
            x_temp = [j * sample_rate for j in range(i)]
            line1.set_data(x_temp, y1)
            line2.set_data(x_temp, y2)
            line3.set_data(x_temp, y3)
            
            txt1.set_position((x_temp[-1]+0.5, y1[-1]))
            txt2.set_position((x_temp[-1]+0.5, y2[-1]))
            txt3.set_position((x_temp[-1]+0.5, y3[-1]))
            ax3.set_xlabel("Time %.1fs"%(i*sample_rate), fontsize=14)
            return line1, line2, line3, txt1, txt2, txt3, ax3
      
    anim = FuncAnimation(fig, animate, 
                               frames=np.arange(1, int(x_len/sample_rate)), interval=100 , repeat=False)
    #line1.set_data(x, power)
    plt.show()
    
    #fig.set_size_inches(16, 12)   

def drawAccuracy(memacc, resacc, fusionacc, app):
    fig =  plt.figure()
    fig.set_size_inches(8, 6)  
    ax1 = fig.add_subplot(1, 1, 1)  
    if memacc < 0.5:
        txt1 = ax1.text(0.5, 0.25, 'Classified WITH data movement trace: Authorized', color="k", horizontalalignment='center', fontsize= 14)
    else:
        txt1 = ax1.text(0.5, 0.25, 'Classified WITH data movement trace: Unauthorized', color="r", horizontalalignment='center', fontsize= 14)
        
    if resacc < 0.5: 
        txt2 = ax1.text(0.5, 0.5, 'Classified WITH resource trace: Authorized',  color="k", horizontalalignment='center', fontsize= 14)    
    else: 
        txt2 = ax1.text(0.5, 0.5, 'Classified WITH resource trace: Unauthorized',  color="r", horizontalalignment='center', fontsize= 14) 
    
    if fusionacc < 0.5:
        txt3 = ax1.text(0.5, 0.75, 'Classified WITH Combine trace: Authorized',  color="k", horizontalalignment='center', fontsize= 14)  
    else: 
        txt3 = ax1.text(0.5, 0.75, 'Classified WITH Combine trace: Unuthorized',  color="r", horizontalalignment='center', fontsize= 14)  
        
    ax1.set_ylim([0, 1])
    ax1.set_xlim([0, 1])
    
    fig.suptitle('%s'%app, fontsize=16)
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])
    plt.show(block=False)
    plt.pause(8)
    #time.sleep(10)
    plt.close()


def drawMem(app, resultfolder):
    memfileName = os.path.join(resultfolder, "%s.mem_output"%app)
    trace = trace_read_C(memfileName)
    df = pd.DataFrame(trace, columns=['start', 'duration',  "H2D",  "D2H", "D2D", "throughput"])
    fig =  plt.figure()
    vmin = min(df['throughput'].values[:])
    vmax = max(df['throughput'].values[:])
    jet = cm = plt.get_cmap('jet') 
   # tmax = df['start'].values[-1] + df['duration'].values[-1]
    tmin = 0
    cNorm  = colors.Normalize(vmin=vmin, vmax=vmax)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    ax1 = fig.add_subplot(1, 1, 1)
    fig.suptitle("%s's data movement trace"%app, fontsize=16)
    fig.set_size_inches(8, 6) 
    max_len = min(200, df.shape[0])
    tmax = df['start'].values[max_len-1] + df['duration'].values[max_len-1]
    for i in range(max_len):
        x1= df['start'][i]
        du = df['duration'][i]
        y1 = df['H2D'][i] * 2 + df['D2H'][i] 
        th = df['throughput'][i]
        colorVal = scalarMap.to_rgba(th)
        #print(x1,du,y1)
        ax1.add_patch(patches.Rectangle(  (x1, y1 + 0.15), du , 0.7, facecolor= colorVal, fill= (th!=0)))
        
        ax1.set_xlim([tmin, tmax])

        ax1.set_yticks([0.5,1.5,2.5])
        ax1.set_yticklabels(["Kernel",  "D2H", "H2D"])
        ax1.set_ylim([0,3])
     
        plt.subplots_adjust(hspace=0.08)
    
    fig.subplots_adjust(right=0.9)
    scalarMap.set_array([])
    cbar_ax = fig.add_axes([0.91, 0.15, 0.03, 0.7])
    fig.colorbar(scalarMap, label='Throughput (GB/s)' ,cax=cbar_ax)   
    plt.show(block=False)
    plt.pause(6)
    #time.sleep(10)
    plt.close()
    
    
def calAccuracy(resultfolder, app ,resmodel, memmodel, fusionmodel ):

    drawMem(app, resultfolder)
    resfileName = os.path.join(resultfolder, "%s.pwr.txt"%app)
    memfileName = os.path.join(resultfolder, "%s.mem_output"%app)
    
    resacc = predict_resource(resfileName, resmodel)
    memacc = predict_mem(memfileName, memmodel)
    fusionacc = predict_fusion(memfileName, resfileName, fusionmodel)
    drawAccuracy(memacc, resacc, fusionacc, app)
    
def realTimeDraw(ax1, ax2, ax3, data):
    sample_rate = 0.1  
    data = np.asarray(data)
    power = data[:,0]
    gpu_utili = data[:, 1]
    mem_utili = data[:, 2]
    
    x= range(len(power))
    x = [i*sample_rate for   i in x] 
    
    line1, = ax1.plot(x, power, ls = '-.', color="C1", lw=2) 
    line2, = ax2.plot(x, gpu_utili, ls = '-.', color="C2", lw=2) 
    line3, = ax3.plot(x, mem_utili, ls = '-.', color="C4", lw=2) 
    
    txt1 = ax1.text(x[-1]+0.5, power[-1], 'Power', color="C1")
    txt2 = ax2.text(x[-1]+0.5, gpu_utili[-1], 'Graphic Unti.', color="C2")    
    txt3 = ax3.text(x[-1]+0.5, mem_utili[-1], 'Mem. Util.', color="C3")  
    
    plt.draw()
    plt.pause(0.001)
    
def run_program(app,  exe, type,  app_folder, resultfolder, q):


    os.chdir(os.path.join(app_folder, type))
    os.chdir(app)
    
    #subprocess.Popen(['ls', '-l'])
    i=0
    data = []
    fileName=os.path.join(resultfolder, "%s.mem_output"%(app))
    exe = "/software/cuda-toolkit/9.0.176/bin/nvprof --csv --normalized-time-unit s --print-gpu-trace --log-file " + fileName + " " + exe 
    print(exe)
    for output in get_a_power(app, exe, resultfolder):
        print(output, end="")
        i+=1
        
        if i == 1:
            continue
        temp = output.split()
        q.put([float(temp[0]),float(temp[2]), float(temp[4]), float(temp[6])] )    
        data.append([float(temp[0]), float(temp[2]), float(temp[4]), float(temp[6])])
    q.put([-1,-1,-1,-1])
    data = np.asarray(data)
    np.savetxt(os.path.join(resultfolder, "%s.pwr.txt"%app), data)
       
    
    
def get_a_power(app, exe, resultfolder):
    os.environ['COMPUTE_PROFILE'] = "0"
    cmd = str("nvidia-smi -i 0") + " --loop-ms=100 --format=csv --query-gpu=power.draw,memory.used,utilization.gpu,utilization.memory"

    p = subprocess.Popen(exe.split(), stdout=subprocess.PIPE)
    #os.spawnl(os.P_NOWAIT, exe)
    #p._internal_poll(_deadstate='dead')
    #p.popen()
    
    smi = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)

    
  
    for stdout_line in iter(smi.stdout.readline, ""):
        if p.poll() == None :
            yield stdout_line 
        else:

         
            break
    smi.stdout.close()
    return_code = smi.wait()
    

def predict_resource(resfileName, model):
    #arch = "p100"
    data = np.loadtxt(resfileName)
    #checkpoint_path = "/home/pzou/projects/Power_Signature/results/data_analysis/%s/resourceAll-256-%s.hdf5"%(arch,arch)
    #model = tf.keras.models.load_model(checkpoint_path)  

    f = h5py.File(checkpoint_path, 'r')
    print(f.attrs.get('keras_version'))
        
    model = tf.keras.models.load_model(checkpoint_path)      
    min_len= 1800

    
    while (len(data[:,0])< min_len):
            data = np.concatenate((data,data), axis=0)
    data = data[:min_len,:]
    
    df = pd.DataFrame(data)
    temp = []
    temp.append(df.values[:,:])
    #temp.append(df.values[:,:])
    temp = np.asarray(temp)
    
    acc = model.predict(temp)
    print(acc)
    return acc[0][0]
    
def trace_read_C(fileName):
    # index
    start       = 0
    duration    = 0
    size        = 0
    throughtput = 0
    device      = 0
    context     = 0
    stream      = 0
    name        = 0

    trace = []
    
    with open(fileName) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            #print(row)
            if ('Start' in row):
                if ('Throughput' not in row):
                    return [-1,-1,-1,-1] 
                #print(row)
                start      = row.index('Start')
                duration   = row.index('Duration')
                name       = row.index('Name')
                throughput = row.index('Throughput')

                break
               
        ndev = 0
        row = []
        for r in reader:
            row.append(r)
        
        time = 0.0
        time_K = 0.0
        time_H_D = 0.0
        time_D_H = 0.0
        time_D_D = 0.0
        
        for i in range(len(row)):
            if (len(row[i]) > 10 and row[i][start] != 'Start' and not 's' in row[i][start]):
                
                if 'HtoD' in row[i][name] :
                    time_H_D += float(row[i][duration])
                    if row[i][throughput] =='':
                        continue
                    trace.append([float(row[i][start]), float(row[i][duration]), 1, 0, 0, float(row[i][throughput])])
                elif 'DtoH' in row[i][name]  :
                    if row[i][throughput] =='':
                        continue
                    time_D_H += float(row[i][duration])
                    trace.append([float(row[i][start]), float(row[i][duration]), 0, 1, 0, float(row[i][throughput])])
                elif 'DtoD' in row[i][name]  :
                    if row[i][throughput] =='':
                        continue
                    time_D_D += float(row[i][duration])
                    trace.append([float(row[i][start]), float(row[i][duration]), 0, 0, 1, float(row[i][throughput])])
                else:
                    if len(row[i][duration]):
                        time_K += float(row[i][duration])
                        trace.append([float(row[i][start]), float(row[i][duration]),0,0,0, 0])
        time = time_K + time_D_D + time_D_H + time_H_D
        

        f.close()
    return trace
def predict_mem(fileName, model):
    trace = trace_read_C(fileName)
    df = pd.DataFrame(trace)
    
    max_len = 64
    
    while (df.shape[0] < max_len):
            df = pd.concat([df, df])
            
    #arch = "p100"     
    #checkpoint_path = "/home/pzou/projects/Power_Signature/results/data_analysis/%s/memTrace-%s.hdf5"%(arch,arch)
    #model = tf.keras.models.load_model(checkpoint_path)    
        
  
    temp = []
    temp.append(df.values[:max_len,:])
    #temp.append(df.values[:,:])
    temp = np.asarray(temp)
    
    acc = model.predict(temp)
    print(acc)
    return acc[0][0]
    
def predict_fusion(memfileName, resfileName, model):
    trace = trace_read_C(memfileName)
    df = pd.DataFrame(trace)
    max_len = 64
    while (df.shape[0] < max_len):
          df = pd.concat([df, df])
    memdata = []
    memdata.append(df.values[:max_len,:])
    
    min_len= 1800
    resoureData= np.loadtxt(resfileName)
    while (len(resoureData[:,0])< min_len):
            resoureData = np.concatenate((resoureData,resoureData), axis=0)
    resoureData = resoureData[:min_len,:]
    df = pd.DataFrame(resoureData)
    resourcedata = []
    resourcedata.append(df.values[:,:])
    
    #arch = "p100"
    #checkpoint_path = "/home/pzou/projects/Power_Signature/results/data_analysis//%s/%s-%s.hdf5"%(arch,"fusion" ,arch)
    
    
    
    model = tf.keras.models.load_model(checkpoint_path)  
    
    
    temp = [ resourcedata, memdata]
    acc =  model.predict(temp)
    print(acc)
    return acc[0][0]
if __name__ == '__main__':
    resultfolder = '/home/pzou/projects/Power_Signature/results/demo'
    app_list = ["matrixMul", "cdpLUDecomposition", "des", "bitcracker"]#
    exe_list = [ "./matrixMul -wA=4096 -hA=4096 -wB=4096 -hB=4096", "./cdpLUDecomposition --matrix_size=16000", "./des --cipher 0x6473646273646134 --key-alphabet abes --key-length 7 --text-alphabet abcdefg --text-length 7 --gpu",  "./build/bitcracker_cuda -f ./test_hash/imgWin8_recovery_password.txt -d ./Dictionary/recovery_passwords.txt -b 256 -r"]
    #
    type_list = ["mybench", "mybench", "risky", "risky" ]
    app_folder = '/scratch3/pzou/Power_Signature/monitor_peng'
    
    #app = "BlackScholes1" #"BlackScholes1", "cdpLUDecomposition1",   "matrixMul9", "quasirandomGenerator8", "CoMD7"
    # benchfile = '/home/pzou/projects/Power_Signature/Scripts/applications-mem_mybench.csv'
    # databench = pd.read_csv(benchfile)
    
    config = tf.ConfigProto(device_count = {'GPU': 0}    )    
    sess = tf.Session(config=config)
    K.set_session(sess)
    # with tf.device('/cpu:0'):
    arch = "p100"
    checkpoint_path = "/home/pzou/projects/Power_Signature/results/data_analysis//%s/%s-%s.hdf5"%(arch,"fusion" ,arch)
    fusionmodel = tf.keras.models.load_model(checkpoint_path)    
    
    checkpoint_path = "/home/pzou/projects/Power_Signature/results/data_analysis/%s/memTrace-%s.hdf5"%(arch,arch)
    memmodel = tf.keras.models.load_model(checkpoint_path)    
    

    checkpoint_path = "/home/pzou/projects/Power_Signature/results/data_analysis/%s/resourceAll-256-%s.hdf5"%(arch,arch)
    resmodel = tf.keras.models.load_model(checkpoint_path)  
        
    i=3
    q = multiprocessing.Queue() 
    
    app = app_list[i]
    exe = exe_list[i]
    type = type_list[i]
    
    datapro = multiprocessing.Process(target = run_program, args = (app,  exe, type,  app_folder, resultfolder, q))
    graph = multiprocessing.Process(target = drawResource, args=(app, q))

    datapro.start()
    graph.start()  
    datapro.join()       
    graph.join() 
    
    calAccuracy(resultfolder, app, resmodel, memmodel, fusionmodel)
       # time.sleep(5)
    
    #drawMem(app, resultfolder)
    #drawAccuracy(0.7, 0.7, 0.7)
 
    #filepath = os.path.join(resultfolder, "%s.pwr.txt"%app_list[0] )

#drawResource(filepath)