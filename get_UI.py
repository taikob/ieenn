import os
import time
from natsort import natsorted
from get import node_data as nd
#from get import optical_flow as op
from get import imagepara as imgpara

#switch
#1: node parameter
#2: optical flow
#3: optical flow

rootpath='runs'
size=[160,120]

center=[(size[0]-1)/2,(size[1]-1)/2]

sw=4


def analyzes(savedir, tl, startt):
    with open(savedir + '/runtime.txt', mode='a') as f:

        if sw==1:#node parameter
            experiment = list()
            for dir in natsorted(os.listdir(savedir + '/act')):
                experiment.append(savedir + '/act/' + dir)

            nd.get_nodedata(experiment, savedir)
            tl.append(['output error time series', time.time()])

        elif sw==2:
            op.lucas_kanade(savedir+'/images','test_19y_0.jpg', 'test_19y_1.jpg',dtct_rm=center)
            tl.append(['optical flow (Lucas-Kanade)', time.time()-startt])

        elif sw==3:
            op.farneback(savedir+'/images','test_19y_0.jpg', 'test_19y_1.jpg'   ,dtct_rm=center)
            tl.append(['optical flow (Farneback)', time.time()-startt])

        elif sw==4:
            imgpara.get_int(savedir+'/images')
            tl.append(['average intensity', time.time()-startt])

        f.write("%s\n" % tl[len(tl) - 1])

for savedir in natsorted(os.listdir(rootpath)):

    savedir = rootpath + '/' + savedir
    if os.path.exists(savedir + '/runtime.txt'):
        print('start_analysis',savedir)
        tl=list()#time list
        startt=time.time()
        analyzes(savedir, tl, startt)