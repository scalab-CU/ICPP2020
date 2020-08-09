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
import os


def load_file(filepath):
    max_len = 1800
    dataframe = pd.read_excel(filepath, index_col=0)
    if (dataframe.shape[1] == 4 and dataframe.shape[0] > 1800):
        return dataframe.values[:max_len,:]
    else:
        print(filepath)

def load_group():
    arch = "V100"
    y_label = []
    data_group = []
    category = "normal"
    pathfolder = '/home/pzou/projects/Power_Signature/results/power/%s/%s'%(category, arch)
    for fileName in glob.glob1(pathfolder, '*.pwr.xlsx'):
        data = load_file(os.path.join(pathfolder, fileName))
        data_group.append(data)
        y_label.append(0)
    category = "risky"
    pathfolder = '/home/pzou/projects/Power_Signature/results/power/%s/%s'%(category, arch)
    for fileName in glob.glob1(pathfolder, '*.pwr.xlsx'):
        data = load_file(os.path.join(pathfolder, fileName))
        data_group.append(data)
        y_label.append(1)
    data_group = np.asarray(data_group)
    return data_group, y_label


print("start loading")
data_group, y_label = load_group()
print("Done loading")


#%%
X_train, X_test, y_train, y_test = train_test_split(data_group, y_label, test_size=0.25, random_state=1)
#X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=1)
#print(X_train)
X_train = np.asarray(X_train)
X_test = np.asarray(X_test)
n_timesteps = 1800
n_features = 4
model = tf.keras.Sequential()
model.add(layers.LSTM(256, input_shape=(n_timesteps, n_features)))
model.add(layers.Dropout(0.4))
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dense(16, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'])

model.fit(x=X_train,y=y_train,
        epochs=120,
        validation_split=0.25,
        batch_size = 256,
        class_weight={1:5, 0:1}
         )
loss, accuracy = model.evaluate(x=X_test, y=y_test)
print("Accuracy", accuracy)
#%%
