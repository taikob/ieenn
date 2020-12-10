import os
from natsort import natsorted
from datetime import datetime
import csv
import re


def readtitleparam(title):

    titleparam=[]
    title=title.split('_')
    del title[len(title)-1]
    pattern = r'([+-]?[0-9]+\.?[0-9]*)'

    for t in title:
        titleparam.append(re.sub('\\D','',t))

    return [re.findall(pattern, t)[0] for t in title]


def stat_data(statdataneme, path, sw=1, dir=None):
    # statdataneme='images/statdata_lk.csv' 'images/intensity.csv'

    data = []

    if sw==1:
        rootpath = path + '/runs'

        for savedir in natsorted(os.listdir(rootpath)):
            savedir = rootpath + '/' + savedir

            if os.path.exists(savedir + '/' + statdataneme):
                datarow = readtitleparam(savedir)

                with open((savedir + '/' + statdataneme), 'r') as f:
                    datarow = datarow + f.read().split()

                data.append(datarow)


    elif sw==2:

        for savedir in natsorted(os.listdir(path)):
            modelname = savedir
            rootpath = path + '/' + savedir + '/runs'
            savedir = rootpath + '/' + dir

            if os.path.exists(rootpath):
                datarow = readtitleparam(modelname)

                with open((savedir + '/' + statdataneme), 'r') as f:
                    datarow = datarow + f.read().split()

                data.append(datarow)


    savepath = path + '/stat/' + str(datetime.now().strftime('%B%d  %H:%M:%S'))
    if not os.path.exists(savepath): os.makedirs(savepath)
    with open((savepath + '/stat_' + statdataneme.split('/')[-1]), 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(data)