import os
import time
import argparse
import numpy as np
from datetime import datetime
from natsort import natsorted
from run import run_PredNet as r
from util import util as u

parser = argparse.ArgumentParser(description='run_UI')
parser.add_argument('--config_sw', '-sw', default=1,  type=int, help='config')
parser.add_argument('--fit_imagenum', '-fimn', default=1,  type=int, help='fit image number')
parser.add_argument('--model', '-m', default='',  type=str, help='initmodel')
parser.add_argument('--stimuli', '-s', default=None,  type=str, help='stimuli')
parser.set_defaults(test=False)
args = parser.parse_args()

path=u.getdir(__file__)+'run/config/'+str(args.config_sw)+'.txt'

#switch
#0: test
#1: time_series
#2: get_optical_flow
#3: traning
#4: traning_monochrome
#5: get_optical_flow_monochrome

rootpath=u.getdir(__file__).replace('ieenn/','stimuli')
if args.stimuli is not None:
    imagelist=[args.stimuli]
else:
    imagelist=natsorted(os.listdir(rootpath))

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
    images = rootpath+'/' + image + '/read_list.txt'
    image=rootpath+'/'+image
    if os.path.isdir(image) and os.path.exists(images):
        if args.fit_imagenum==1: input_len=sum([1 for _ in open(image+'/read_list.txt')])-1
        if args.model is not None: initmodel=args.model
        tl=list()#time list
        savedir=image.replace(rootpath,'')+'_'+str(datetime.now().strftime('%B%d  %H:%M:%S'))
        startt=time.time()

        print(image+'_start')
        prediction_error=r.run_PredNet(images, sequences, gpu, root, initmodel, resume, \
                      size, channels, offset, input_len, ext, bprop, save, period, test, savedir)

        savedir = u.getdir(__file__).replace('ieenn/', 'PredNet/') + savedir
        np.savetxt(savedir+'/prediction_error.csv',prediction_error)

        with open(savedir + '/runtime.txt', mode='a') as f:
            tl.append([image+'_network runtime',time.time()-startt])
            f.write("%s\n" % tl[len(tl) - 1])
