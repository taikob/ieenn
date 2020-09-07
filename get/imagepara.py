from natsort import natsorted
import os
import cv2

def get_int(path):

    with open(path+'/intensity.csv', 'w') as f:
        intns=list()
        dintns=list()
        k=0
        for dir in natsorted(os.listdir(path)):
            if ('.jpg' in dir) and ('19' in dir):
                img = cv2.imread(os.path.join(path,dir))
                intn=0
                for i in range(img.shape[0]):
                    for j in range(img.shape[1]):
                        intn+=0.298912 * img[i,j,2] + 0.586611 * img[i,j,1] + 0.114478 * img[i,j,0]
                intns.append(intn/(img.shape[0]*img.shape[1]))
                if not k==0:
                    dintns.append(intns[k]-intns[k-1])
                k+=1
        for intn in intns:
            if not intn==intns[0]:
                f.write('\n')
            f.write(str(intn))
        for dintn in dintns:
            f.write('\n'+str(dintn))
