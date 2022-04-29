import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import os
from math import ceil
v_max = 3000
v_step = 100
bias_v = np.concatenate((np.arange(0, v_max, v_step),
                        np.arange(v_max, 0, -v_step),
                        np.arange(0, -v_max, -v_step),
                        np.arange(-v_max, 1, v_step)))
bias = np.zeros((bias_v.shape[0], 25))
changed_sens = np.full(bias.shape, False)

dir_name = "C:\\Users\\snehd\\Desktop\\Northwestern\\BISOL Research\\"
device_name = "FIB1_C3_CircularPad_LP6dB1Hz_Integ1.csv"
get_dir = dir_name + device_name
data = np.genfromtxt(get_dir,
                    delimiter=",")
unique_colors = cm.tab20(np.linspace(0,1,20))
color = np.array([unique_colors] * ceil(bias_v.shape[0]/20))
color = color.flatten().reshape(-1, 4)

plt.figure()
for ii in range(data.shape[0]):
    for jj in range(1,data.shape[1]):
        plt.plot(ii,data[ii,0]/data[ii,jj],'.',c=color[ii])
#for ii in range(data.shape[1]):
 #   for jj in range(data.shape[0]):
  #      plt.plot(jj*data.shape[0]+ii,data[jj,ii])

plt.show()