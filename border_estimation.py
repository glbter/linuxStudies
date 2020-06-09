import sys
import numpy as np
import PIL as pl
import matplotlib.pyplot as plt
import skimage as sk
from skimage import filters, feature, io, measure

def flipImage():
    testIm = pl.Image.open("../test20.png")
    im_flipped = testIm.transpose(method=pl.Image.FLIP_LEFT_RIGHT)
    im_flipped.show()

    #im = pl.Image.open("../os-shot_182_450/090249.png")
'''
path = str(sys.argv[1])
NAME = path
path = "../os-shot_182_450/" + path
im = io.imread(path)
'''
im = io.imread("../os-shot_182_450/090249.png")
#im = io.imread("../test21.png")

im = sk.color.rgb2gray(im)
im = filters.gaussian(im)
im2 = np.copy(im)



#im = feature.canny(im, sigma=4.5, low_threshold=0.15, high_threshold=0.15)
#im = filters.sobel(im)
def threshold(image):
    otsu = filters.threshold_otsu(image)
    return image < otsu

def conrecs():
    #im = feature.corner_shi_tomasi(im).corner_harris(im)
    keypoints1 = feature.corner_peaks(
                feature.corner_shi_tomasi(im), min_distance=1)
    print(keypoints1)
    
    extractor = feature.BRIEF()
    
    extractor.extract(im, keypoints1)
    keys = keypoints1[extractor.mask]
    
    fig, ax = plt.subplots(figsize=(18,13))
    ax.imshow(im, cmap=plt.cm.gray)
    
    for pair in keys : 
        plt.scatter(pair[0], pair[1])


'''
fig, ax = plt.subplots(figsize=(18,13))
ax.imshow(im, cmap=plt.cm.gray)
'''

def findContours(skiit_image):
    contours = measure.find_contours(skiit_image, 0.975,
                                     fully_connected="high")
    return contours
 
def plotContours(contours):
    
    fig, ax = plt.subplots(figsize=(18,13))
    ax.imshow(im, cmap=plt.cm.gray)
    
    for n, contour in enumerate(contours):
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
   
def plotContour(contour): 
    fig, ax = plt.subplots(figsize=(18,13))
    ax.imshow(im, cmap=plt.cm.gray)
    
    ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
    
conturs = findContours(im)


def maxContour(contours) -> int :
    maxLen = 0
    maxPos = 0
    for n , contur in enumerate(conturs):
        if len(contur) > maxLen:
            maxLen = len(contur)
            maxPos = n
    
    return maxPos

myContour = conturs[maxContour(conturs)]

def writeToFile(): 
    with open("../test.txt",'w') as f:
        for elem in conturs[maxContour(conturs)]  :
            f.write(str(elem))
            f.write("\n")


def plot_contour(contours):    
    myContur =  contours[maxContour(contours)]      
    fig, ax = plt.subplots(figsize=(18,13))
    #for elem in myContur:
    plt.gca().invert_yaxis()
    plt.plot(myContur[:,1], myContur[:,0])


def find_dots(contour):
    for i in (250, 500, 1400, 1800, 3300, 3550, 4650, 4900):
        plt.plot(contour[i,1], contour[i,0], 'rx')


def first_dot(contour):
    plt.plot(contour[0,1], contour[0,0], 'rx')
    return contour[0]


def pixel_average(pixels):
    pixels = np.asarray(pixels)
    
    x_avg = np.average(pixels[:,0])
    y_avg = np.average(pixels[:,1])
    
    return np.asarray([x_avg, y_avg])

    
def sort_horizontal_contour(contour, _min=1275, _max=1290):
    #_min = 35 max = 41
    #lower_contour = (pixel for pixel in contour)
    lower_contour = (x for x in contour if x[0] > _min 
                                                and x[0] < _max)

    lower_contour = sorted(
                    list(lower_contour), key=lambda x: x[1])
    #dtype = [('x', np.float64, (1,)), ('y', np.float64, (1,))]
    #lower_contour = np.fromiter(lower_contour, dtype=np.float64)
        #lower_contour = np.sort(lower_contour, order='x')

    return np.array(lower_contour)


def sort_vertical_contour(contour, _min=50, _max=55):
    #_min = 1757 max = 1763
    vert_contour = (x for x in contour if x[1] > _min 
                                                and x[1] < _max)

    vert_contour = sorted(
                    list(vert_contour), key=lambda x: x[0])
   
    return np.array(vert_contour)


#----------test----
#np.dtype(myContour)  
#lowerC = sort_lower_contour(myContour)  
#plotContour(lowerC) 
'''
ar = [[1227, 221],
    [1220, 215],
    [1230, 229]]
'''
#print(np.average(ar))
#print((pixel_average(ar)))
C = sort_horizontal_contour(myContour)  
plotContour(C)  
first_dot(C)

#plt.savefig('test/' + NAME)
    
    
    
  
