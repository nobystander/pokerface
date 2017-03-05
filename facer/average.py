# -*- coding=utf8 -*-
"""
    生成平均脸
"""
import os
import cv2
import numpy as np
import math
import json
from model import FemaleFace

keyPoints = ['mouth_upper_lip_left_contour2',
             'contour_chin',
             'mouth_lower_lip_right_contour3',
             'mouth_upper_lip_left_contour1',
             'left_eye_upper_left_quarter',
             'left_eyebrow_lower_middle',
             'mouth_upper_lip_left_contour3',
             'left_eyebrow_lower_left_quarter',
             'nose_contour_left3',
             'right_eye_pupil',
             'left_eyebrow_upper_left_quarter',
             'mouth_lower_lip_left_contour2',
             'left_eye_bottom',
             'mouth_lower_lip_bottom',
             'contour_left9',
             'left_eye_lower_right_quarter',
             'mouth_lower_lip_top',
             'contour_right6',
             'right_eye_bottom',
             'contour_right9',
             'contour_left6',
             'contour_left5',
             'contour_left4',
             'contour_left3',
             'contour_left2',
             'contour_left1',
             'left_eye_lower_left_quarter',
             'contour_right1',
             'contour_right3',
             'contour_right2',
             'contour_right5',
             'contour_right4',
             'contour_right7',
             'left_eyebrow_left_corner',
             'nose_right',
             'nose_tip',
             'nose_contour_lower_middle',
             'right_eye_top',
             'mouth_lower_lip_left_contour3',
             'right_eye_right_corner',
             'right_eye_lower_right_quarter',
             'mouth_upper_lip_right_contour2',
             'right_eyebrow_lower_right_quarter',
             'contour_left7',
             'mouth_right_corner',
             'mouth_lower_lip_right_contour1',
             'contour_right8',
             'left_eyebrow_right_corner',
             'right_eye_center',
             'left_eye_pupil',
             'left_eye_upper_right_quarter',
             'mouth_upper_lip_top',
             'nose_left',
             'right_eyebrow_lower_middle',
             'left_eye_top',
             'left_eye_center',
             'contour_left8',
             'right_eyebrow_left_corner',
             'right_eye_left_corner',
             'right_eyebrow_lower_left_quarter',
             'left_eye_left_corner',
             'mouth_left_corner',
             'right_eyebrow_upper_left_quarter',
             'left_eye_right_corner',
             'right_eye_lower_left_quarter',
             'right_eyebrow_right_corner',
             'right_eye_upper_left_quarter',
             'left_eyebrow_upper_middle',
             'mouth_lower_lip_right_contour2',
             'nose_contour_left1',
             'nose_contour_left2',
             'mouth_upper_lip_right_contour1',
             'nose_contour_right1',
             'nose_contour_right2',
             'nose_contour_right3',
             'mouth_upper_lip_bottom',
             'right_eyebrow_upper_middle',
             'left_eyebrow_lower_right_quarter',
             'right_eyebrow_upper_right_quarter',
             'mouth_upper_lip_right_contour3',
             'left_eyebrow_upper_right_quarter',
             'right_eye_upper_right_quarter',
             'mouth_lower_lip_left_contour1']
keyPointsNumber = len(keyPoints)


def readPoints(landmark):
    points = []
    for item in keyPoints:
        # 所有的图片都是640 * 480
        # 为了通用考虑可以获取图片尺寸
        x, y = landmark[item]['x'] , landmark[item]['y'] 
        points.append((int(x), int(y)))
    return points

# Read all jpg images in folder.
def readImages(fileList) :

    imagesArray, pointsArray = [], []

    #List all files in the directory and read points from text files one by one
    for filePath in fileList:
        if filePath.endswith(".jpg"):
            # Read image found.
            img = cv2.imread(filePath)

            # Convert to floating point
            img = np.float32(img)/255.0

            # Add to array of images
            imagesArray.append(img)

            filename = os.path.basename(filePath)
            landmark = json.loads(FemaleFace.get(filename).landmark)

            pointsArray.append(readPoints(landmark))

    return imagesArray, pointsArray

# Compute similarity transform given two sets of two points.
# OpenCV requires 3 pairs of corresponding points.
# We are faking the third one.

def similarityTransform(inPoints, outPoints) :
    s60 = math.sin(60*math.pi/180)
    c60 = math.cos(60*math.pi/180)

    inPts = np.copy(inPoints).tolist()
    outPts = np.copy(outPoints).tolist()

    xin = c60*(inPts[0][0] - inPts[1][0]) - s60*(inPts[0][1] - inPts[1][1]) + inPts[1][0]
    yin = s60*(inPts[0][0] - inPts[1][0]) + c60*(inPts[0][1] - inPts[1][1]) + inPts[1][1]

    inPts.append([np.int(xin), np.int(yin)])

    xout = c60*(outPts[0][0] - outPts[1][0]) - s60*(outPts[0][1] - outPts[1][1]) + outPts[1][0]
    yout = s60*(outPts[0][0] - outPts[1][0]) + c60*(outPts[0][1] - outPts[1][1]) + outPts[1][1]

    outPts.append([np.int(xout), np.int(yout)])

    tform = cv2.estimateRigidTransform(np.array([inPts]), np.array([outPts]), False)

    return tform


# Check if a point is inside a rectangle
def rectContains(rect, point) :
    if point[0] < rect[0] :
        return False
    elif point[1] < rect[1] :
        return False
    elif point[0] > rect[2] :
        return False
    elif point[1] > rect[3] :
        return False
    return True

# Calculate delanauy triangle
def calculateDelaunayTriangles(rect, points):
    # Create subdiv
    subdiv = cv2.Subdiv2D(rect)

    # Insert points into subdiv
    for p in points:
        subdiv.insert((p[0], p[1]))


    # List of triangles. Each triangle is a list of 3 points ( 6 numbers )
    triangleList = subdiv.getTriangleList()

    # Find the indices of triangles in the points array

    delaunayTri = []

    for t in triangleList:
        pt = []
        pt.append((t[0], t[1]))
        pt.append((t[2], t[3]))
        pt.append((t[4], t[5]))

        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        if rectContains(rect, pt1) and rectContains(rect, pt2) and rectContains(rect, pt3):
            ind = []
            for j in xrange(0, 3):
                for k in xrange(0, len(points)):
                    if(abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                        ind.append(k)
            if len(ind) == 3:
                delaunayTri.append((ind[0], ind[1], ind[2]))



    return delaunayTri


def constrainPoint(p, w, h) :
    p =  ( min( max( p[0], 0 ) , w - 1 ) , min( max( p[1], 0 ) , h - 1 ) )
    return p

# Apply affine transform calculated using srcTri and dstTri to src and
# output an image of size.
def applyAffineTransform(src, srcTri, dstTri, size) :

    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform( np.float32(srcTri), np.float32(dstTri) )

    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine( src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

    return dst


# Warps and alpha blends triangular regions from img1 and img2 to img
def warpTriangle(img1, img2, t1, t2) :

    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))

    # Offset points by left top corner of the respective rectangles
    t1Rect = []
    t2Rect = []
    t2RectInt = []

    for i in xrange(0, 3):
        t1Rect.append(((t1[i][0] - r1[0]),(t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))
        t2RectInt.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))


    # Get mask by filling triangle
    mask = np.zeros((r2[3], r2[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(t2RectInt), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]

    size = (r2[2], r2[3])

    img2Rect = applyAffineTransform(img1Rect, t1Rect, t2Rect, size)

    img2Rect = img2Rect * mask

    # Copy triangular region of the rectangular patch to the output image
    img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * ( (1.0, 1.0, 1.0) - mask )

    img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] + img2Rect



if __name__ == '__main__' :


    # Dimensions of output image
    w = 600
    h = 600

    # 0丑 1一般 2漂亮
    fileList = FemaleFace.get_file_by_label(2) 
    fileList = [u'../data/{}'.format(x) for x in fileList]
    # Read all images
    images, allPoints = readImages(fileList)

    # Eye corners
    eyecornerDst = [ (np.int(0.35 * w ), np.int(h / 2)), (np.int(0.65 * w ), np.int(h / 2)) ]

    imagesNorm = []
    pointsNorm = []

    # Add boundary points for delaunay triangulation
    boundaryPts = np.array([(0,0), (w/2,0), (w-1,0), (w-1,h/2), ( w-1, h-1 ), ( w/2, h-1 ), (0, h-1), (0,h/2) ])

    # Initialize location of average points to 0s
    pointsAvg = np.array([(0,0)]* ( len(allPoints[0]) + len(boundaryPts) ), np.float32())

    n = len(allPoints[0])

    numImages = len(images)

    # Warp images and trasnform landmarks to output coordinate system,
    # and find average of transformed landmarks.

    for i in xrange(0, numImages):

        points1 = allPoints[i]

        # Corners of the eye in input image
        eyecornerSrc  = [ allPoints[i][60], allPoints[i][39] ]

        # Compute similarity transform
        tform = similarityTransform(eyecornerSrc, eyecornerDst)

        # Apply similarity transformation
        img = cv2.warpAffine(images[i], tform, (w,h))

        # Apply similarity transform on points
        points2 = np.reshape(np.array(points1), (keyPointsNumber,1,2))

        points = cv2.transform(points2, tform)

        points = np.float32(np.reshape(points, (keyPointsNumber, 2)))

        # Append boundary points. Will be used in Delaunay Triangulation
        points = np.append(points, boundaryPts, axis=0)

        # Calculate location of average landmark points.
        pointsAvg = pointsAvg + points / numImages

        pointsNorm.append(points)
        imagesNorm.append(img)



    # Delaunay triangulation
    rect = (0, 0, w, h)
    dt = calculateDelaunayTriangles(rect, np.array(pointsAvg))

    # Output image
    output = np.zeros((h,w,3), np.float32())

    # Warp input images to average image landmarks
    for i in xrange(0, len(imagesNorm)) :
        img = np.zeros((h,w,3), np.float32())
        # Transform triangles one by one
        for j in xrange(0, len(dt)) :
            tin = []
            tout = []

            for k in xrange(0, 3) :
                pIn = pointsNorm[i][dt[j][k]]
                pIn = constrainPoint(pIn, w, h)

                pOut = pointsAvg[dt[j][k]]
                pOut = constrainPoint(pOut, w, h)

                tin.append(pIn)
                tout.append(pOut)


            warpTriangle(imagesNorm[i], img, tin, tout)


        # Add image intensities for averaging
        output = output + img


    # Divide by numImages to get average
    output = output / numImages

     # Display result
    cv2.imshow('image', output)

    output = np.int8(output * 127)
    cv2.imwrite('out.jpg', output)



    cv2.waitKey(0)
