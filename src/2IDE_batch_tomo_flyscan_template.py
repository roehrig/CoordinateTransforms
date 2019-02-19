#!/APSshare/anaconda/x86_64/bin/python

import epics
from epics import caput, caget
from epics import PV
import time
import numpy as np

'''
please enter the scan prameters below:
scans [x-center(um), y-center.(um), x-width.(um), y-width.(um), x-stepsize.(um), Y-stepsize.(um), dwell.(ms)]
'''

scans = [

]

pvs = ['2xfm:m24.VAL', '2xfm:m13.VAL', '2xfm:m58.VAL', '2xfm:FscanH.P1WD',
       '2xfm:Fscan1.P1WD', '2xfm:FscanH.P1SI', '2xfm:Fscan1.P1SI', '2xfm:Flyscans:Setup:DwellTime.VAL']

sample_x = PV('2xfm:m24.VAL')
sample_x_rbv = PV('2xfm:m24.RBV')
sample_y = PV('2xfm:m13.VAL')
sample_y_rbv = PV('2xfm:m13.RBV')

def calc_ETA(scan):
    dwell = scan[0][7]
    y_step = scan[0][6]
    x_step = scan[0][5]

    eta = 0
    for i in range(len(scan)):
        pixels_wide = scan[i][3]/x_step
        pixels_tall = scan[i][4]/y_step
        eta += dwell*pixels_wide*pixels_tall*1.1
        total_time = eta/1000

eta = calc_ETA(scans)

print('Batchscan starts')

for batch_num, scan in enumerate(scans):

    print('entering scan parameters for scan #{0:d}'.format(batch_num + 1))
    for i, pvs1 in enumerate(pvs):
        print ('Setting %s' % pvs1)
        caput(pvs1, scans[batch_num][i])
        time.sleep(1.)

    # check whether the motors have moved to the requested position
    print('checking whether motors are in position')
    ready = abs(sample_x_rbv.get() - sample_x.get()) < 0.1 and abs(sample_y_rbv.get() - sample_y.get()) < 0.1
    while not ready:
        print('\t Motors are not ready')
        sample_x.put(sample_x.get())
        sample_y.put(sample_y.get())
        time.sleep(3.)
        ready = abs(sample_x_rbv.get() - sample_x.get()) < 0.1 and abs(
            sample_y_rbv.get() - sample_y.get()) < 0.1
    print('\t Motors are ready now!')

    caput('2xfm:Fscan1.EXSC', 1)
    time.sleep(1)
    done = False
    print('Checking every 10 sec for scan to complete')

    while not done:
        done = caget('2xfm:Fscan1.EXSC') == 0
        print('\t Batch {0:d}/{1:d} scan is ongoing'.format(batch_num + 1, len(scans)))
        hours = np.floor(eta / 60 / 60)
        minutes = np.floor((eta / 60 / 60 - hours) * 60)
        seconds = np.floor(eta - minutes * 60 - hours * 60 * 60)
        print('ETA = Hours: {}  Min: {}  Seconds: {}'.format(hours, minutes, seconds))
        eta -= 10
        time.sleep(10.)

print('Completeted. Congratulations!')
