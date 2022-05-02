import tkinter as tk
from tkinter import filedialog, ttk, font
import matplotlib.backends.backend_tkagg as mplTk
import matplotlib.pyplot as plt
from matplotlib import rc, cm
from datetime import datetime
import os
import numpy as np
from instr_inter import *
from time import sleep, time
from scan import meas_current

def select_dir(*args):
   path= filedialog.askdirectory(title="Select a Folder")
   save_dir_val.set(path)

def replot(curr, bias_v):
   sweep_colors = np.zeros((0,4))
   for colormap, steps in zip([cm.Purples, cm.Blues, cm.Greens, cm.Oranges], num_steps):
      unique_colors = colormap(np.linspace(.5,1,steps))
      #color = np.array([unique_colors] * ceil(steps/100))
      color = unique_colors.flatten().reshape(-1, 4)
      sweep_colors = np.vstack((sweep_colors, color))
   global bias
   for ii in range(curr.shape[0]):
      for jj in range(curr.shape[1]):
         ax_seq_v.plot(ii*curr.shape[1]+jj, bias_v[ii], 
                        '.', c=sweep_colors[ii])
         ax_seq.plot(ii*curr.shape[1]+jj, bias[ii,jj], 
                     '.', c=sweep_colors[ii])
         ax_iv.plot(bias_v[ii], curr[ii,jj], '.', c=sweep_colors[ii])

   fig_seq.tight_layout()
   fig_iv.tight_layout()
   canvas_iv.draw()
   canvas_seq.draw()
   canvas_iv.flush_events()
   canvas_seq.flush_events()

def scale_change(*args):
   try:
      val = plot_scale_clicked.get()
   except:
      return

   if val == 'symlog':
      plot_linthresh_meas.grid(column=2, row=5, sticky=tk.E, padx=5, pady=5)
      plot_linthresh_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)
      try:
         linthresh = plot_linthresh_val.get()
      except:
         return
      ax_seq.set_yscale(val, linthreshy=linthresh)
      ax_iv.set_yscale(val, linthreshy=linthresh)
      replot(curr, bias_v)
   elif val == 'log':
      replot(abs(curr), bias_v)
      plot_linthresh_meas.grid_remove()
      plot_linthresh_label.grid_remove()
      ax_seq.set_yscale(val)
      ax_iv.set_yscale(val)
   elif val == 'linear':
      replot(abs(curr), bias_v)
      plot_linthresh_meas.grid_remove()
      plot_linthresh_label.grid_remove()
      ax_seq.set_yscale(val)
      ax_iv.set_yscale(val)

   fig_seq.tight_layout()
   fig_iv.tight_layout()
   canvas_seq.draw()
   canvas_iv.draw()

def iv_sweep(delay=.1):
   v_max = sweep_max_val.get()
   v_min = sweep_min_val.get()
   v_step = sweep_step_val.get()
   step_0_max = np.arange(0, v_max, v_step)
   step_max_0 = np.arange(v_max, 0, -v_step)
   step_0_neg_max = np.arange(0, -v_max, -v_step)
   step_neg_max_0 = np.arange(-v_max, 1e-6, v_step)
   num_steps = [step_0_max.size, step_max_0.size, step_0_neg_max.size, step_neg_max_0.size]
   bias_v = np.concatenate((step_0_max,
                           step_max_0,
                           step_0_neg_max,
                           step_neg_max_0))
   curr = np.zeros((bias_v.shape[0], dmm_num_val.get()))
   time_spent = np.zeros((bias_v.shape[0]))

   sweep_colors = np.zeros((0,4))
   for colormap, steps in zip([cm.Purples, cm.Blues, cm.Greens, cm.Oranges], num_steps):
      unique_colors = colormap(np.linspace(.5,1,steps))
      #color = np.array([unique_colors] * ceil(steps/100))
      color = unique_colors.flatten().reshape(-1, 4)
      sweep_colors = np.vstack((sweep_colors, color))

   # If selected measure a noise floor and subtract it from future measurements
   LNA.set_bias(0)
   sleep(1.5)
   sens = lna_sens_clicked.get()
   # Manually Update the sens on the GUI
   sens_var.set(f'Sens: {LNA.sens_table[sens]}')
   curr_floor = np.zeros(10)
   for ii in range(10):
      curr_floor[ii], sens = meas_current(sens, LNA, DMM, delay)
   curr_floor_mean = np.mean(curr_floor)

   for ii, v in enumerate(bias_v):
      #print(f'Bias: {v} V')
      LNA.set_bias(round(v*1000))
      LNA.reset_filter_caps()
      sleep(1.5)

      # Take groups of measurements until stdev is lower than 1/3e of the sensitivity
      t = time()
      while True:
         for jj in range(curr.shape[1]):
            if e_stop:
               relay.switch_relay(relay.NONE)
               relay.switch_relay(relay.LNA)
               LNA.set_bias(0)
               return curr, bias_v, time_spent, curr_floor_mean

            curr[ii, jj], sens_out = meas_current(sens, LNA, DMM, delay,
                                                  LNA_gui_var=curr_var, 
                                                  Sens_gui_var=sens_var)
            # Update the plots
            if plot_scale_clicked.get() == 'log':
               curr_plot = abs(curr[ii,jj])
            else:
               curr_plot = curr[ii,jj]
            if lna_offset.get():
               ax_seq_v.plot(ii*curr.shape[1]+jj, bias_v[ii]-curr_floor_mean, 
                           '.', c=sweep_colors[ii])
               ax_seq.plot(ii*curr.shape[1]+jj, curr_plot-curr_floor_mean, 
                           '.', c=sweep_colors[ii])
            else:
               ax_seq_v.plot(ii*curr.shape[1]+jj, bias_v[ii], 
                           '.', c=sweep_colors[ii])
               ax_seq.plot(ii*curr.shape[1]+jj, curr_plot, 
                           '.', c=sweep_colors[ii])

            ax_iv.plot(bias_v[ii], curr_plot, '.', c=sweep_colors[ii])
            # Pause to allow plots and progress bar to update
            sleep(0.02)
            fig_seq.tight_layout()
            fig_iv.tight_layout()
            canvas_iv.draw()
            canvas_seq.draw()
            canvas_iv.flush_events()
            canvas_seq.flush_events()

            #bias[ii, jj] -= curr_floor_mean
            if sens_out != sens:
                  sens = sens_out

         mean_curr = np.mean(curr[ii])
         diff = np.abs(curr[ii] - mean_curr) / LNA.sens_table[sens]
         if not any(np.abs(diff) > 3*np.e):
            break
         else:
            sleep(1.5)
      time_spent[ii] = time() - t
   sleep(0.02)
   progress_var.set((ii+1)/bias_v.shape[0]* 100)
   root.update_idletasks()
   
   return curr, bias_v, time_spent, curr_floor_mean

def start_scan(*args):
   save_dir_btn['state'] = tk.DISABLED
   stop_btn.grid(column=0, row=1, columnspan=3, sticky='EW', padx=5, pady=5)
   pb.grid(column=0, row=2, columnspan=3, sticky='EW', padx=5, pady=5)
   sens_label.grid(column=0, row=3, sticky='EW', padx=5, pady=5)
   curr_label.grid(column=2, row=3, columnspan=3, sticky='EW', padx=5, pady=5)

   global e_stop
   e_stop = False
   # Clear axes if hold is not on
   if not hold_on.get():
      ax_seq.cla()
      ax_seq.cla()
      ax_iv.cla()

      ax_seq.set_ylabel('Current (A)')
      ax_seq.set_xlabel('Measurement #')
      ax_seq_v.set_ylabel('Bias Voltage (V)')
      ax_seq_v.set_xlabel('Measurement #')
      fig_seq.tight_layout()

      ax_iv.set_xlabel('Bias Voltage (V)')
      ax_iv.set_ylabel('Current (A)')
      fig_iv.tight_layout()

   # Pull parameters from GUI to initialize instruments
   DMM.set_integ_time(dmm_integ_clicked.get())
   lna_gain = lna_gain_mode_clicked.get().replace(' ', '_')
   lna_filter = lna_filter_clicked.get().replace(' ', '_')
   LNA.set_filter(lna_gain, lna_filter, lna_filter_freq_clicked.get())
   
   curr, bias_v, time_spent, curr_floor_mean = iv_sweep()

   # Save data from the sweep
   # save plot in Device Exploration Directory
   if lna_filter != 'None':
      filter_str = f'{lna_gain}_LP{lna_filter}{lna_filter_clicked.get()}Hz'
   else:
      filter_str = f'{lna_gain}_None'
   device_name = device_name_val.get()
   device_idx = device_idx_val.get()
   dir_name = save_dir_val.get()
   integ_time=dmm_integ_clicked.get()
   title = f'{device_name}_{device_idx}_{filter_str}_Integ{integ_time}'

   # Create dir if it does not exist
   if not os.path.exists(dir_name):
      os.mkdir(dir_name)
   fig_seq.savefig(os.path.join(dir_name, f'{title}.png'))
   fig_iv.savefig(os.path.join(dir_name, f'{title}_alt.png'))

   # Save the raw data to a directory
   headers = ['v', 'i_floor', 'time_spent'] + [f'i_{ii}' for ii in range(curr.shape[1])]
   header_str = ','.join(headers)
   save_arr = np.hstack((np.expand_dims(bias_v, 1), 
                         curr_floor_mean*np.ones((bias_v.shape[0], 1)),
                         np.expand_dims(time_spent, 1),
                         curr))
   np.savetxt(os.path.join(dir_name, f'{title}.csv'), save_arr, 
              delimiter=",",header=header_str)
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
DMM = A34410A.A34410A()
LNA = SR570.SR570()


root = tk.Tk()
root.state('zoomed')
root.title('IV Sweep GUI')
curr = None # Initialize outside of function so that we can change the scaling
bias_v = None
num_steps = None
e_stop = False

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
save_dir_val.set(os.path.join('.', 'Measurements', date))
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
lna_gain_mode_clicked.set(lna_gain_mode_options[0])
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
dmm_num_label = tk.Label(dmm_frame, text='Measurements per voltage')
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
sweep_frame = tk.Frame(root, bd=2, width=375)
sweep_frame.grid(column=0, row=3, sticky=tk.W+tk.E)
sweep_frame.grid_columnconfigure(0, weight=1)
# Label for the subframe
tk.Label(sweep_frame, text='IV Sweep', font=('Arial',12)).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
# Min Voltage
sweep_min_label = tk.Label(sweep_frame, text='Min Voltage (V)')
sweep_min_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
sweep_min_val = tk.DoubleVar()
sweep_min_meas = tk.Entry(sweep_frame, text=sweep_min_val, width=5)
sweep_min_meas.grid(column=1, row=1, sticky=tk.E+tk.W, padx=5, pady=5)
sweep_min_meas.grid_columnconfigure(1, weight=1)
sweep_min_val.set(-1.5)
# Max Voltage
sweep_max_label = tk.Label(sweep_frame, text='Max Voltage (V)')
sweep_max_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
sweep_max_val = tk.DoubleVar()
sweep_max_meas = tk.Entry(sweep_frame, text=sweep_max_val, width=5)
sweep_max_meas.grid(column=1, row=2, sticky=tk.E+tk.W, padx=5, pady=5)
sweep_max_meas.grid_columnconfigure(1, weight=1)
sweep_max_val.set(1.5)
# Voltage Step
sweep_step_label = tk.Label(sweep_frame, text='Voltage Step (V)')
sweep_step_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
sweep_step_val = tk.DoubleVar()
sweep_step_meas = tk.Entry(sweep_frame, text=sweep_step_val, width=5)
sweep_step_meas.grid(column=1, row=3, sticky=tk.E+tk.W, padx=5, pady=5)
sweep_step_meas.grid_columnconfigure(1, weight=1)
sweep_step_val.set(0.1)

## Plot Settings
plot_frame = tk.Frame(root, bd=2, width=375)
plot_frame.grid(column=0, row=4, sticky=tk.W+tk.E)
plot_frame.grid_columnconfigure(0, weight=1)
# Button to start sweep
ft = font.Font(size='14', weight='bold')
save_dir_btn = tk.Button(plot_frame, text='Start Scan', command=start_scan, font=ft)
save_dir_btn.grid(column=0, row=0, columnspan=3, sticky='EW', padx=5, pady=5)
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
plot_hold_on_check.grid(column=0, row=3, padx=5, pady=5)
# Set linthresh for symlog
plot_linthresh_label = tk.Label(plot_frame, text='Symlog linthresh')
plot_linthresh_val = tk.DoubleVar()
plot_linthresh_meas = tk.Entry(plot_frame, text=plot_linthresh_val, width=10)
plot_linthresh_val.set(1e-9)
# Plot Scale
plot_scale_label = tk.Label(plot_frame, text='Y-Scale')
plot_scale_label.grid(column=1, row=3, sticky=tk.W, padx=5, pady=5)
plot_scale_options = ['linear', 'log', 'symlog']
plot_scale_clicked = tk.StringVar()
plot_scale_clicked.set(plot_scale_options[0])
plot_scale_menu = tk.OptionMenu(plot_frame, plot_scale_clicked ,*plot_scale_options)
plot_scale_menu.config(width=6)
plot_scale_menu.grid(column=2, row=3, sticky=tk.E, padx=5, pady=5)

plot_linthresh_val.trace('w', scale_change)
plot_scale_clicked.trace('w', scale_change)

## Figure settings
font = {'size'   : 12}
rc('font', **font)

# Sequential Figures
fig_seq, (ax_seq, ax_seq_v) = plt.subplots(2, 1)
fig_seq.set_size_inches(2*3.5,2*4.75)
canvas_seq = mplTk.FigureCanvasTkAgg(fig_seq, master=root)
canvas_seq.get_tk_widget().grid(column=1, row=0, sticky=tk.W+tk.E, rowspan=10)
ax_seq.set_ylabel('Current (A)')
ax_seq.set_xlabel('Measurement #')
ax_seq_v.set_ylabel('Bias Voltage (V)')
ax_seq_v.set_xlabel('Measurement #')
fig_seq.tight_layout()

frame_seq_toolbar = tk.Frame(root)
frame_seq_toolbar.grid(row=10, column=1)
toolbar_seq = mplTk.NavigationToolbar2Tk(canvas_seq, frame_seq_toolbar)
toolbar_seq.update()

# IV figure
fig_iv, ax_iv = plt.subplots(1,1)
fig_iv.set_size_inches(2*4.75,2*4.75)
canvas_iv = mplTk.FigureCanvasTkAgg(fig_iv, master=root)
canvas_iv.get_tk_widget().grid(column=2, row=0, sticky=tk.W+tk.E, rowspan=10)
ax_iv.set_xlabel('Bias Voltage (V)')
ax_iv.set_ylabel('Current (A)')
fig_iv.tight_layout()

frame_iv_toolbar = tk.Frame(root)
frame_iv_toolbar.grid(row=10, column=2)
toolbar_iv = mplTk.NavigationToolbar2Tk(canvas_iv, frame_iv_toolbar)
toolbar_iv.update()

root.mainloop()