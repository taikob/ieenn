import os
import cv2
import yaml
import itertools
import csv
import numpy as np
from recalc import r_util as ru


colormap = {'blue': [255, 0, 0], 'green': [0, 255, 0], 'red': [0, 0, 255],
            'yellow': [0, 255, 255], 'white': [255, 255, 255]}
config = yaml.load(open('ieenn/config.yaml'),Loader=yaml.SafeLoader)

def detect_rotmo(o,op,vec):#dimension of o and op must be 2

    opo=np.zeros(len(op))

    r=0
    norm=0
    for i in range(len(op)):
        opo[i]=op[i]-o[i]
        r    +=opo[i]**2
        norm +=vec[i]**2

    r   =np.sqrt(r)
    norm=np.sqrt(norm)
    if r !=0 and norm < r:
        rotnorm=(-vec[0]*opo[1] + vec[1]*opo[0]) /r
        if abs(rotnorm)/norm>=np.sqrt(2)/2:
            return rotnorm
        else:
            return 0
    else:
        return 0

def detect_errorflow(good_new, good_old):
    angles=np.ndarray(0)
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        dx = a - c
        dy = b - d

        th= np.arccos(dx/(np.sqrt(dx*dx+dy*dy)))

        if dy > 0:
            angles = np.append(angles, th)
        else:
            angles = np.append(angles, 2*np.pi-th)

    return np.std(angles)




def lucas_kanade(root,file1, file2,cc='yellow',lc='red',s=1,l=2, dtct_rm=None):
    conf = config['LucasKanade']
    # params for ShiTomasi corner detection
    feature_params = dict(maxCorners = 100,
                          qualityLevel = conf['quality_level'],
                          minDistance = 7,
                          blockSize = 7)

    # Parameters for lucas kanade optical flow
    lk_params = dict(winSize = (conf['window_size'],
                                conf['window_size']),
                     maxLevel = 2,
                     criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    img1 = cv2.imread(os.path.join(root,file1))
    img2 = cv2.imread(os.path.join(root,file2))
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    met='lk'
    vs=50
    p0 = cv2.goodFeaturesToTrack(img1_gray, mask = None, **feature_params)
    mask = np.zeros_like(img1)
    p1, st, err = cv2.calcOpticalFlowPyrLK(img1_gray, img2_gray, p0, None, **lk_params)

    good_new = p1[st==1]
    good_old = p0[st==1]

    # draw the tracks
    std=detect_errorflow(good_new, good_old)

    data = []
    ofabs=np.ndarray(0)
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        dx = a - c
        dy = b - d
        if dtct_rm is not None:
            norm=detect_rotmo(dtct_rm,[c,d],[dx,dy])
        else:
            norm=np.sqrt(dx**2+dy**2)
        data.append([c, d, dx, dy,norm])
        dx = vs * dx
        dy = vs * dy
        if norm==0:
            cv2.line  (mask, (c, d), (int(c + dx), int(d + dy)), colormap['green'],l)
            cv2.line  (img2, (c, d), (int(c + dx), int(d + dy)), colormap['green'],l)
        else:
            cv2.line  (mask, (c, d), (int(c + dx), int(d + dy)), colormap[lc],l)
            cv2.line  (img2, (c, d), (int(c + dx), int(d + dy)), colormap[lc],l)
        cv2.circle(mask, (c, d), s, colormap[cc], -1)
        cv2.circle(img2, (c, d), s, colormap[cc], -1)
        if norm==0: continue
        else: ofabs = np.append(ofabs, norm)

    cv2.imwrite(os.path.join(root,'vectors_'+met+'.jpg'), mask)
    cv2.imwrite(os.path.join(root,'result_'+met+'.jpg'), img2)
    if np.count_nonzero(ofabs > 0)!=0:
        aveact=ru.actsum(ofabs) / np.count_nonzero(ofabs > 0)
    else:
        aveact=0
    if np.count_nonzero(ofabs < 0)!=0:
        avesup=ru.supsum(ofabs) / np.count_nonzero(ofabs < 0)
    else:
        avesup=0
    stdata=np.array([ru.actsum(ofabs),aveact, np.count_nonzero(ofabs > 0),
                     ru.supsum(ofabs),avesup, np.count_nonzero(ofabs < 0),
                     ofabs.sum(), ofabs.mean(),len(ofabs),std])
    np.savetxt(os.path.join(root,'statdata_'+met+'.csv'),stdata)
    with open(os.path.join(root,'data_'+met+'.csv'), 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(data)

def farneback(root,file1, file2,cc='yellow',lc='red',vs=4,s=1,l=2, dtct_rm=False):
    conf = config['Farneback']
    frame1 = cv2.imread(os.path.join(root,file1))
    prv = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(frame1)
    frame2 = cv2.imread(os.path.join(root,file2))
    nxt = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(prv, nxt, None, 0.5, 3,
                                        conf['window_size'],
                                        3, 5, 1.2, 0)
    height, width = prv.shape

    data = []
    for x, y in itertools.product(range(0, width, conf['stride']),
                                  range(0, height, conf['stride'])):
        if np.linalg.norm(flow[y, x]) >= conf['min_vec']:
            dx, dy = flow[y, x].astype(float)
            data.append([x, y, dx, dy])
            dx = vs * dx
            dy = vs * dy
            cv2.line  (mask  , (x, y), (x + int(dx), y + int(dy)), colormap[lc], l)
            cv2.line  (frame2, (x, y), (x + int(dx), y + int(dy)), colormap[lc], l)
            cv2.circle(mask  , (x, y), s, colormap[cc], -1)
            cv2.circle(frame2, (x, y), s, colormap[cc], -1)
    cv2.imwrite(os.path.join(root,'vectors_fb.jpg'), mask)
    cv2.imwrite(os.path.join(root,'result_fb.jpg'), frame2)
    with open(os.path.join(root,'data_fb.csv'), 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(data)

        def farneback(root, file1, file2, cc='yellow', lc='red', vs=4, s=1, l=2):
            conf = config['Farneback']
            frame1 = cv2.imread(os.path.join(root, file1))
            prv = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            mask = np.zeros_like(frame1)
            frame2 = cv2.imread(os.path.join(root, file2))
            nxt = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            flow = cv2.calcOpticalFlowFarneback(prv, nxt, None, 0.5, 3,
                                                conf['window_size'],
                                                3, 5, 1.2, 0)
            height, width = prv.shape

            data = []
            for x, y in itertools.product(range(0, width, conf['stride']),
                                          range(0, height, conf['stride'])):
                if np.linalg.norm(flow[y, x]) >= conf['min_vec']:
                    dx, dy = flow[y, x].astype(float)
                    if dtct_rm:
                        norm=dtct_rm()
                    else:
                        norm=np.sqrt(dx**2+dy**2)
                    data.append([x, y, dx, dy, norm])
                    ofabs = np.append(ofabs, norm)
                    dx = vs * dx
                    dy = vs * dy
                    cv2.line  (mask,  (x, y), (x + int(dx), y + int(dy)), colormap[lc], l)
                    cv2.line  (frame2,(x, y), (x + int(dx), y + int(dy)), colormap[lc], l)
                    cv2.circle(mask,  (x, y), s, colormap[cc], -1)
                    cv2.circle(frame2,(x, y), s, colormap[cc], -1)
            cv2.imwrite(os.path.join(root, 'vectors_fb.jpg'), mask)
            cv2.imwrite(os.path.join(root, 'result_fb.jpg'), frame2)
            if np.count_nonzero(ofabs > 0) != 0:
                aveact = ru.actsum(ofabs) / np.count_nonzero(ofabs > 0)
            else:
                aveact = 0
            if np.count_nonzero(ofabs < 0) != 0:
                avesup = ru.supsum(ofabs) / np.count_nonzero(ofabs < 0)
            else:
                avesup = 0
            stdata = np.array([ru.actsum(ofabs), aveact, np.count_nonzero(ofabs > 0),
                               ru.supsum(ofabs), avesup, np.count_nonzero(ofabs < 0),
                               ofabs.sum(), ofabs.mean(), len(ofabs)])
            np.savetxt(os.path.join(root,'statdata_fb.csv'),stdata)
            with open(os.path.join(root, 'data_fb.csv'), 'w') as f:
                writer = csv.writer(f, lineterminator='\n')
                writer.writerows(data)

#def get_parameter(file):
