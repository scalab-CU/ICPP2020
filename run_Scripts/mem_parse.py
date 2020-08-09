import sys
import glob
import csv
import os
import subprocess
import getopt
import numpy
from operator import add
# ====================================== Configuration ========================================
DEVICE = 0
arch = "Pascal"
gpu = "P100"
def get_apps():
    apps = []
    fin = open("./applications.csv","r")
    for line in fin.readlines():
        if not line.startswith('#'):
            words = line.split(',')
            #print(words)
            app = words[0].strip()
            exe = str("./") + words[1].strip()
            if len(words) == 4:
                exe += " " + words[2].strip()
            if len(words) == 3:
                ker = words[2].strip()
            elif len(words) == 4:
                ker = words[3].strip()
            apps.append([app,exe,ker])
    fin.close()
    return apps 

def get_forward_overlap(row, i, start_idx, duration_idx, name_idx, device_idx):
    start_time = float(row[i][start_idx])
    end_time   = start_time + float(row[i][duration_idx])
    overlap_time = [0.0, 0.0, 0.0, 0.0]
    j = i + 1
    while (j < len(row)):
        start_time_j = float(row[j][start_idx])
        end_time_j   = start_time_j + float(row[j][duration_idx])
        if (start_time_j < end_time):
            
            if (row[i][device_idx] == row[j][device_idx]):
                #print("overlap")
                overlap = min(end_time, end_time_j) - start_time_j
                if row[j][name_idx] == '[CUDA memcpy HtoD]':
                    overlap_time[1] += overlap
                elif row[j][name_idx] == '[CUDA memcpy DtoH]':
                    overlap_time[2] += overlap
                elif row[j][name_idx] == '[CUDA memcpy DtoD]':
                    overlap_time[3] += overlap
                else:
                    overlap_time[0] += overlap
        else:
            break
        j += 1
    return overlap_time

def main(pathfolder, app):

 
    filename = "{}/{}.mem_output".format(pathfolder, app)
    comp_time = 0.0
    h2d_time  = 0.0
    d2h_time  = 0.0
    d2d_time  = 0.0

    # index
    start       = 0
    duration    = 0
    size        = 0
    throughtput = 0
    device      = 0
    context     = 0
    stream      = 0
    name        = 0

    T = 4
 
    time_avg = [0.0, 0.0, 0.0, 0.0]
    olap_avg = []
    for t in range(T):
            olap_avg.append([0.0, 0.0, 0.0, 0.0])
    ndev = 0

    #dev_count  = int(argv[1])

    with open(filename) as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            #print(row)
            if ('Start' in row):
                #print(row)
                start      = row.index('Start')
                duration   = row.index('Duration')
                size       = row.index('Size')
                throughput = row.index('Throughput')
                device     = row.index('Device')
                context    = row.index('Context')
                stream     = row.index('Stream')
                name       = row.index('Name')
                break
        print ('Get index: Start({}), Duration({}), Size({}), Throughput({}), Device({}), Context({}), Stream({}), Name({})'.format( start, duration, size, throughput, device, context, stream, name ))
        
        ndev = 0
        row = []
        for r in reader:
            row.append(r)
        
        time = {}
        time_K = []
        time_H_D = []
        time_D_H = []
        time_D_D = []
        
        olap = {}

        for i in range(len(row)):
            if (len(row[i]) > 10 and row[i][start] != 'Start' and not 's' in row[i][start]):
                d = row[i][device]
                
                if not d in time:
                    ndev += 1
                    time[d] = [0.0, 0.0, 0.0, 0.0]
                    olap[d] = []
                    for t in range(T):
                        olap[d].append([0.0, 0.0, 0.0, 0.0])
                type = ''
                if row[i][name] == '[CUDA memcpy HtoD]':
                    type = 1
                    time_H_D.append([float(row[i][start]), float(row[i][duration])])
                elif row[i][name] == '[CUDA memcpy DtoH]':
                    type = 2
                    time_D_H.append([float(row[i][start]), float(row[i][duration])])
                elif row[i][name] == '[CUDA memcpy DtoD]':
                    type = 3
                    time_D_D.append([float(row[i][start]), float(row[i][duration])])
                else:
                    type = 0
                    time_K.append([float(row[i][start]), float(row[i][duration])])

                time[d][type] += float(row[i][duration])               
                overlap = get_forward_overlap(row, i, start, duration, name, device)
                for t in range(T):
                    olap[d][type][t] += overlap[t]
                    olap[d][t][type] += overlap[t]

        olap_p = {}
        print("done parsing")
        
        
        time_H_D = numpy.asarray(time_H_D)
        time_D_H = numpy.asarray(time_D_H)
        time_D_D = numpy.asarray(time_D_D)
        print(time_D_D)
        time_K = numpy.asarray(time_K)
        
        # calculate percentage
        for d, v in time.items():
            olap_p[d] = []
            for a in range(T):
                olap_p[d].append([])
                for b in range(T):
                    if (time[d][a] > 0):
                        olap_p[d][a].append(olap[d][a][b]/time[d][a])
                    else:
                        olap_p[d][a].append(0.0)
       
        # calculate average
        for d, v in time.items():
            time_avg  = list(map(add, time_avg, time[d]))
            for t in range(T):
                olap_avg[t] = list(map(add, olap_avg[t], olap_p[d][t]))
    repeat=1
    for t in range(4):
        time_avg[t] /= (ndev * repeat)
    for a in range(T):
        for b in range(T):
            olap_avg[a][b] /= (ndev * repeat)
            
    with open("{}/{}.H_D.csv".format(pathfolder, app), "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["start", "duration"])
        if len(time_H_D):
            for i in range(len(time_H_D[:,0])):
                csvwriter.writerow([time_H_D[i,0], time_H_D[i,1] ])
            
        csvfile.close()
            
    with open("{}/{}.D_H.csv".format(pathfolder, app), "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["start", "duration"])
        if len(time_D_H):
            for i in range(len(time_D_H[:,0])):
                csvwriter.writerow([time_D_H[i,0], time_D_H[i,1] ])
            
        csvfile.close()
        
    with open("{}/{}.D_D.csv".format(pathfolder, app), "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["start", "duration"])
        if len(time_D_D):
            for i in range(len(time_D_D[:,0])):
                csvwriter.writerow([time_D_D[i,0], time_D_D[i,1] ])
            
        csvfile.close()
        
        
    with open("{}/{}.K.csv".format(pathfolder, app), "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["start", "duration"])
        if len(time_K):
            for i in range(len(time_K[:,0])):
                csvwriter.writerow([time_K[i,0], time_K[i,1] ])
            
        csvfile.close()

    with open("{}/{}.olap.csv".format(pathfolder, app), "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow([" ", "Kernel","HtoD", "DtoH", "DtoD"])  
        csvwriter.writerow(["Kernel", olap_avg[0][0], olap_avg[0][1], olap_avg[0][2], olap_avg[0][3]])
        csvwriter.writerow(["HtoD", olap_avg[1][0], olap_avg[1][1], olap_avg[1][2], olap_avg[1][3] ])
        csvwriter.writerow(["DtoH", olap_avg[2][0], olap_avg[2][1], olap_avg[2][2], olap_avg[2][3] ])
        csvwriter.writerow(["DtoD", olap_avg[3][0], olap_avg[3][1], olap_avg[3][2], olap_avg[3][3] ])
        
        csvfile.close()
    # print("|-> Kernel: ", time_avg[0])
    # print("|-> HtoD: ", time_avg[1])
    # print("|-> DtoH: ", time_avg[2])
    # print("|-> DtoD: ", time_avg[3])
    # print("Overlap:")
    # print("          Kernel     HtoD      DtoH      DtoD")
    # print("Kernel   %.6f  %.6f  %.6f  %.6f" % (olap_avg[0][0], olap_avg[0][1], olap_avg[0][2], olap_avg[0][3]))
    # print("HtoD     %.6f  %.6f  %.6f  %.6f" % (olap_avg[1][0], olap_avg[1][1], olap_avg[1][2], olap_avg[1][3]))
    # print("DtoH     %.6f  %.6f  %.6f  %.6f" % (olap_avg[2][0], olap_avg[2][1], olap_avg[2][2], olap_avg[2][3]))
    # print("DtoD     %.6f  %.6f  %.6f  %.6f" % (olap_avg[3][0], olap_avg[3][1], olap_avg[3][2], olap_avg[3][3]))


if __name__ == "__main__":
    pathfolder="/home/pzou/projects/Power_Signature/results/mybench/node0249-2019-03-10-19-45"
    for app in get_apps():
        print(app[0])
        main(pathfolder, app[0])
