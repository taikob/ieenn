import os
from natsort import natsorted
from datetime import datetime
import csv
import re

rootpath='runs'
saveroot='stat'
savepath=saveroot+'/'+str(datetime.now().strftime('%B%d  %H:%M:%S'))

sw=2

def readtitleparam(title):

    titleparam=[]
    title=title.split('_')
    del title[len(title)-1]
    pattern = r'([+-]?[0-9]+\.?[0-9]*)'

    for t in title:
        titleparam.append(re.sub('\\D','',t))

    return [re.findall(pattern, t)[0] for t in title]

if sw==1:
    statdataneme='images/statdata_lk.csv'
    titledatanum=3
elif sw==2:
    statdataneme='images/intensity.csv'

if not os.path.exists(savepath): os.makedirs(savepath)

data=[]
for savedir in natsorted(os.listdir(rootpath)):
    savetitle=savedir
    savedir = rootpath + '/' + savedir

    if os.path.exists(savedir+'/'+statdataneme):

        datarow=readtitleparam(savedir)

        with open((savedir+'/'+statdataneme), 'r') as f:
            datarow = datarow + f.read().split()

        data.append(datarow)

with open((savepath+ '/stat_' + statdataneme.split('/')[-1]), 'w') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(data)