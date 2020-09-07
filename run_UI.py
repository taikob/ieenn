import os
import time
import argparse
import numpy as np
from datetime import datetime
from natsort import natsorted
from main import run_PredNet as r

parser = argparse.ArgumentParser(description='PredNet_UI')
parser.add_argument('--condition_sw', '-sw', default=1,  type=int, help='condition')
parser.add_argument('--fit_imagenum', '-fimn', default=1,  type=int, help='fit image number')
parser.set_defaults(test=False)
args = parser.parse_args()

if args.condition_sw==0:
    path='condition/test.txt'
elif args.condition_sw==1:
    path='condition/time_series.txt'
elif args.condition_sw==2:
    path='condition/get_optical_flow.txt'
elif args.condition_sw==3:
    path='condition/traning.txt'
elif args.condition_sw==4:
    path='condition/traning_monochrome.txt'

imagelist=natsorted(os.listdir('.'))

with open(path, mode='r') as f:
    line = f.readline().strip()
    while line:
        s=line.split(' ')
        if len(s)==2:
            if s[1].isdigit():exec(s[0] + '=int(s[1])')
            else: exec(s[0] + '=s[1]')
        else: exec(s[0] + '=None')
        line = f.readline().strip()

for image in imagelist:
    if os.path.isdir(image) and os.path.exists(image+'/read_list.txt'):
        images=image+'/read_list.txt'
        if args.fit_imagenum==1: input_len=sum([1 for _ in open(image+'/read_list.txt')])-1
        tl=list()#time list
        savedir=image+'_'+str(datetime.now().strftime('%B%d  %H:%M:%S'))
        startt=time.time()

        print(image+'_start')
        prediction_error=r.run_PredNet(images, sequences, gpu, root, initmodel, resume, \
                      size, channels, offset, input_len, ext, bprop, save, period, test, savedir)

        savedir = 'runs/' + savedir
        np.savetxt(savedir+'/prediction_error.csv',prediction_error)

        with open(savedir + '/runtime.txt', mode='a') as f:
            tl.append([image+'_network runtime',time.time()-startt])
            f.write("%s\n" % tl[len(tl) - 1])
