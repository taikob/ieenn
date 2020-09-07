import os
import sys
import numpy as np
from natsort import natsorted
from datetime import datetime
from util import dotmdf as dot
from util import util
from processing import graph as g


def all_analysis(experiment, switch):
    folder_list = util.get_folderlist(experiment[0])

    netlist=list()
    if len(experiment)!=1:
        rootpath='analysis/image_'+str(datetime.now().strftime('%B%d  %H:%M:%S'))
        if not os.path.exists(rootpath): os.makedirs(rootpath)
        with open(rootpath + '/experiments.txt', mode='w') as f:
            for exp in experiment:
                f.write(exp.split('/')[-3]+'_'+exp.split('/')[-1]+ '\n')
        if switch==1:
            for exp in experiment:
                folname='comp_'+exp.split('/')[-3]+'_'+exp.split('/')[-1]
                netlist.append(folname)
                util.make_foldertree(rootpath +'/'+folname, folder_list)
        elif switch==2:
            for n in range(len(experiment) - 1):
                for m in range(n+1,len(experiment)):
                    name1=experiment[n].split('/')[-3]+'_'+experiment[n].split('/')[-1]
                    name2=experiment[m].split('/')[-3]+'_'+experiment[m].split('/')[-1]
                    folname='dif_'+name1+'-'+name2
                    netlist.append(folname)
                    util.make_foldertree(rootpath +'/'+folname , folder_list)
    else:
        if switch == 2:
            print('number of experiments should be more than 1.')
            sys.exit(1)
        else:
            netlist.append(str())
            rootpath=experiment[0]


    for huname in folder_list:
        print(huname)
        for uname in natsorted(os.listdir(experiment[0] + '/' + huname)):
            if '.npy' in uname:
                uname = uname.replace('.npy', '')
                unitlist = list()
                for path in experiment:
                    unitlist.append(np.load(path + '/' + huname + '/' + uname + '.npy'))

                if switch==1:
                    norm=0
                    for node in unitlist:
                        if np.max(np.abs(node))>norm:
                            norm=np.max(np.abs(node))
                    for n in range(len(experiment)):
                        if len(experiment)==1: folname=str()
                        else: folname='/comp_'+experiment[n].split('/')[-3]+'_'+experiment[n].split('/')[-1]
                        g.plot_image(unitlist[n], rootpath +folname+ '/' + huname + '/' + uname, uname, nor=norm)

                elif switch==2:
                    for n in range(len(experiment) - 1):
                        for m in range(n+1,len(experiment)):
                            difunit = unitlist[n] - unitlist[m]
                            name1=experiment[n].split('/')[-3]+'_'+experiment[n].split('/')[-1]
                            name2=experiment[m].split('/')[-3]+'_'+experiment[m].split('/')[-1]
                            folname='dif_'+name1+'-'+name2
                            g.plot_image(difunit, rootpath + '/' +folname+ '/' + huname + '/' + uname, uname)
    print(netlist)
    for folname in netlist:
        print(rootpath, folname)
        dot.make_cgimage(rootpath, subfol=folname)

def compare_data(savedirlist,numlist):
    anadir =  'analysis/'+str(datetime.now().strftime('%B%d  %H:%M:%S'))
    if not os.path.exists(anadir): os.makedirs(anadir)

    with open(anadir + '/namelist.csv', mode='w') as f:
        n=0
        for savedir in savedirlist:
            f.write(savedir+','+str(numlist[n])+'\n')
            n+=1

    folderlist=util.get_folderlist('runs/'+savedirlist[0]+'/nodedata')
    util.make_foldertree(anadir, folderlist)
    for folder in folderlist:
        for dir in os.listdir('runs/' +savedirlist[0]+'/nodedata/'+folder):
            if os.path.isfile('runs/' +savedirlist[0]+'/nodedata/'+folder+'/'+dir) and '.csv' in dir:
                n=0
                for savedir in savedirlist:
                    filepath='runs/' +savedir+'/nodedata/'+folder+'/'+dir
                    data = np.loadtxt(filepath)
                    if data.ndim == 1 and data.size != 0:
                        if n == 0:
                            cpdata = np.ndarray([0]) #compared data
                        if 'node_error.csv' in filepath:
                            cpdata = np.append(cpdata, np.array([data[numlist[n]-1  ]])        )
                        else:
                            cpdata = np.append(cpdata, np.array([data[numlist[n]    ]])        )
                    elif data.ndim == 2:
                        if n == 0:
                            cpdata = np.ndarray([0, data.shape[1]]) #compared data
                        if 'node_error.csv' in filepath:
                            cpdata = np.append(cpdata, np.array([data[numlist[n]-1,:]]), axis=0)
                        else:
                            cpdata = np.append(cpdata, np.array([data[numlist[n]  ,:]]), axis=0)
                    n+=1
                if data.size != 0:
                    np.savetxt(anadir + '/' + folder + '/' + dir, cpdata)
    return anadir.replace('analysis/','')

def graphdata_make(grouplist,param,sw=0):
    #graph_check
    root='analysis'
    if isinstance(grouplist,str): grouplist=[grouplist]
    if sw==0:   optn=str()
    elif sw==1: optn='_change_rate'

    imgroot = root + '/graph_' +param+'_sw'+str(sw)+'_'+ str(datetime.now().strftime('%B%d  %H:%M:%S'))
    folder_list=util.get_folderlist(root+'/'+grouplist[0])
    util.make_foldertree(imgroot, folder_list)

    with open(imgroot + '/condition.csv',mode='w') as c:
        c.write('parameter : ' + param + '\n')
        c.write('sw :'+str(sw)+'\n')
        for fol in grouplist:
            c.write('analyzed data :'+fol+'\n')
            with open(root + '/' + fol + '/namelist.csv') as f:
                for line in f.readlines():
                    c.write(line)

    for folder in folder_list:
        imgfolder=imgroot+'/'+folder
        folder=root+'/'+grouplist[0]+'/'+folder
        for dir in natsorted(os.listdir(folder)):
            if param in dir and '.csv' in dir:
                for anafol in grouplist:
                    dirpath=(folder+'/'+dir).replace(grouplist[0],anafol)
                    imgpath=imgfolder + '/' + dir
                    data = np.loadtxt(dirpath)

                    if grouplist[0] in anafol:
                        graphdata=np.ndarray([data.shape[1],1])
                        graphdata[:,0]=np.array(range(data.shape[1]))#channel number
                        headline='x'

                    if sw==0:#value
                        if len(grouplist)==1:#all kind plot
                            with open(root+'/'+anafol+ '/namelist.csv') as f:
                                lines = f.readlines()
                            for yn in range(data.shape[0]):
                                y=np.ndarray([data.shape[1],1])
                                y[:,0]=np.array(data[yn,:])#channel number
                                graphdata = np.hstack((graphdata, y))
                                headline+=lines[yn]+','
                        else:#average of group
                            y=np.ndarray([data.shape[1],1])
                            y[:,0]=np.array(np.mean(data, axis=0))#channel number
                            graphdata = np.hstack((graphdata, y))
                            headline+=anafol+','

                    elif sw==1:#change_rate
                        ydata=np.zeros(data.shape[1])
                        for ch in range(data.shape[1]):
                            mx=np.max(data[:,ch])
                            mn=np.min(data[:,ch])
                            if not np.isnan(mx) and not np.isnan(mn):
                                if np.abs(mx)>np.abs(mn):
                                    ydata[ch]=(mx-mn)/mx
                                else:
                                    ydata[ch]=(mn-mx)/mn
                            else:
                                ydata[ch]=np.NaN
                        y=np.ndarray([data.shape[1],1])
                        y[:,0]=np.array(ydata)#channel number
                        graphdata = np.hstack((graphdata, y))
                        headline+=anafol+','

                headline=headline.rstrip(',')
                np.savetxt(imgpath, graphdata, header=headline)
    return imgroot

