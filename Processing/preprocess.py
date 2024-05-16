import os
import numpy as np
import matplotlib.pyplot as plt
import math
import cv2
from scipy import ndimage


def getBestShift(img):
    '''
    This function finds and returns the centre of mass of an image 
    '''
    cy,cx = ndimage.measurements.center_of_mass(img)

    rows,cols = img.shape
    shiftx = np.round(cols/2.0-cx).astype(int)
    shifty = np.round(rows/2.0-cy).astype(int)

    return shiftx,shifty

def shift(img,sx,sy):
    '''
    This function shifts the image based on the centre of mass coodinates
    '''
    rows,cols = img.shape
    M = np.float32([[1,0,sx],[0,1,sy]])
    shifted = cv2.warpAffine(img,M,(cols,rows))
    return shifted

def preprocess(directory):
    i=0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath) and "GUI_DSP" in filepath:
            items = sorted(os.listdir(filepath), key=lambda x: int(x.split('.')[0]))
            for item in items:
                if "0_1" not in item:
                    img_path = os.path.join(filepath,item)
                    mean = np.round(np.mean(cv2.imread(img_path)))
                    gray = cv2.imread(img_path,cv2.IMREAD_GRAYSCALE)
                    gray = cv2.resize(255-gray, (28, 28)) # resize image to 28x28
                    test = gray
                    (thresh, gray) = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # apply threashold function
                    if (mean >= 254): # if a blank block is found
                        gray = cv2.threshold(test, 128, 0, cv2.THRESH_BINARY)[1] # ensure it is just one colour (black)
                    if(mean < 254): #else remove the outer rows
                        while np.sum(gray[0]) == 0:
                            gray = gray[1:]

                        while np.sum(gray[:,0]) == 0:
                            gray = np.delete(gray,0,1)

                        while np.sum(gray[-1]) == 0:
                            gray = gray[:-1]

                        while np.sum(gray[:,-1]) == 0:
                            gray = np.delete(gray,-1,1)

                    rows,cols = gray.shape

                    if rows > cols: # resize image to 20x20
                        factor = 20.0/rows
                        rows = 20
                        cols = int(round(cols*factor))
                        gray = cv2.resize(gray, (cols,rows))
                    else:
                        factor = 20.0/cols
                        cols = 20
                        rows = int(round(rows*factor))
                        gray = cv2.resize(gray, (cols, rows))

                    colsPadding = (int(math.ceil((28-cols)/2.0)),int(math.floor((28-cols)/2.0))) # resize back to 28x28
                    rowsPadding = (int(math.ceil((28-rows)/2.0)),int(math.floor((28-rows)/2.0))) # resize back to 28x28
                    gray = np.lib.pad(gray,(rowsPadding,colsPadding),'constant')
                    shiftx,shifty = getBestShift(gray) # get centre of mass coordinates
                    shifted = shift(gray,shiftx,shifty) # shift image according to centre of mass
                    gray = shifted           
                    
                    cv2.imwrite(f"converted/{i+1}.png", gray) # save image
                    i+=1