from statistics import variance
import tkinter as tk
from tkinter import Variable, filedialog, ttk, font
import matplotlib.backends.backend_tkagg as mplTk
import matplotlib.pyplot as plt
from matplotlib import rc, cm
from datetime import datetime
import os
import numpy as np
from instr_inter import *
from time import sleep, time
from scan import meas_current
from math import floor

def select_dir(*args):
   path= filedialog.askdirectory(title="Select a Folder")
   save_dir_val.set(path)

def replot(actual_time, meas_curr, meas_res, curr_floor_mean, data_hist, bias_v):
   if meas_curr is None or data_hist is None:
      return 
   # Add previous measurements
   t_hist = data_hist[:, 0::2]
   i_hist = data_hist[:, 1::2]
   r_hist = data_hist[:, 1::2]
   valid_plot = ~np.isnan(t_hist)
   valid_hist = data_hist[valid_plot]
   ax_curr.plot(t_hist[valid_plot], i_hist[valid_plot]-curr_floor_mean, 'k.')
   if curr_floor_mean != 0:
      ax_curr.plot(t_hist[valid_plot], bias_v/(i_hist[valid_plot]-curr_floor_mean), 'k.')
   else:
      ax_res.plot(t_hist[valid_plot], r_hist[valid_plot], 'k.')

   # Add current values
   valid_plot = np.logical_not(np.isnan(actual_time))

   ax_curr.plot(actual_time[valid_plot], meas_curr[valid_plot]-curr_floor_mean, 'k.')
   if curr_floor_mean != 0:
      ax_res.plot(actual_time[valid_plot], bias_v/(meas_curr[valid_plot]-curr_floor_mean), 'k.')
   else:
      ax_res.plot(actual_time[valid_plot], meas_res[valid_plot], 'k.')

   fig_curr.tight_layout()
   fig_res.tight_layout()
   canvas_curr.draw()
   canvas_res.draw()
   canvas_curr.flush_events()
   canvas_res.flush_events()

def scale_change(*args):
   try:
      xval = plot_xscale_clicked.get()
      yval = plot_yscale_clicked.get()
   except:
      return

   # Since time is always postive or 0, no need to do special adjusts
   ax_curr.set_yscale(xval)
   ax_res.set_yscale(xval)
      
   global bias_v, data_hist, actual_time, meas_curr, data_hist, meas_res
   if yval == 'symlog':
      plot_linthresh_meas.grid(column=2, row=5, sticky=tk.E, padx=5, pady=5)
      plot_linthresh_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)
      try:
         linthresh = plot_linthresh_val.get()
      except:
         return
      ax_curr.set_yscale(yval, linthreshy=linthresh)
      ax_res.set_yscale(yval, linthreshy=linthresh)
      replot(actual_time, meas_curr, meas_res, curr_floor_mean, data_hist, bias_v)
   elif yval == 'log':
      if meas_curr is not None and data_hist is not None:
         replot(actual_time, np.abs(meas_curr), meas_res, curr_floor_mean, 
               np.hist(data_hist), bias_v)
      plot_linthresh_meas.grid_remove()
      plot_linthresh_label.grid_remove()
      ax_curr.set_yscale(yval)
      ax_res.set_yscale(yval)
   elif yval == 'linear':
      replot(actual_time, meas_curr, meas_res, curr_floor_mean, data_hist, bias_v)
      plot_linthresh_meas.grid_remove()
      plot_linthresh_label.grid_remove()
      ax_curr.set_yscale(yval)
      ax_res.set_yscale(yval)

   fig_res.tight_layout()
   fig_curr.tight_layout()
   canvas_res.draw()
   canvas_curr.draw()

def retention_scan(delay=.1):
   global t0, curr_floor_mean, actual_time, meas_curr, meas_res
   time_step_size = float(meas_period_meas.get())
   time_final = float(meas_time_meas.get())
   time_steps = np.arange(t0, t0 + time_final, time_step_size)
   num_time_steps = time_steps.size

   bias_v = meas_bias_val.get()
   num_meas_per_time = dmm_num_val.get()
   actual_time = np.empty((num_meas_per_time, num_time_steps))
   actual_time[:] = np.NaN
   meas_curr = np.empty((num_meas_per_time, num_time_steps))
   meas_curr[:] = np.NaN
   meas_res = np.empty((num_meas_per_time, num_time_steps))
   meas_res[:] = np.NaN

   # If selected measure a noise floor and subtract it from future measurements
   sens = lna_sens_clicked.get()
   # Manually Update the sens on the GUI
   sens_var.set(f'Sens: {LNA.sens_table[sens]}')
   if lna_offset.get():
      LNA.set_bias(0)
      sleep(1)
      relay.switch_relay(relay.LNA)
      curr_floor = np.zeros(10)
      for ii in range(10):
         curr_floor[ii], sens = meas_current(sens, LNA, DMM, delay)
      curr_floor_mean = np.mean(curr_floor)
   else:
      curr_floor_mean = 0

   # Start measurement and set bias
   relay.switch_relay(relay.NONE)
   LNA.set_bias(round(bias_v*1000))
   LNA.reset_filter_caps()
   relay.switch_relay(relay.LNA)
   # Record initial time when bias was applied
   t = time()
   for t_idx, t_ideal in enumerate(time_steps):
      # Wait until the elapsed time exceeds our current time point
      if e_stop:
            relay.switch_relay(relay.NONE)
            relay.switch_relay(relay.LNA)
            LNA.set_bias(0)
            return actual_time, meas_curr, num_time_steps, time(), curr_floor_mean
      while time()-t < t_ideal:
         sleep(1e-3)
         continue
   
      for m_idx in range(num_meas_per_time):
         meas_curr[m_idx, t_idx], sens_out = meas_current(sens, LNA, DMM, delay,
                                                            LNA_gui_var=curr_var, 
                                                            Sens_gui_var=sens_var)
         actual_time[m_idx, t_idx] = time()-t
         meas_res = bias_v / meas_curr[m_idx, t_idx]

         # Update the plots
         if plot_yscale_clicked.get() == 'log':
            curr_plot = abs(meas_curr[m_idx, t_idx])
         else:
            curr_plot = meas_curr[m_idx, t_idx]

         ax_curr.plot(actual_time[m_idx, t_idx], curr_plot-curr_floor_mean, 'k.')
         ax_res.plot(actual_time[m_idx, t_idx], bias_v/(curr_plot-curr_floor_mean), 'k.')


         if sens_out != sens:
               sens = sens_out
      
      fig_curr.tight_layout()
      fig_res.tight_layout()
      canvas_curr.draw()
      canvas_res.draw()
      canvas_curr.flush_events()
      canvas_res.flush_events()

      progress_var.set((t_idx+1)/num_time_steps* 100)
      root.update_idletasks()

   relay.switch_relay(relay.NONE)

   return actual_time, meas_curr, num_time_steps, time(), curr_floor_mean

def save_data(actual_time, meas_curr, meas_res, curr_floor):
   global data_hist
   # Save data from the sweep
   # save plot in Device Exploration Directory
   bias_v = float(meas_bias_val.get())
   lna_gain = lna_gain_mode_clicked.get().replace(' ', '_')
   lna_filter = lna_filter_clicked.get().replace(' ', '_')
   if lna_filter != 'None':
      filter_str = f'{lna_gain}_LP{lna_filter}{lna_filter_clicked.get()}Hz'
   else:
      filter_str = f'{lna_gain}_None'
   device_name = device_name_val.get()
   device_idx = device_idx_val.get()
   dir_name = save_dir_val.get()
   integ_time=dmm_integ_clicked.get()
   title = f'{device_name}_{device_idx}_{filter_str}_Integ{integ_time}_Bias{bias_v}V'
   if lna_offset.get():
      title += f'CurrFloor_{curr_floor}A'

   # Create dir if it does not exist
   if not os.path.exists(dir_name):
      os.makedirs(dir_name)
   fig_curr.savefig(os.path.join(dir_name, f'{title}_curr.png'))
   fig_res.savefig(os.path.join(dir_name, f'{title}_res.png'))

   # Check if the new data array and the historical data array are of compatible dim
   # If not concat NaN to the empty spots
   if data_hist is None:
      width = actual_time.shape[0]*3
   else:
      width = max(actual_time.shape[0]*3, data_hist.shape[0])
   height = actual_time.shape[1]
   # Make new array that interleaves time, curr, and res
   arr_new_data = np.empty((height, width))
   arr_new_data[:] = np.NaN
   arr_new_data[:height, 0::3] = np.transpose(actual_time)
   arr_new_data[:height, 1::3] = np.transpose(meas_curr)
   arr_new_data[:height, 2::3] = np.transpose(meas_res)
   # If necessary, expand the original data array
   if data_hist is not None and arr_new_data.shape[1] > data_hist.shape[1]:
      pad_len = arr_new_data.shape[1] - data_hist.shape[1]
      pad_arr = np.empty((data_hist.shape[0], pad_len))
      pad_arr[:] = np.NaN
      data_hist = np.hstack((data_hist, pad_arr))

   # Save the raw data to a directory
   headers = [f't_{ii}, i_{ii}, r_{ii}' for ii in range(actual_time.shape[0])]
   header_str = ','.join(headers)
   if data_hist is not None:
      save_arr = np.vstack((data_hist, arr_new_data))
   else:
      data_hist = arr_new_data
      save_arr = arr_new_data
   np.savetxt(os.path.join(dir_name, f'{title}.csv'), save_arr, 
              delimiter=",",header=header_str)

def start_scan(*args):
   save_dir_btn['state'] = tk.DISABLED
   stop_btn.grid(column=0, row=1, columnspan=2, sticky='EW', padx=5, pady=5)
   pb.grid(column=0, row=2, columnspan=2, sticky='EW', padx=5, pady=5)
   sens_label.grid(column=0, row=3, sticky='EW', padx=5, pady=5)
   curr_label.grid(column=1, row=3, columnspan=3, sticky='EW', padx=5, pady=5)
   plot_frame.update_idletasks()
   sleep(.1)

   global e_stop, t0
   e_stop = False
   # Clear axes if hold is not on
   if not hold_on.get() or bias_v != float(meas_bias_val.get()):
      t0 = 0
      ax_curr.cla()
      ax_res.cla()

      ax_curr.set_xlabel('Time (s)')
      ax_curr.set_ylabel('I (A)')
      ax_res.set_xlabel('Time (s)')
      ax_res.set_ylabel('R (Ohms)')
      fig_curr.tight_layout()
      fig_res.tight_layout()


   # Pull parameters from GUI to initialize instruments
   DMM.set_integ_time(dmm_integ_clicked.get())
   lna_gain = lna_gain_mode_clicked.get().replace(' ', '_')
   lna_filter = lna_filter_clicked.get().replace(' ', '_')
   LNA.set_filter(lna_gain, lna_filter, lna_filter_freq_clicked.get())
   
   bias_v = float(meas_bias_val.get())
   global actual_time, meas_curr, meas_res, tf, curr_floor_mean
   actual_time, meas_curr, meas_res, tf, curr_floor_mean = retention_scan()
   save_data(actual_time, meas_curr, meas_res, curr_floor_mean)
   t0 += tf

   # Increment index
   device_idx_val.set(device_idx_val.get()+1)
   
   # Remove items
   save_dir_btn['state'] = tk.NORMAL
   pb.grid_remove()
   sens_label.grid_remove()
   curr_label.grid_remove()
   stop_btn.grid_remove()

# Intialize Instruments
relay = relay_inter.relay_inter()
relay.switch_relay(relay.NONE)
DMM = A34410A.A34410A()
LNA = SR570.SR570()


root = tk.Tk()
root.state('zoomed')
root.title('Retention GUI')
t0 = None
curr_floor_mean = None
e_stop = False
data_hist = None
actual_time = None
meas_curr = None
meas_res = None
bias_v = 0

## Device options
device_frame = tk.Frame(root, bd=2, width=450)
device_frame.grid(column=0, row=0,sticky=tk.W+tk.E)
device_frame.grid_columnconfigure(0, weight=1)
# Save Dir
save_dir_label = tk.Label(device_frame, text='Save Folder')
save_dir_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
save_dir_btn = tk.Button(device_frame, text='Browse', command=select_dir)
save_dir_btn.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)
save_dir_val = tk.StringVar()
save_dir_entry = tk.Entry(device_frame, text=save_dir_val, width=42)
save_dir_entry.grid(column=0, row=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
now = datetime.now()
date = now.strftime('%Y-%m-%d')
save_dir_val.set(os.path.join('.', 'Measurements', 'Retention', date))
# Device Name
device_name_label = tk.Label(device_frame, text='Device Name')
device_name_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
device_name_val = tk.StringVar()
device_name_meas = tk.Entry(device_frame, text=device_name_val, width=20)
device_name_meas.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)
device_name_val.set('FIB1_A1')
# Meas Idx
device_idx_label = tk.Label(device_frame, text='Index')
device_idx_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)
device_idx_val = tk.IntVar()
device_idx_meas = tk.Entry(device_frame, text=device_idx_val, width=20)
device_idx_meas.grid(column=1, row=4, sticky=tk.E, padx=5, pady=5)
device_idx_val.set(0)

## LNA Options
lna_frame = tk.Frame(root, bd=2, width=375)
lna_frame.grid(column=0, row=1, sticky=tk.W+tk.E)
lna_frame.grid_columnconfigure(0, weight=1)
# Label for the subframe
tk.Label(lna_frame, text='LNA', font=('Arial',12)).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
# Gain Mode
lna_gain_mode_label = tk.Label(lna_frame, text='Gain Mode')
lna_gain_mode_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
lna_gain_mode_options = [m.replace('_', ' ') for m in list(SR570.SR570.gain_modes.keys())]
lna_gain_mode_clicked = tk.StringVar()
lna_gain_mode_clicked.set(lna_gain_mode_options[-1])
lna_gain_mode_menu = tk.OptionMenu(lna_frame, lna_gain_mode_clicked ,*lna_gain_mode_options)
lna_gain_mode_menu.config(width=len(max(lna_gain_mode_options)))
lna_gain_mode_menu.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)
# Filter Type
lna_filter_label = tk.Label(lna_frame, text='LP Cutoff')
lna_filter_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
lna_filter_options = list(SR570.SR570.filters.keys())
lna_filter_options[0] = 'None' # Convert None to a string
lna_filter_clicked = tk.StringVar()
lna_filter_clicked.set(lna_filter_options[1])
lna_filter_menu = tk.OptionMenu(lna_frame, lna_filter_clicked ,*lna_filter_options)
lna_filter_menu.grid(column=1, row=2, sticky=tk.E, padx=5, pady=5)
# Filter cutoff frequency
lna_filter_freq_label = tk.Label(lna_frame, text='LP Cutoff Frequency (Hz)')
lna_filter_freq_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
lna_filter_freq_options = [f'{f}' for f in SR570.SR570.filter_freqs]
lna_filter_freq_clicked = tk.DoubleVar()
lna_filter_freq_clicked.set(lna_filter_freq_options[3])
lna_filter_freq_menu = tk.OptionMenu(lna_frame, lna_filter_freq_clicked ,*lna_filter_freq_options)
lna_filter_freq_menu.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)
# Initial Sens
lna_sens_label = tk.Label(lna_frame, text='Initial Sensitivity')
lna_sens_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)
lna_sens_options = list(range(len(SR570.SR570.sens_table)))
lna_sens_clicked = tk.IntVar()
lna_sens_clicked.set(lna_sens_options[0])
lna_sens_menu = tk.OptionMenu(lna_frame, lna_sens_clicked ,*lna_sens_options)
lna_sens_menu.grid(column=1, row=4, sticky=tk.E, padx=5, pady=5)
# Offset correction
lna_offset = tk.BooleanVar()
lna_offset_check = tk.Checkbutton(lna_frame, text='Offset Correction', variable=lna_offset)
lna_offset_check.grid(column=0, row=5, columnspan=2, padx=5, pady=5)

## DMM Options
dmm_frame = tk.Frame(root, bd=2, width=375)
dmm_frame.grid(column=0, row=2, sticky=tk.W+tk.E)
dmm_frame.grid_columnconfigure(0, weight=1)
# Label for the subframe
tk.Label(dmm_frame, text='DMM', font=('Arial',12)).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
# Integration time
dmm_integ_label = tk.Label(dmm_frame, text='Integration Time (* 1/60 s)')
dmm_integ_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
dmm_integ_options = A34410A.A34410A.integ_times
dmm_integ_clicked = tk.DoubleVar()
dmm_integ_clicked.set(dmm_integ_options[4])
dmm_integ_menu = tk.OptionMenu(dmm_frame, dmm_integ_clicked ,*dmm_integ_options)
dmm_integ_menu.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)
# Measurements per voltage
dmm_num_label = tk.Label(dmm_frame, text='Measurements per time')
dmm_num_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
dmm_num_val = tk.IntVar()
dmm_num_meas = tk.Entry(dmm_frame, text=dmm_num_val, width=5)
dmm_num_meas.grid(column=1, row=2, sticky=tk.E, padx=5, pady=5)
dmm_num_val.set(5)
# Initial measurements to discard per voltage
dmm_discard_label = tk.Label(dmm_frame, text='Initial discarded')
dmm_discard_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
dmm_discard_val = tk.IntVar()
dmm_discard_meas = tk.Entry(dmm_frame, text=dmm_discard_val, width=5)
dmm_discard_meas.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)
dmm_discard_val.set(0)

## General Sweep Options
meas_frame = tk.Frame(root, bd=2, width=375)
meas_frame.grid(column=0, row=3, sticky=tk.W+tk.E)
meas_frame.grid_columnconfigure(0, weight=1)

def update_meas(*args):
   def set(entry, val):
      entry.delete(0, tk.END)
      entry.insert(0, val)

   name = args[0]
   if name is None:
      return False
   try:
      if name == 'period':
         t = float(meas_period_meas.get())
         set(meas_freq_meas, 1/t)
         total_t = float(meas_time_meas.get())
         set(meas_total_num_meas, floor(total_t/t))
      elif name == 'freq':
         f = float(meas_freq_meas.get())
         set(meas_period_meas, 1/f)
         total_t = float(meas_time_meas.get())
         set(meas_total_num_meas, floor(total_t*f))
      elif name == "total_time":
         t = float(meas_period_meas.get())
         total_t = float(meas_time_meas.get())
         meas_total_num_meas.set(floor(total_t/t))
      elif name == "num_meas":
         t = float(meas_period_meas.get())
         total_num = float(meas_total_num_meas.get())
         set(meas_time_meas, t*total_num)
      return True
   except Exception as e:
      return False

# Label for the subframe
tk.Label(meas_frame, text='Retention Measurement', font=('Arial',12)).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
# Bias Voltage
meas_bias_label = tk.Label(meas_frame, text='Bias Voltage (V)')
meas_bias_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
meas_bias_val = tk.DoubleVar()
meas_bias_meas = tk.Entry(meas_frame, text=meas_bias_val, width=5)
meas_bias_meas.grid(column=1, row=1, sticky=tk.E+tk.W, padx=5, pady=5)
meas_bias_meas.grid_columnconfigure(1, weight=1)
meas_bias_val.set(0.2)
# Period between measurement
meas_period_label = tk.Label(meas_frame, text='Meas. Period (s)')
meas_period_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
meas_period_meas = tk.Entry(meas_frame, name='period', width=10,
                            validate='focusout', 
                            validatecommand=lambda : update_meas("period"))
meas_period_meas.grid(column=1, row=2, sticky=tk.E+tk.W, padx=5, pady=5)
meas_period_meas.grid_columnconfigure(1, weight=1)
meas_period_meas.insert(0, 1)
# Frequency of measurements
meas_freq_label = tk.Label(meas_frame, text='Meas. Frequency (Hz)')
meas_freq_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
meas_freq_meas = tk.Entry(meas_frame, name='freq', width=10,
                             validate='focusout', 
                             validatecommand=lambda : update_meas("freq"))
meas_freq_meas.grid(column=1, row=3, sticky=tk.E+tk.W, padx=5, pady=5)
meas_freq_meas.grid_columnconfigure(1, weight=1)
meas_freq_meas.insert(0, 1)
# Total Time
meas_time_label = tk.Label(meas_frame, text='Total Meas. Time (s)')
meas_time_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)
meas_time_meas = tk.Entry(meas_frame, name='total_time', width=10,
                             validate='focusout', 
                             validatecommand=lambda : update_meas("total_time"))
meas_time_meas.grid(column=1, row=4, sticky=tk.E+tk.W, padx=5, pady=5)
meas_time_meas.grid_columnconfigure(1, weight=1)
meas_time_meas.insert(0, 1)
# Num Measurements
meas_total_num_label = tk.Label(meas_frame, text='Total Meas. #')
meas_total_num_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)
meas_total_num_meas = tk.Entry(meas_frame, name='num_meas', width=10,
                             validate='focusout', 
                             validatecommand=lambda : update_meas("num_meas"))
meas_total_num_meas.grid(column=1, row=5, sticky=tk.E+tk.W, padx=5, pady=5)
meas_total_num_meas.grid_columnconfigure(1, weight=1)
meas_total_num_meas.insert(0, 1)


## Plot Settings
plot_frame = tk.Frame(root, bd=2, width=375)
plot_frame.grid(column=0, row=4, sticky=tk.W+tk.E)
plot_frame.grid_columnconfigure(0, weight=1)
# Button to start sweep
ft = font.Font(size='14', weight='bold')
save_dir_btn = tk.Button(plot_frame, text='Start Measurement', command=start_scan, font=ft)
save_dir_btn.grid(column=0, row=0, columnspan=2, sticky='EW', padx=5, pady=5)
# Progress bar for the scan
progress_var = tk.DoubleVar()
pb = ttk.Progressbar(plot_frame, orient='horizontal', mode='determinate', variable=progress_var)
# Labels for the current sens and current
sens_var = tk.StringVar()
curr_var = tk.StringVar()
sens_label = tk.Label(plot_frame, textvariable=sens_var)
curr_label = tk.Label(plot_frame, textvariable=curr_var)
def set_e_stop():
    global e_stop
    e_stop = True
stop_btn = tk.Button(plot_frame, text='Stop', command=set_e_stop, 
                    bg='red', fg='white', font=ft)
# Keep previous plots
hold_on = tk.BooleanVar()
plot_hold_on_check = tk.Checkbutton(plot_frame, text='Hold On', variable=hold_on)
plot_hold_on_check.grid(column=0, row=4, columnspan=3, padx=5, pady=5)
# Set linthresh for symlog
plot_linthresh_label = tk.Label(plot_frame, text='Symlog linthresh')
plot_linthresh_val = tk.DoubleVar()
plot_linthresh_meas = tk.Entry(plot_frame, text=plot_linthresh_val, width=10)
plot_linthresh_val.set(1e-9)
# Plot Scale
plot_xscale_label = tk.Label(plot_frame, text='X-Scale')
plot_xscale_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)
plot_xscale_options = ['linear', 'log']
plot_xscale_clicked = tk.StringVar()
plot_xscale_clicked.set(plot_xscale_options[0])
plot_xscale_menu = tk.OptionMenu(plot_frame, plot_xscale_clicked ,*plot_xscale_options)
plot_xscale_menu.config(width=6)
plot_xscale_menu.grid(column=1, row=5, sticky=tk.E, padx=5, pady=5)

plot_yscale_label = tk.Label(plot_frame, text='Y-Scale')
plot_yscale_label.grid(column=0, row=6, sticky=tk.W, padx=5, pady=5)
plot_yscale_options = ['linear', 'log', 'symlog']
plot_yscale_clicked = tk.StringVar()
plot_yscale_clicked.set(plot_yscale_options[0])
plot_yscale_menu = tk.OptionMenu(plot_frame, plot_yscale_clicked ,*plot_yscale_options)
plot_yscale_menu.config(width=6)
plot_yscale_menu.grid(column=1, row=6, sticky=tk.E, padx=5, pady=5)

plot_linthresh_val.trace_add('write', scale_change)
plot_xscale_clicked.trace_add('write', scale_change)
plot_yscale_clicked.trace_add('write', scale_change)

## Figure settings
font = {'size'   : 12}
rc('font', **font)

# Frame for plots
fig_frame = tk.Frame(root, bd=2, width=375)
fig_frame.grid(column=1, row=0, rowspan=10, sticky=tk.W+tk.E)

# Current Figure
fig_curr, ax_curr = plt.subplots(1, 1)
fig_curr.set_size_inches(2*8,2*2.25)
canvas_curr = mplTk.FigureCanvasTkAgg(fig_curr, master=fig_frame)
canvas_curr.get_tk_widget().grid(column=1, row=0, sticky=tk.W+tk.E)
ax_curr.set_xlabel('Time (s)')
ax_curr.set_ylabel('I (A)')
fig_curr.tight_layout()

frame_curr_toolbar = tk.Frame(fig_frame)
frame_curr_toolbar.grid(row=1, column=1, sticky=tk.E)
toolbar_curr = mplTk.NavigationToolbar2Tk(canvas_curr, frame_curr_toolbar)
toolbar_curr.update()

# Resistance Figure
fig_res, ax_res = plt.subplots(1,1)
fig_res.set_size_inches(2*8,2*2.25)
canvas_res = mplTk.FigureCanvasTkAgg(fig_res, master=fig_frame)
canvas_res.get_tk_widget().grid(column=1, row=2, sticky=tk.W+tk.E)
ax_res.set_xlabel('Time (s)')
ax_res.set_ylabel('R (Ohms)')
fig_res.tight_layout()

frame_res_toolbar = tk.Frame(fig_frame)
frame_res_toolbar.grid(row=3, column=1, sticky=tk.E)
toolbar_res = mplTk.NavigationToolbar2Tk(canvas_res, frame_res_toolbar)
toolbar_res.update()

root.mainloop()