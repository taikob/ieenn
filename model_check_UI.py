import os
import argparse
from natsort import natsorted
import numpy as np
import matplotlib.pyplot as plt
from util import util as u

parser = argparse.ArgumentParser(description='model_check_UI')
parser.add_argument('--switch', '-sw', type=int, help='switch')
parser.set_defaults(test=False)
args = parser.parse_args()

# switch
# 1:prediction_error
# 2:optical flow check



path=u.getdir(__file__)+'exp/config/'+str(args.config_sw)+'.txt'

with open(path, mode='r') as f:
    line = f.readline().strip()
    while line:
        s=line.split(' ')
        if len(s)==2:
            if s[1].isdigit():exec(s[0] + '=int(s[1])')
            else: exec(s[0] + '=s[1]')
        elif len(s)==1:
            exec(s[0] + '=None')
        else:
            ss=' '.join(s[1:(len(s)+1)])
            exec(s[0] + '=ss')

        line = f.readline().strip()

modeldir=network+'/'+video


mlist = np.ndarray(0)
for dir in natsorted(os.listdir(modeldir)):
    if '.model' in dir:
        mlist = np.append(mlist, int(dir.replace('.model', '')))


if args.switch==1:

    perror=np.loadtxt(modeldir+'/prediction_error.csv')

    fig = plt.figure()
    plt.xlabel('Channel')
    plt.ylabel('Prediction error')

    #plt.xscale('log')
    #plt.yscale('log')

    ax = fig.add_subplot(111)
    plt.ylim(np.min(perror),np.max(perror))
    ax.plot(perror, '-', linewidth=1)
    #for num in mlist:
    #    print(perror[int(num)])
    #    ax.plot(num,perror[int(num)], marker='o', color='g', markersize=10)

    fig.savefig(modeldir+'/prediction_error.csv'.replace('.csv', '.png'))
    plt.close()

    print(len(perror))
    print(mlist)

elif args.switch==2:

    for model in mlist:
        os.system('python ieenn/run_UI.py -sw 2 -m '+modeldir+'/'+model+'/model.model -s stimuli/test/rotsnake')

    os.system('python ieenn/get_UI.py -sw 2 -m ' + modeldir + '/' + model + '/model.model')
