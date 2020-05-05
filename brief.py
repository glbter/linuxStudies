#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 19:16:26 2020

@author: gleb
"""
import numpy as np
from skimage import data
from skimage import transform as tf
from skimage.feature import (match_descriptors, corner_peaks, corner_harris,
                             plot_matches, BRIEF, corner_shi_tomasi)
from skimage.color import rgb2gray
import matplotlib.pyplot as plt


img1 = rgb2gray(data.astronaut())
tformMatrix = np.array([[1,0.1,10],
                        [0,1,10],
                        [0,0,1]])
tform = tf.AffineTransform(scale=(1.2, 1.2), translation=(0, -100))
#print(tform)
img2 = tf.warp(img1, tform)
#img2 = rgb2gray(data.camera())

keypoints1 = corner_peaks(corner_shi_tomasi(img1), min_distance=5)
keypoints2 = corner_peaks(corner_shi_tomasi(img2), min_distance=5)


extractor = BRIEF()

extractor.extract(img1, keypoints1)
keypoints1 = keypoints1[extractor.mask]
descriptors1 = extractor.descriptors

extractor.extract(img2, keypoints2)
keypoints2 = keypoints2[extractor.mask]
descriptors2 = extractor.descriptors

matches12 = match_descriptors(descriptors1, descriptors2
                              , cross_check=True, max_distance=0.2)


fig, ax = plt.subplots(nrows=2, ncols=1)

plt.gray()

plot_matches(ax[0], img1, img2, keypoints1, keypoints2, matches12)
#ax[0].imshow(img1)
ax[0].axis('off')
ax[0].set_title("Original Image vs. Transformed Image")

#testArrayFop = np.array([[]])

#my code

tmpArray = np.array([[0,0]])
for pos in matches12[:,0] :
   tmpArray = np.vstack((tmpArray, keypoints1[pos]))
    #tmpArray = np.append(tmpArray, keypoints1[pos], axis=0)
dst = np.delete(tmpArray, 0, axis=0)



tmpArray = np.array([[0,0]])
for pos in matches12[:,1] :
    tmpArray = np.vstack((tmpArray, keypoints2[pos]))
    #tmpArray = np.append(tmpArray, keypoints1[pos], axis=0)
#tmpArray = tmpArray.reshape(int(len(tmpArray)/2),2)  

src = np.delete(tmpArray, 0, axis=0)

estimation = tf.ProjectiveTransform()

tform = tf.estimate_transform('projective',src, dst)
estimation.estimate(src, dst)

Test = tf.warp(img2, tform)
ax[1].axis('off')
ax[1].imshow(Test)

#ax[0].plot(src[:, 0], src[:, 1], '.r')

plt.show()

