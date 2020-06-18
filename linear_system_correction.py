import sys
import os
import numpy as np
import PIL as pl
import matplotlib.pyplot as plt
import skimage as sk
from skimage import filters, feature, io, measure
from skimage import transform as tf

from skimage.registration import optical_flow_tvl1


def findContours(skiit_image):
    contours = measure.find_contours(skiit_image, 0.975,
                                     fully_connected="high")
    return contours
 
   
def plotContour(contour, im): 
    #testing func
    fig, ax = plt.subplots(figsize=(18,13))
    ax.imshow(im, cmap=plt.cm.gray)
    
    #ax.plot(contour[:, 1], contour[:, 0], linewidth=2, marker='o')
    ax.scatter(contour[:, 1], contour[:, 0])


def maxContour(contours) -> int :
    #return the contour of the image
    maxLen = 0
    maxPos = 0
    for n , contur in enumerate(contours):
        if len(contur) > maxLen:
            maxLen = len(contur)
            maxPos = n
    
    return maxPos
    

def pixel_average(pixels):
    pixels = np.asarray(pixels)
    
    x_avg = np.average(pixels[:,0])
    y_avg = np.average(pixels[:,1])
    
    return np.asarray([x_avg, y_avg])

    
def sort_horizontal_contour(contour, _min=1275, _max=1290):
    #_min = 35 max = 41
    lower_contour = (x for x in contour if x[0] > _min 
                                                and x[0] < _max)
    lower_contour = sorted(
                    list(lower_contour), key=lambda x: x[1])
    return np.array(lower_contour)


def sort_vertical_contour(contour, _min=50, _max=55):
    #_min = 1757 max = 1763
    #x is piXel
    vert_contour = (x for x in contour if x[1] > _min 
                                                and x[1] < _max)
    vert_contour = sorted(
                    list(vert_contour), key=lambda x: x[0])
    return np.array(vert_contour)


def derivative(contour):
    c = contour
    b = [c[i+1]-c[i-1]  for i in range(1,len(c)-1) ]
    b.insert(0,0)
    b.append(0)
    return b


def binary_derivative(contour):
    dy = derivative(contour[:,0])
    dx = derivative(contour[:,1])
    df = list(zip(dy, dx))
    df = np.asarray(df, dtype=np.float64)
    return df


def isNotConst(derivative):
    test = []
    der = np.abs(derivative)
    
    for elem in der:
        if (elem > 1) and (elem < 3) : 
            test.append(False)
        else:
            test.append(True)
    return np.asarray(test)   


def checkCorners(derivatives):
    y = isNotConst(derivatives[:,0])
    x = isNotConst(derivatives[:,1])
    F = zip(y, x)
    res = map(lambda x: x[0] and x[1], F)
    res = list(res)
    return np.asarray(res)


def get2Points(part_contour):
    middle_point = lambda pix1, pix2 : \
        np.asarray([(pix1[0]+pix2[0]) / 2, (pix1[1]+pix2[1]) / 2])
    #random contuor points
    p1 = part_contour[150]
    p2 = part_contour[300]
    length = len(part_contour)
    p3 = part_contour[length - 300]
    p4 = part_contour[length - 150]
    pA1 = part_contour[225]
    pA2 = part_contour[length - 225]
    
    pixel1 = middle_point(p1,p2)
    pixel2 = middle_point(p3,p4)
    pixel1 = middle_point(pixel1, pA1)
    pixel2 = middle_point(pixel2, pA2)
    return np.array([pixel1, pixel2])


def find_tang(dots):
    #tang of contour line
    y1 = dots[0][0]
    y2 = dots[1][0]
    x1 = dots[0][1]
    x2 = dots[1][1]
    return (y2-y1) / (x2-x1)


def find_const(tang, dots):
    #linear fucntion constant y = kx + b
    y = (dots[0][0]+dots[1][0]) / 2
    x = (dots[0][1]+dots[1][1]) / 2
    return y - tang*x 


def solve_lenal(tang1, tang2, const1, const2):
    #find intersection of two lines
    params = np.array([[1, -tang1],
                      [1, -tang2]])
    constants = np.array([const1, 
                         const2])
    
    return np.linalg.solve(params, constants)


def get_part_contour(contour):
    #divide contour in 4 parts
    vert = sort_vertical_contour(contour)
    hor = sort_horizontal_contour(contour)
    vert2 = sort_vertical_contour(contour, 1757, 1763)
    hor2 = sort_horizontal_contour(contour, 35, 41)
    partial_contour = (vert, hor, vert2, hor2)
    return partial_contour


def get_line_params(partial_contour):
    #for each line get tang and const
    line_params = []
    for cont in partial_contour:
        dots = get2Points(cont)
        tang = find_tang(dots)
        const = find_const(tang, dots)
        line_params.append((tang, const))
    return line_params   
    

def get_image_corners(line_params):
    #get resulting corner points
    result_dots = []
    first = line_params[0]
    for params in line_params:
        if params == first:
            prev = first
            continue
        # 0-pos is tang, 1-pos is const
        r = solve_lenal(params[0], prev[0], params[1], prev[1])
        prev = params
        result_dots.append(r)
        
    r = solve_lenal(first[0], prev[0], first[1], prev[1]) 
    result_dots.append(r)  
    return np.asarray(result_dots) 


def all_images_average(all_images_points):
    # count averege point from all imeges
    # for each of 4 corner point
    res = []
    for point in range(4):
        y = np.average(all_images_points[:,point,0])
        x = np.average(all_images_points[:,point,1])
        res.append((y,x))
    return np.asarray(res)
    

def optical_flow_correction(images):
    #be carefull    
    #works with picture artifacts
    # --- Use the estimated optical flow for registration
    example = sk.color.rgb2gray(images[0])
    nr, nc = example.shape
    row_coords, col_coords = np.meshgrid(np.arange(nr), np.arange(nc),
                                         indexing='ij')
    warped_images = []
    for image in images :
        image = sk.color.rgb2gray(image)
        v, u = optical_flow_tvl1(example, image)   
       
        image_warp = tf.warp(image, np.array([row_coords + v, 
                                                  col_coords + u]),
                                                  mode='nearest')
        '''
        colors = []
        for channel in range(3) :
            color = image[..., channel]

            # --- Compute the optical flow
            v, u = optical_flow_tvl1(example,color)   
       
            color_warp = tf.warp(image, np.array([row_coords + v, 
                                                  col_coords + u]),
                                                  mode='nearest')

            colors.append(color_warp) 
        # build an RGB image with the registered sequence
        reg_im = np.zeros((nr, nc, 3))
        reg_im[..., 0] = color[0]
        reg_im[..., 1] = color[1]
        reg_im[..., 2] = color[2]
            
        warped_images.append(reg_im)
        '''
        warped_images.append(image_warp)
        example = image
        
    return np.asarray(warped_images)


def main():
    path_to_files = '../os-shot_182_450/'
    os.chdir(path_to_files)
    files = os.listdir()
   
    each_result = []
    images = []
    for image in files:
        try:
            im = io.imread(image)  
        except ValueError as e :
            print('ERROR')
            print(e)
            continue
        
        images.append(im)
        im = sk.color.rgb2gray(im)
        #find all contours
        conturs = findContours(im)
        #find the biggest
        myContour = conturs[maxContour(conturs)]
        #divide it
        partContour = get_part_contour(myContour)
        #get linear equations
        lineParams = get_line_params(partContour)
        #solve linear systems (get intersection)
        resultPoints = get_image_corners(lineParams)
        #save it
        each_result.append(resultPoints)
    
    images = np.asarray(images)
    each_result = np.asarray(each_result)
    #find average
    average_points = all_images_average(each_result)
   
    estimation = tf.EuclideanTransform()
    
    warped_images = []
    for image, dots in zip(images, each_result):
        dst = average_points
        src = dots

        tform = tf.estimate_transform('Euclidean',src, dst)
        estimation.estimate(src, dst)
        
        img = tf.warp(image, tform)
        warped_images.append(img)
    
    warped_images = np.asarray(warped_images)
   
    # uses optical flow to stable images
   # warped_images = optical_flow_correction(warped_images)
    
    os.mkdir('result')
    os.chdir('result')
    
    for name, result in zip(files, warped_images):  
            io.imsave(name, result)


if __name__ == '__main__':
    main()

   
