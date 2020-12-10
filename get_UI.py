import os
import time
import argparse
from natsort import natsorted
from get import node_data as nd
from get import optical_flow as op
from get import imagepara as imgpara
from get import make_stat_data as msd
from util import util as u

parser = argparse.ArgumentParser(description='get_UI')
parser.add_argument('--config_sw', '-sw', type=int, help='config')
parser.add_argument('--model', '-model', type=str, help='modelpath')
parser.set_defaults(test=False)
args = parser.parse_args()

#switch
#1: node parameter
#2: optical flow(Lucas-Kanade)
#3: optical flow(Farneback)
#4: intensity
#5: optical flow(Lucas-Kanade)+model
#6: optical flow(Lucas-Kanade)+lerning

path=u.getdir(__file__)+'get/config/'+str(args.config_sw)+'.txt'

model=args.model

with open(path, mode='r') as f:
    line = f.readline().strip()
    while line:
        s=line.split(' ')
        if len(s)==2:
            if s[1].isdigit():exec(s[0] + '=int(s[1])')
            else: exec(s[0] + '=s[1]')
        else: exec(s[0] + '=None')
        line = f.readline().strip()

rootpath=model+'/runs'
size=[width,height]


def analyzes(savedir, tl, startt):
    with open(savedir + '/runtime.txt', mode='a') as f:

        if args.config_sw==1:#node parameter
            experiment = list()
            for dir in natsorted(os.listdir(savedir + '/act')):
                experiment.append(savedir + '/act/' + dir)

            nd.get_nodedata(experiment, savedir)
            tl.append(['output error time series', time.time()])

        elif args.config_sw==2:
            center = [(size[0] - 1) / 2, (size[1] - 1) / 2]
            op.lucas_kanade(savedir+'/images','test_19y_0.jpg', 'test_19y_1.jpg',dtct_rm=center)
            tl.append(['optical flow (Lucas-Kanade)', time.time()-startt])
            sdname='images/statdata_lk.csv'

        elif args.config_sw==3:
            center = [(size[0] - 1) / 2, (size[1] - 1) / 2]
            op.farneback(savedir+'/images','test_19y_0.jpg', 'test_19y_1.jpg'   ,dtct_rm=center)
            tl.append(['optical flow (Farneback)', time.time()-startt])

        elif args.config_sw==4:
            imgpara.get_int(savedir+'/images')
            tl.append(['average intensity', time.time()-startt])
            sdname='images/intensity.csv'

        f.write("%s\n" % tl[len(tl) - 1])

    return sdname

for savedir in natsorted(os.listdir(rootpath)):

    savedir = rootpath + '/' + savedir
    if os.path.exists(savedir + '/runtime.txt'):
        print('start_analysis',savedir)
        tl=list()#time list
        startt=time.time()
        sdname=analyzes(savedir, tl, startt)

if sd==1: msd.stat_data(sdname,model,sw,dir)
