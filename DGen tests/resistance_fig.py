import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from instr_inter import *
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import os
from time import sleep, time
from tqdm import tqdm
from math import ceil
from datetime import datetime


data = np.genfromtxt("C:\\Users\\Lab User\\Documents\\Memristor\\Measurements\\Device Exploration\\2022-04-21\\FIB1_A3-10-Short_LP6dB1Hz_Integ1.csv",
                    delimiter=",")
plt.figure
for ii in range(data.shape[1]):
    for jj in range(data.shape[0]):
        plt.plot(jj*data.shape[0]+ii,data[jj,ii])

plt.show()