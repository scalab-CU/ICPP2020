import os
import sys
import re
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
from tensorflow.keras import layers
from tensorflow.keras import Model
import pickle
import random
import itertools

def select_features(X, y, topN):
    clf = sklearn.svm.SVC(kernel='linear')    
    clf.fit(X, y)
    coef_list = clf.coef_[0][:]
    coef_list =abs(coef_list)
    top_idx = (np.argsort(coef_list)[-topN:]).tolist()
    top_idx.reverse()
    return top_idx, clf.coef_[0][top_idx]

def tfnnClassify_seen(X, y, index_label):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=index_label)
    y_train = np.asarray(y_train)
    y_test = np.asarray(y_test)
    X_train = np.asarray(X_train)
    X_test = np.asarray(X_test)
    model = tf.keras.Sequential()
    
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
   
   
    arch = "p100"
    fileM = "nnPerf"
    model_eval = "seen"
    ratio = 8
    checkpoint_path = "%s/%s-%s-%s-%d-W%d.hdf5"%(arch,fileM ,arch, model_eval, index_label, ratio )
    cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, 
                                                 save_best_only=True,
                                                 monitor='val_loss', 
                                                 mode='min')
    model.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy'])

    hist= model.fit(x=X_train,y=y_train,
            validation_split=0.25,
            callbacks = [cp_callback],
            epochs=200,
            batch_size = 256,
            class_weight={1:ratio, 0:1})

    df = pd.DataFrame.from_dict(hist.history)
    df.to_csv("%s/%s-%s-%s-%d-W%d-history.csv"%(arch,fileM ,arch, model_eval, index_label, ratio ))

    model = tf.keras.models.load_model(checkpoint_path)
    loss, accuracy = model.evaluate(x=X_test, y=y_test)
    with open("%s/%s-%s-%s-%d-W%d-testAccurcy.txt"%(arch,fileM ,arch, model_eval, index_label, ratio), "w+") as f:
        f.write(str(accuracy))
        f.close()

    y_prob = model.predict(X)
    y_predict = [int(i>=0.5) for i in y_prob]
    #y_predict = [ i[0] for i in y_predict.tolist()]
    df = pd.DataFrame.from_dict({"y_real":y, "predict":y_predict})
    df.to_csv("%s/%s-%s-%s-%d-W%d-All.csv"%(arch,fileM ,arch, model_eval, index_label, ratio))


    y_prob = model.predict(X_test)
    y_predict = [int(i>=0.5) for i in y_prob]
    df = pd.DataFrame.from_dict({"y_real":y_test, "predict":y_predict})
    df.to_csv("%s/%s-%s-%s-%d-W%d-test.csv"%(arch,fileM ,arch, model_eval, index_label, ratio))

def tfnnClassify_unseen(dataX, index_label):
    
    max_app_num = 64
    max_list = range(max_app_num)
    
    app_train, app_test = train_test_split(max_list, test_size=0.25, random_state=index_label)
    
  
    train_idx = dataX.index[dataX["appIdx"].isin(app_train)].tolist()
    test_idx = dataX.index[dataX["appIdx"].isin(app_test)].tolist()
    
    
    random.shuffle(train_idx)
    
    X = dataX.iloc[:, 5:]
    X_std =  StandardScaler().fit_transform(X.values)
    y = dataX.loc[:,"Type"]
    top_idx, coef_list = select_features(X_std, y, 12)
    X_std = X_std[:, top_idx]
    
    
    X_train =  X_std[train_idx, :]
    X_test =  X_std[test_idx, :]
    y_train =  dataX.loc[train_idx, "Type"].values
    y_test =  dataX.loc[test_idx, "Type"].values
    
  

    model = tf.keras.Sequential()
    
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
   
   
    arch = "p100"
    fileM = "nnPerf"
    model_eval = "unseen"
    ratio = 8
    checkpoint_path = "%s/%s-%s-%s-%d-W%d.hdf5"%(arch,fileM ,arch, model_eval, index_label, ratio )
    cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, 
                                                 save_best_only=True,
                                                 monitor='val_loss', 
                                                 mode='min')
    model.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy'])

    hist= model.fit(x=X_train,y=y_train,
            validation_split=0.25,
            callbacks = [cp_callback],
            epochs=200,
            batch_size = 256,
            class_weight={1:ratio, 0:1})

    df = pd.DataFrame.from_dict(hist.history)
    df.to_csv("%s/%s-%s-%s-%d-W%d-history.csv"%(arch,fileM ,arch, model_eval, index_label, ratio ))

    model = tf.keras.models.load_model(checkpoint_path)
    loss, accuracy = model.evaluate(x=X_test, y=y_test)
    with open("%s/%s-%s-%s-%d-W%d-testAccurcy.txt"%(arch,fileM ,arch, model_eval, index_label, ratio), "w+") as f:
        f.write(str(accuracy))
        f.close()

    y_prob = model.predict(X_std)
    y_predict = [int(i>=0.5) for i in y_prob]
    #y_predict = [ i[0] for i in y_predict.tolist()]
    df = pd.DataFrame.from_dict({"y_real":y, "predict":y_predict})
    df.to_csv("%s/%s-%s-%s-%d-W%d-All.csv"%(arch,fileM ,arch, model_eval, index_label, ratio))


    y_prob = model.predict(X_test)
    y_predict = [int(i>=0.5) for i in y_prob]
    df = pd.DataFrame.from_dict({"y_real":y_test, "predict":y_predict})
    df.to_csv("%s/%s-%s-%s-%d-W%d-test.csv"%(arch,fileM ,arch, model_eval, index_label, ratio))




if __name__=="__main__":

    arch = "P100"
    dataName= 'perf_transfer_%s.csv'%arch
    print("start")
    dataX = pd.read_csv(dataName, sep=',' )
    #y = dataX.loc[:,"Type"]
    #y = [int(i=='risky') for i in y]
    #X = dataX.iloc[:, 5:]
    #X_std =  StandardScaler().fit_transform(X.values)

    #top_idx, coef_list = select_features(X_std, y, 12)
    #accuracy_nn = []
    #X_input = X_std[:, top_idx]
    
    for index_label in range(1, 6):
        tfnnClassify_unseen(dataX, index_label)


