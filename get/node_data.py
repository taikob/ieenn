import os
import numpy as np
from natsort import natsorted
from util import util


def get_nodedata(experiment, imageroot):
    rootpath = imageroot + '/nodedata'
    # make folder list
    folder_list = util.get_folderlist(experiment[0])
    # make folder
    util.make_foldertree(rootpath, folder_list)
    unit_error = np.ndarray([len(experiment) - 1, len(folder_list)])
    params=['nodemax', 'nodemin', 'nodesum', 'nodeactsum', 'nodesupsum', 'nodeabsmin', 'nodevar']
    hunum = 0
    for huname in folder_list:
        if huname == folder_list[0]: ue_title = huname
        else: ue_title += ',' + huname
        node_error = np.ndarray([len(experiment) - 1, 0])
        unum = -1
        ne_title=str()
        for uname in natsorted(os.listdir(experiment[0] + '/' + huname)):
            if '.npy' in uname:
                node_error = np.hstack((node_error, np.ndarray([len(experiment) - 1, 1])))
                uname = uname.replace('.npy', '')
                unum += 1
                if len(ne_title) == 0:
                    ne_title = uname
                else:
                    ne_title += ',' + uname
                diflist = list()
                for path in experiment:
                    hunitpath = path + '/' + huname
                    unit = np.load(hunitpath + '/' + uname + '.npy')
                    diflist.append(unit)
                    if path == experiment[0]:
                        for param in params:
                            exec(param + '= np.ndarray([0, unit.shape[0]])')
                    for m in range(unit.shape[0]):
                        if m == 0:
                            nodemaxline = np.array([np.max(unit[m, :])])
                            nodeminline = np.array([np.min(unit[m, :])])
                            nodesumline = np.array([np.sum(unit[m, :])])
                            nodeactsumline = np.array([np.sum(np.maximum( unit[m, :],0))])
                            nodesupsumline = np.array([np.sum(np.maximum(-unit[m, :],0))])
                            nodeabsminline = np.array([np.min(np.abs(unit[m, :]))])
                            nodevarline = np.array([np.var(unit[m, :])])
                        else:
                            nodemaxline = np.append(nodemaxline, np.max(unit[m, :]))
                            nodeminline = np.append(nodeminline, np.min(unit[m, :]))
                            nodesumline = np.append(nodesumline, np.sum(unit[m, :]))
                            nodeactsumline = np.append(nodeactsumline, np.sum(np.maximum( unit[m, :],0)))
                            nodesupsumline = np.append(nodesupsumline, np.sum(np.maximum(-unit[m, :],0)))
                            nodeabsminline = np.append(nodeabsminline, np.min(np.abs(unit[m, :])))
                            nodevarline = np.append(nodevarline, np.var(unit[m, :]))
                    for param in params:
                        exec(param + '= np.append(' + param + ', np.array([' + param + 'line]), axis=0)')
                if len(experiment) != 1:
                    for n in range(len(experiment) - 1):
                        if diflist[n + 1].shape == diflist[n].shape:
                            difunit = abs(diflist[n + 1] - diflist[n])
                            node_error[n][unum] = np.sum(difunit)
                        else:
                            print('do not match size',huname, uname, experiment[n+1],  diflist[n + 1].shape, experiment[n], diflist[n].shape)
                for param in params:
                    txt=rootpath + '/' + huname + '/' + uname + '_' + param +'.csv'
                    exec('np.savetxt(\'' + txt + '\',' + param + ')')
            if len(experiment) != 1:
                np.savetxt(rootpath + '/' + huname + '/node_error.csv', node_error, header=ne_title)
                unit_error[:, hunum] = np.sum(node_error, axis=1)
        hunum += 1
    if len(experiment) != 1: np.savetxt(rootpath + '/unit_error.csv', unit_error, header=ue_title)
    return 0