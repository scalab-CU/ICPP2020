
# coding: utf-8

# In[ ]:


# %%

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
import tensorflow as tf
from tensorflow import feature_column
from tensorflow.keras import layers
import pickle


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
                apps.append(app+app_num)
        f.close()
    return apps

def load_mem_file(filepath, max_len):
    dataframe = pd.read_csv(filepath, index_col=0)
    print(dataframe.shape)
    if (dataframe.shape[1] == 6 and dataframe.shape[0] ==max_len):
        #if dataframe["u_gpu"].sum() == 0:
            #os.remove(filepath)
        #    print(filepath)
        #else:
        return dataframe.values[:max_len,:]
    else:
        print(filepath)

def load_resource_file(filepath, max_len):
    
    dataframe = pd.read_csv(filepath, index_col=0)
    print(dataframe.shape)
    if (dataframe.shape[1] == 4 and dataframe.shape[0] ==max_len):
        #if dataframe["u_gpu"].sum() == 0:
            #os.remove(filepath)
        #    print(filepath)
        #else:
        return dataframe.values[:max_len,:]
    else:
        print(filepath)
def load_group(arch):
    y_label = []
    data_mem_group = []
    data_resource_group = []
    
    i=0
    for category in ["mybench", "risky"]:
        mem_pathfolder = '/home/pzou/projects/Power_Signature/results/%s/%s/mem_trace-combine'%(category, arch)
        resource_pathfolder = '/home/pzou/projects/Power_Signature/results/%s/%s/power-combine'%(category, arch)
        app_list = app_list = get_app_list("/home/pzou/projects/Power_Signature/Scripts/applications-mem_%s.csv"%(category))
        for app in app_list:
            fileName =app+".csv"
            data = load_mem_file(os.path.join(mem_pathfolder, fileName), mem_max_len)
            data_mem_group.append(data)

            fileName =app+".pwr.csv"
            data = load_resource_file(os.path.join(resource_pathfolder, fileName), res_max_len)
            data_resource_group.append(data)

            y_label.append(i)
        i+=1
    data_mem_group = np.asarray(data_mem_group)  
    data_resource_group = np.asarray(data_resource_group)  
    return data_group, y_label
    
res_max_len = 1200
mem_max_len = 64
arch="p100"

print("start")
load_group(arch)
print("done")
#%%
   


# In[ ]:


y_label = pd.Series(y_label)

X_res_train, X_res_test, y_train, y_test = train_test_split(data_resource_group, y_label, test_size=0.25, random_state=1)
train_index = y_train.index.tolist()
test_index = y_test.index.tolist()

X_mem_train = data_mem_group[train_index, :, :]
X_mem_test = data_mem_group[test_index, :, :]
X_train = [X_res_train, X_mem_train]
X_test = [X_res_test, X_mem_test]


inputRes = layers.Input(shape=(res_max_len,4))
inputMem = layers.Input(shape=(mem_max_len,6))

x = (layers.LSTM(256, input_shape=(res_max_len, 4)))(inputRes)
x = (layers.Dropout(0.4))(x)
x = (layers.Dense(128, activation='relu'))(x)
x = (layers.Dense(16, activation='relu'))(x)
x= Model(inputs=inputRes, outputs=x)


y = (layers.LSTM(32, input_shape=(mem_max_len, 6)))(inputMem)
y = (layers.Dropout(0.2))(y)
y = (layers.Dense(16, activation='relu'))(y)
y = Model(inputs=inputMem, outputs=y)


combine = concatenate([x.output, y.output])

out = layers.Dense(2, activation="relu")(combined)
out = layers.Dense(1, activation="sigmoid")(out)

    
model = Model(inputs=[x.input, y.input], outputs=out)


fileM = "fusion"
checkpoint_path = "%s/%s-%s.hdf5"%(arch,fileM ,arch)
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, 
                                             save_best_only=True,
                                             monitor='val_loss', 
                                             mode='min')
model.compile(optimizer='adam',
                            loss='binary_crossentropy',
                            metrics=['accuracy'])

hist= model.fit(x=X_train,y=y_train,
        epochs=100,
        validation_split=0.25,
        callbacks = [cp_callback],
        batch_size = 256,
        class_weight={1:5, 0:1}
         )

df = pd.DataFrame.from_dict(hist.history)
df.to_csv("%s/%s-%s-history.csv"%(arch,fileM ,arch))

model = tf.keras.models.load_model(checkpoint_path)    
loss, accuracy = model.evaluate(x=X_test, y=y_test)    
with open("%s/%s-%s-testAccurcy.txt"%(arch,fileM ,arch), "w+") as f:
    f.write(str(accuracy))
    f.close()


