# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:34:47 2021

@author: wangyan
"""

import wfdb
import numpy as np
import pandas as pd
import os 
import matplotlib.pyplot as plt

def erosion(signal,B):
    N=len(signal)
    M=len(B)
    fe=signal.copy()
    for n in range(int(np.ceil((M-1)/2)),N-int(np.ceil((M-1)/2))):
        fblock=[]
        for m in range(0,M):
            fblock.append(signal[n-int(np.ceil((M-1)/2))+m]-B[m])
        fe[n]=min(fblock)
    return fe
def dilation(signal,B):
    N=len(signal)
    M=len(B)
    fd=signal.copy()
    for n in range(int(np.ceil((M-1)/2)),N-int(np.ceil((M-1)/2))):
        fblock=[]
        for m in range(0,M):
            fblock.append(signal[n-int(np.ceil((M-1)/2))+m]+B[m])
        fd[n]=max(fblock)
    return fd   

def opening(signal,B,Bd=[]):
    if Bd==[]:
        Bd=B
    else:
        pass
    fo=dilation(erosion(signal,B),Bd)
    return fo

def closing(signal,B,Be=[]):
    if Be==[]:
        Be=B
    else:
        pass
    fc=erosion(dilation(signal,B),Be)
    return fc      

#ecg10 = nk.ecg_simulate(duration=10, method='ecgsyn')

###读取训练集数据
pathTrain='Training_set_I'
pathList=os.listdir(pathTrain)
fileTrain=[]
m=15 ##求微分时的m
for element in pathList:
    if element[-3:]=='hea':
        fileTrain.append(element[:-4])    
sigPro={}
sigDrv={}
drvMin={}
drvMax={}
##根据文献对数据去除基线和降噪
for file in fileTrain[0:1]:
    signals, fields = wfdb.rdsamp(os.path.join(pathTrain,file),sampfrom=0,channels=[0])
    fs=fields['fs']
    Bo=int(0.2*fs)*[0]
    Bc=int(0.3*fs)*[0]
    # plt.plot(range(0,300),signals[0:300],'b.')
    # plt.show()
    sigBase=closing(opening(signals,Bo),Bc)
    # plt.plot(range(0,300),sigBase[0:300],'r.')
    # plt.show()
    sigBaseRemv=signals-sigBase
    B1=[0,1,5,1,0]
    B2=[0]*5
    sigPro[file]=1/2*(opening(sigBaseRemv,B1,B2)+closing(sigBaseRemv,B1,B2))
    # plt.plot(range(0,300),sigPro[0:300],'k.')
    # plt.show()
        
    ##对降噪后的数据求微分
    d=[]
    dmin=[]
    dmax=[]    
    for n in range(len(signals)):
        xLeft=max(0,n-m)
        xRight=min(n+m+1,len(signals))
        derivative=(max(signals[range(xLeft,xRight)])+min(signals[range(xLeft,xRight)])-2*signals[n])/(xRight-xLeft)*fs
        derivative=derivative[0]
        if n>1:
            if (derivative>d[-1])&(d[-2]>d[-1]):
                dmin.append([n-1,d[-1]])
            if (derivative<d[-1])&(d[-2]<d[-1]):
                dmax.append([n-1,d[-1]])
        d.append(derivative)
    sigDrv[file]=d
    drvMin[file]=dmin
    drvMax[file]=dmax
        
plt.plot(range(0,300),sigDrv[fileTrain[0]][0:300],'k.')
plt.show()    

x,y=np.matrix(dmin[20:20000]).T
plt.plot(x,y,'b.')
plt.show() 

##找到局部最小值为R峰

