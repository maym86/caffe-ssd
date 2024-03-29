#!/usr/bin/python

import numpy as np
import sys,os
import cv2
caffe_root = '/home/maym86/code/forks/caffe-ssd/'
sys.path.insert(0, caffe_root + 'python')
import caffe
import time
import glob
caffe.set_device(0)
caffe.set_mode_gpu()

net_file= 'MobileNetSSD_deploy.prototxt'
caffe_model='MobileNetSSD_deploy10695.caffemodel'

video_capture = cv2.VideoCapture(0)

if not os.path.exists(caffe_model):
    print("MobileNetSSD_deploy.affemodel does not exist,")
    print("use merge_bn.py to generate it.")
    exit()
net = caffe.Net(net_file,caffe_model,caffe.TEST)

CLASSES = ('background',
           'person')


def preprocess(src):
    img = cv2.resize(src, (300,300))
    img = img - 127.5
    img = img * 0.007843
    return img

def postprocess(img, out):
    h = img.shape[0]
    w = img.shape[1]
    box = out['detection_out'][0,0,:,3:7] * np.array([w, h, w, h])

    cls = out['detection_out'][0,0,:,1]
    conf = out['detection_out'][0,0,:,2]
    return (box.astype(np.int32), conf, cls)


def detect(files=[]):
    global idx

    if files == []:
        ret, origimg = video_capture.read()
    else:
        if idx >= len(files):
            return False
        origimg = cv2.imread(files[idx])
        idx+=1

    img = preprocess(origimg)
    img = img.astype(np.float32)
    img = img.transpose((2, 0, 1))

    net.blobs['data'].data[...] = img
    start = time.time()
    out = net.forward()
    use_time=time.time() - start
    print("time="+str(use_time)+"s")
    box, conf, cls = postprocess(origimg, out)
    
    height, height, width = origimg.shape
    for i in range(len(box)):
        if conf[i] > 0.3: # and abs(box[i][0] - box[i][2]) < height / 3:
            p1 = (box[i][0], box[i][1])
            p2 = (box[i][2], box[i][3])
            cv2.rectangle(origimg, p1, p2, (0,255,0))
            p3 = (max(p1[0], 15), max(p1[1], 15))
            title = "%s:%.2f" % (CLASSES[int(cls[i])], conf[i])
            cv2.putText(origimg, title, p3, cv2.FONT_ITALIC, 0.6, (0, 255, 0), 1)

    cv2.imshow("SSD", origimg)

    k = cv2.waitKey(50)
    if k==27:
        return False

    return True

if __name__ == '__main__':
    global idx
    #files = glob.glob("/home/maym86/pedestrian_data/INRIAPerson/pos/*.png")
    files = [] #glob.glob("/home/maym86/pedestrian_data/TUD-Brussels/*.png")
    files.sort()
    idx = 0
    while detect(files):
        pass

