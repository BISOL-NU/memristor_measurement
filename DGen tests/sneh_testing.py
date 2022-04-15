from instr_inter import DG645

instr_lib = DG645.DG645(
    bnc='2',
    channel_start = '4',  channel_end = '5'
)

while True:
    instr_lib.config_burst(50e-6,100e-6,3,1/(200e-6),1)
    instr_lib.trig_burst()
    #instr_lib.check_error()