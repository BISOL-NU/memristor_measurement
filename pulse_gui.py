import tkinter as tk
from tkinter import filedialog, ttk, font
import matplotlib.backends.backend_tkagg as mplTk
import matplotlib.pyplot as plt
from matplotlib import rc
from datetime import datetime
import os
from instr_inter import *

def select_dir(*args):
   path= filedialog.askdirectory(title="Select a Folder")
   save_dir_val.set(path)

def scale_change(*args):
    try:
        val = plot_scale_clicked.get()
    except:
        return

    if val == 'symlog':
        plot_linthresh_meas.grid(column=2, row=4, sticky=tk.E, padx=5, pady=5)
        plot_linthresh_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)
        try:
            linthresh = plot_linthresh_val.get()
        except:
            return
        ax_meas.set_yscale(val, linthreshy=linthresh)
    else:
        plot_linthresh_meas.grid_remove()
        plot_linthresh_label.grid_remove()
        ax_meas.set_yscale(val)

    fig_meas.tight_layout()
    canvas_meas.draw()

def start_scan(*args):
   save_dir_btn['state'] = tk.DISABLED
   pb.grid(column=0, row=1, columnspan=3, sticky='EW', padx=5, pady=5)
   sens_label.grid(column=0, row=2, sticky='EW', padx=5, pady=5)
   curr_label.grid(column=2, row=2, columnspan=3, sticky='EW', padx=5, pady=5)

root = tk.Tk()
root.state('zoomed')
root.title('Pulse GUI')
dashboard_frame = tk.Frame(root)
dashboard_frame.grid(column=0, row=0, rowspan=4, sticky=tk.N)

## Device options
device_frame = tk.Frame(dashboard_frame, bd=2, width=450)
device_frame.grid(column=0, row=0,sticky=tk.W+tk.E)
device_frame.grid_columnconfigure(0, weight=1)
# Save Dir
save_dir_label = tk.Label(device_frame, text='Save Folder')
save_dir_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
save_dir_btn = tk.Button(device_frame, text='Browse', command=select_dir)
save_dir_btn.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)
save_dir_val = tk.StringVar()
save_dir_entry = tk.Entry(device_frame, text=save_dir_val, width=50)
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
device_idx_val = tk.StringVar()
device_idx_meas = tk.Entry(device_frame, text=device_idx_val, width=20)
device_idx_meas.grid(column=1, row=4, sticky=tk.E, padx=5, pady=5)
device_idx_val.set('0')

## LNA Options
lna_frame = tk.Frame(dashboard_frame, bd=2, width=375)
lna_frame.grid(column=0, row=1, sticky=tk.W+tk.E)
lna_frame.grid_columnconfigure(0, weight=1)
# Label for the subframe
tk.Label(lna_frame, text='LNA', font=('Arial',12)).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
# Gain Mode
lna_gain_mode_label = tk.Label(lna_frame, text='Gain Mode')
lna_gain_mode_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
lna_gain_mode_options = [m.replace('_', ' ') for m in list(SR570.SR570.gain_modes.keys())]
lna_gain_mode_clicked = tk.StringVar()
lna_gain_mode_clicked.set(lna_gain_mode_options[1])
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
lna_filter_freq_clicked = tk.StringVar()
lna_filter_freq_clicked.set(lna_filter_freq_options[3])
lna_filter_freq_menu = tk.OptionMenu(lna_frame, lna_filter_freq_clicked ,*lna_filter_freq_options)
lna_filter_freq_menu.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)
# Initial Sens
lna_sens_label = tk.Label(lna_frame, text='Initial Sensitivity')
lna_sens_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)
lna_sens_options = list(range(len(SR570.SR570.sens_table)))
lna_sens_clicked = tk.StringVar()
lna_sens_clicked.set(lna_sens_options[0])
lna_sens_menu = tk.OptionMenu(lna_frame, lna_sens_clicked ,*lna_sens_options)
lna_sens_menu.grid(column=1, row=4, sticky=tk.E, padx=5, pady=5)
# Offset correction
lna_offset = tk.BooleanVar()
lna_offset_check = tk.Checkbutton(lna_frame, text='Offset Correction', variable=lna_offset)
lna_offset_check.grid(column=0, row=5, columnspan=2, padx=5, pady=5)

## DMM Options
dmm_frame = tk.Frame(dashboard_frame, bd=2, width=375)
dmm_frame.grid(column=0, row=2, sticky=tk.W+tk.E)
dmm_frame.grid_columnconfigure(0, weight=1)
# Label for the subframe
tk.Label(dmm_frame, text='DMM', font=('Arial',12)).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
# Integration time
dmm_integ_label = tk.Label(dmm_frame, text='Integration Time (* 1/60 s)')
dmm_integ_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
dmm_integ_options = A34410A.A34410A.integ_times
dmm_integ_clicked = tk.StringVar()
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

## Pulse Parameters
pulse_frame = tk.Frame(dashboard_frame, bd=2, width=375)
pulse_frame.grid(column=0, row=3, sticky=tk.W+tk.E)
pulse_frame.grid_columnconfigure(0, weight=1)
# Label for the subframe
tk.Label(pulse_frame, text='Pulse Measurement', font=('Arial',12)).grid(column=0, row=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
# Pulse Voltage
pulse_v_label = tk.Label(pulse_frame, text='Pulse Amplitude (V)')
pulse_v_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
pulse_v_val = tk.StringVar()
pulse_v_meas = tk.Entry(pulse_frame, text=pulse_v_val, width=25)
pulse_v_meas.grid(column=1, row=1, sticky=tk.E+tk.W, padx=5, pady=5)
pulse_v_meas.grid_columnconfigure(1, weight=1)
pulse_v_val.set('7, -7')
# Pulse period
pulse_period_label = tk.Label(pulse_frame, text='Pulse On Period (s)')
pulse_period_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
pulse_period_val = tk.StringVar()
pulse_period_meas = tk.Entry(pulse_frame, text=pulse_period_val, width=25)
pulse_period_meas.grid(column=1, row=2, sticky=tk.E+tk.W, padx=5, pady=5)
pulse_period_meas.grid_columnconfigure(1, weight=1)
pulse_period_val.set('500e-9, 500e-9')
# Pulse per Burst
pulse_per_burst_label = tk.Label(pulse_frame, text='Pulses per burst')
pulse_per_burst_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
pulse_per_burst_val = tk.StringVar()
pulse_per_burst_meas = tk.Entry(pulse_frame, text=pulse_per_burst_val, width=25)
pulse_per_burst_meas.grid(column=1, row=3, sticky=tk.E+tk.W, padx=5, pady=5)
pulse_per_burst_meas.grid_columnconfigure(1, weight=1)
pulse_per_burst_val.set('100, 100')
# Number of Bursts
pulse_num_burst_label = tk.Label(pulse_frame, text='Number of Bursts')
pulse_num_burst_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=25)
pulse_num_burst_val = tk.StringVar()
pulse_num_burst_meas = tk.Entry(pulse_frame, text=pulse_num_burst_val, width=25)
pulse_num_burst_meas.grid(column=1, row=4, sticky=tk.E+tk.W, padx=5, pady=5)
pulse_num_burst_meas.grid_columnconfigure(1, weight=1)
pulse_num_burst_val.set('15, 15')

## Plot Settings
plot_frame = tk.Frame(dashboard_frame, bd=2, width=375)
plot_frame.grid(column=0, row=4, sticky=tk.W+tk.E)
plot_frame.grid_columnconfigure(0, weight=1)
# Button to start sweep
ft = font.Font(size='14', weight='bold')
save_dir_btn = tk.Button(plot_frame, text='Start Pulsing', command=start_scan, font=ft)
save_dir_btn.grid(column=0, row=0, columnspan=3, sticky='EW', padx=5, pady=5)
# Progress bar for the scan
pb = ttk.Progressbar(plot_frame, orient='horizontal', mode='determinate')
# Labels for the current sens and current
sens_label = tk.Label(plot_frame)
curr_label = tk.Label(plot_frame)

# Keep previous plots
hold_on = tk.BooleanVar()
plot_hold_on_check = tk.Checkbutton(plot_frame, text='Hold On', variable=hold_on)
hold_on.set(True)
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

# Measurement Figures
fig_meas, ax_meas = plt.subplots(1, 1)
fig_meas.set_size_inches(2*8,2*2.25)
canvas_meas = mplTk.FigureCanvasTkAgg(fig_meas, master=root)
canvas_meas.get_tk_widget().grid(column=1, row=0, sticky=tk.W+tk.E)
ax_meas.set_xlabel('Measurement #')
ax_meas.set_ylabel('Current (A)')
fig_meas.tight_layout()

frame_meas_toolbar = tk.Frame(root)
frame_meas_toolbar.grid(row=1, column=1, sticky=tk.E)
toolbar_meas = mplTk.NavigationToolbar2Tk(canvas_meas, frame_meas_toolbar)
toolbar_meas.update()

# Pulse figure
fig_in, ax_in = plt.subplots(1,1)
fig_in.set_size_inches(2*8,2*2.25)
canvas_in = mplTk.FigureCanvasTkAgg(fig_in, master=root)
canvas_in.get_tk_widget().grid(column=1, row=2, sticky=tk.W+tk.E)
ax_in.set_xlabel('Measurement #')
ax_in.set_ylabel('Pulse Voltage (V)')
fig_in.tight_layout()

frame_in_toolbar = tk.Frame(root)
frame_in_toolbar.grid(row=3, column=1, sticky=tk.E)
toolbar_in = mplTk.NavigationToolbar2Tk(canvas_in, frame_in_toolbar)
toolbar_in.update()

root.mainloop()