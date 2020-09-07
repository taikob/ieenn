import numpy as np
import csv
from natsort import natsorted
import matplotlib.pyplot as plt
import matplotlib

dataname='stat/stat_statdata_onecolor.csv'#file path
paramrow=range(0,8)
xnum=1 # depended param
ynum=15 # check param
znum=4 # overwrap param
lnum=None # aligne param
fixparam=[[0, 1],[3, 1]] #combinate list of fix parameter index and value
addt=None#"_wr"+str(fixparam[1][1])
tc=0 #title color
pc=0 #plot color
minus=1

tt="x"+str(xnum)+"_y"+str(ynum)
if lnum is not None:
  tt+="_z"+str(znum)+"_l"+str(lnum)
elif znum is not None:
  tt+="_z"+str(znum)
if addt is not None:
  tt+=addt


def HLS_to_RGB(H, L, S):
    if not L == 0 or not L == 1:
        if not S == 0:
            tmp = S * (1 - abs(2 * L - 1)) / 2
            Max = L + tmp
            Min = L - tmp
            while H >= 360:
                H -= 360
            if 0 <= H < 60:
                return [Max, Min + (Max - Min) * H / 60, Min]
            if 60 <= H < 120:
                return [Min + (Max - Min) * (120 - H) / 60, Max, Min]
            if 120 <= H < 180:
                return [Min, Max, Min + (Max - Min) * (H - 120) / 60]
            if 180 <= H < 240:
                return [Min, Min + (Max - Min) * (240 - H) / 60, Max]
            if 240 <= H < 300:
                return [Min + (Max - Min) * (H - 240) / 60, Min, Max]
            if 300 <= H < 360:
                return [Max, Min, Min + (Max - Min) * (360 - H) / 60]
        else:
            return [L, L, L]
    elif L == 0:
        return [0, 0, 0]
    elif L == 1:
        return [1, 1, 1]

def RGB_to_colorcode(RGB):
    code='#'
    for c in RGB:
        if c < 16:
            code += str(0)
        code+=str(hex(int(c))).replace('0x','')
    return code

def get_color(H):
    RGB=HLS_to_RGB(H, 0.5, 1)
    return RGB_to_colorcode([int(255*RGB[0]), int(255*RGB[1]), int(255*RGB[2])])

def get_sysparam(data,paramrow):

  param=list()
  for i in paramrow:
    prm=[]
    for j in range(len(data)):
      if not data[j][i] in prm:
        prm.append(data[j][i])
    param.append(natsorted(prm))

  nump=[]
  for p in param:
    nump.append(len(p))

  return param,nump

def datafilter(data, fixparam):

  for param in fixparam:
    for i in reversed(range(len(data))):
      if data[i][param[0]]!=str(param[1]):
        del data[i]

  return data

def make_graphdata(data,sysparam,nump,xnum,ynum,znum,lnum,fixparam=None):

  if lnum is not None:
    aldata=np.ndarray([nump[xnum],nump[znum],nump[lnum]])
    lpara=sysparam[lnum]
    zpara=sysparam[znum]
  elif znum is not None:
    aldata=np.ndarray([nump[xnum],nump[znum], 1])
    lpara=[0]
    zpara=sysparam[znum]
  else:
    aldata=np.ndarray([nump[xnum],1,1])
    lpara=[0]
    zpara=[0]

  xpara = sysparam[xnum]

  for li, l in enumerate(lpara):
    if lnum is not None:
      ldata=np.ndarray([0,len(data[0])])
      for d in data:
        if d[lnum]==l:
          ldata=np.vstack((ldata, d))
    else:
      ldata=data

    for zi, z in enumerate(zpara):
      if znum is not None:
        zdata=np.ndarray([0,len(data[0])])
        for d in ldata:
          if d[znum]==z:
            zdata=np.vstack((zdata, d))
      else:
        zdata=ldata


      for xi, x in enumerate(xpara):
        for d in zdata:
          if d[xnum] == x:
            aldata[xi][zi][li] = d[ynum]

  return aldata

with open(dataname) as f:
  reader = csv.reader(f)
  data = [row for row in reader]

if fixparam is not None:
  data=datafilter(data, fixparam)

sysparam, nump=get_sysparam(data,paramrow)

sw=1

if sw==1:

    data=make_graphdata(data,sysparam,nump,xnum,ynum,znum,lnum)
    print(len(data))

    num = 0
    if lnum is not None:
      fig = plt.figure(figsize=(30,10))
      for l in range(nump[lnum]):
        plt.subplot(3, 4, l+1)
        plt.grid()
        plt.ylim(-np.max(np.abs(data)), np.max(np.abs(data)))
        if tc==1:
          plt.title(str(sysparam[lnum][l]),color=get_color(int(sysparam[lnum][l])))
        else:
          plt.title(str(sysparam[lnum][l]))
        ydata = data[:,:,l]
        for yn in range(0, data.shape[1]):
          if pc==1:
            plt.plot(sysparam[xnum], ydata[:, yn], '-o', label=str(sysparam[znum][yn]), color=get_color(int(sysparam[znum][yn])), linewidth=0.5, markersize=6)
          else:
            plt.plot(sysparam[xnum], ydata[:, yn], '-o', label=str(sysparam[znum][yn]), linewidth=0.5, markersize=6)

    else:
      fig = plt.figure(figsize=(8, 3))
      plt.subplot(111)
      plt.grid()
      if minus==1:
        plt.ylim(-np.max(np.abs(data)), np.max(np.abs(data)))
      else:
        plt.ylim(0, np.max(np.abs(data)))
      ydata = data[:, :, 0]
      for yn in range(0, data.shape[1]):
        if znum is not None:
            lb=str(sysparam[znum][yn])
        else:
            lb=None
        if pc==1:
          plt.plot(sysparam[xnum], ydata[:, yn], '-o', label=lb, color=get_color(int(sysparam[znum][yn])), linewidth=0.5, markersize=6)
        else:
          if znum is None:
              cl='black'
          else:
              cl=matplotlib.colors.XKCD_COLORS.items()[yn][0]
          plt.plot(sysparam[xnum], ydata[:, yn], '-o', label=lb, color=cl, linewidth=0.5, markersize=6)

    fig.savefig(tt+'_output.png')
    plt.legend().get_frame().set_alpha(1)
    fig.savefig(tt+"_legend.png", bbox_inches='tight')
    plt.close()

elif sw==2:
    with open(('stat.csv'), 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(data)