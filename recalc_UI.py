import os
import argparse
import numpy as np
from recalc import node_analysis as na
from processing import graph as gr
from recalc import evaluate as ev
from util import dotmdf as dot
from util import util as u

parser = argparse.ArgumentParser(description='recalc_UI')
parser.add_argument('--config_sw', '-sw', type=int, help='config')
parser.add_argument('--test_sw', '-tsw', type=int, help='test')
parser.add_argument('--model', '-model', type=str, help='modelpath')
parser.add_argument('--group_list', '-gl', type=str, help='group_list')
parser.add_argument('--params', '-prm', type=str, help='params')
parser.add_argument('--anapath', '-ap', type=str, help='anapath')
parser.set_defaults(test=False)
args = parser.parse_args()

#switch
#1: ???
#2: ???
#3: ???

path=u.getdir(__file__)+'recalc/config/'+str(args.config_sw)+'.txt'

with open(path, mode='r') as f:
    line = f.readline().strip()
    while line:
        s=line.split(' ')
        if len(s)==2:
            if s[1].isdigit():exec(s[0] + '=int(s[1])')
            else: exec(s[0] + '=s[1]')
        else: exec(s[0] + '=None')
        line = f.readline().strip()

savelist=list()
explist=list()

if args.test==1:
    for group in args.group_list:
        exp=list()
        num=list()
        with open(group) as f:
            w=1
            while w:
                line = f.readline().replace('\n','').split(',')
                if len(line)>1:
                    exp.append(line[0])
                    num.append(int(line[1].replace(' ','')))
                    explist.append('runs/'+line[0]+'/act/image_'+str(line[1].replace(' ','')))
                else:
                    w=0
        print(group+'_compare_data')
        savelist.append(na.compare_data(exp,num))
        print(group+'_allanalysis')
        na.all_analysis(explist, 1)

elif args.test==2:

    print('start_group_plot')
    for param in args.params:
        graphpath=na.graphdata_make(args.anapath,param,sw=0)
        gr.graph_plot(graphpath)
        graphpath=na.graphdata_make(args.anapath,param,sw=1)
        gr.graph_plot(graphpath)

    print('start_data_plot')
    if len(savelist)!=1:
        for savepath in savelist:
            for param in args.params:

                graphpath=na.graphdata_make(args.anapath,param,sw=0)
                gr.graph_plot(graphpath)

                graphpath=na.graphdata_make(args.anapath,param,sw=1)
                gr.graph_plot(graphpath)

elif args.test==3:
    switch=[1]
    for sw in switch:
        list1=ev.listup(args.anapath[0], 1)
        list2=ev.listup(args.anapath[1], 3)#, secondpath=anapath[1])
        clist=ev.complist(list1, list2, listup='eq')
        #clist=[list1]

        for ana in args.anapath:
            with open('analysis/' + ana + '/namelist.csv', mode='r') as f:
                w=1
                while w:
                    line = f.readline().replace('\n', '').split(',')
                    if len(line) > 1:
                        explist.append('runs/' + line[0] + '/act/image_' + str(line[1].replace(' ', '')))
                    else:
                        w=0

        for cl in clist:
            saveroot=cl.replace('.csv','_image')
            if not os.path.exists(saveroot): os.makedirs(saveroot)
            cl=ev.loadlist(cl)
            for key in cl.keys():
                for n in cl[key]:
                    gr.compare_channel(saveroot, explist, key, n)
            dot.make_cgimage(saveroot, chilfol=1)

        #xc=np.array([3,3.5,4,4.5,5,6,7,8,9,10,11,12])
        for cl in clist:
            saveroot=cl.replace('.csv','_graph')
            cl=ev.loadlist(cl)
            for key in cl.keys():
                if len(cl[key]):
                    savefol=saveroot+'/'+key.split('/')[0]
                    if not os.path.exists(savefol): os.makedirs(savefol)
                    y=gr.evaluated_channel('analysis/' + args.anapath[0], key, cl[key], sw)#, x=xc)
                    np.savetxt(saveroot+'/'+key+'.csv', y, header=','.join(cl[key]))
            gr.graph_plot(saveroot,defi=1)
