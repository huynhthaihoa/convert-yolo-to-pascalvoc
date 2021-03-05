#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert annotation files from YOLO format (.txt) to Pascal VOC format (.xml)
Created on March 3rd 2021

@author: Thai-Hoa Huynh
@credit: original Github repository (https://github.com/carolinepacheco/Convert-YOLO-to-PascalVOC)
"""

import os
from glob import glob
import cv2
from lxml.etree import Element, SubElement, tostring
import numpy as np
import argparse

def unconvert(class_id, width, height, x, y, w, h):
    '''
    Convert the normalized positions into integer positions:
    @class_id [in]:
    @width [in]:
    @height [in]:
    @x [in]:
    @y [in]:
    @class_id [out]:
    @xmin [out]:
    @xmax [out]:
    @ymin [out]:
    @ymax [out]:
    '''
    xmax = int((x*width) + (w * width)/2.0)
    xmin = int((x*width) - (w * width)/2.0)
    ymax = int((y*height) + (h * height)/2.0)
    ymin = int((y*height) - (h * height)/2.0)
    class_id = int(class_id)
    return (class_id, xmin, xmax, ymin, ymax)

## converts coco into xml 
def xml_transform(classes, inputImg, inputAnn, outputImg, outputAnn):  
    '''
    Convert YOLO (.txt) into Pascal VOC (.xml):
    @classes [in]:
    @inputImg [in]:
    @inputAnn [in]:
    @outputImg [in]:
    @outputAnn [in]:
    ''' 
    imgs = []
    exts = ['/*.jpg', '/*.png', '/*.jpeg', '/*.jfif']
    for ext in exts:
        imgs += glob(inputImg + ext)
    ids = [os.path.basename(x) for x in imgs]
    for i, imgpath in enumerate(imgs):
        img= cv2.imread(imgpath)
        target = inputAnn + '/' + ids[i].split('.')[0] + '.txt'
        outImgPath = outputImg + '/' + str(i) + '.' + ids[i].split('.')[1]
        print(target)
        outAnnPath = outputAnn + '/' + str(i) + '.xml'
        cv2.imwrite(outImgPath, img)
        height, width, channels = img.shape

        node_root = Element('annotation')
        node_folder = SubElement(node_root, 'folder')
        node_folder.text = 'VOC2007'

        node_filename = SubElement(node_root, 'filename')
        node_filename.text = outImgPath
        
        node_size = SubElement(node_root, 'size')
        
        node_width = SubElement(node_size, 'width')
        node_width.text = str(width)
    
        node_height = SubElement(node_size, 'height')
        node_height.text = str(height)

        node_depth = SubElement(node_size, 'depth')
        node_depth.text = str(channels)

        node_segmented = SubElement(node_root, 'segmented')
        node_segmented.text = '0'

        label_norm = np.loadtxt(target).reshape(-1, 5)

        for j in range(len(label_norm)):
            labels_conv = label_norm[j]
            print(labels_conv)
            
            new_label = unconvert(labels_conv[0], width, height, labels_conv[1], labels_conv[2], labels_conv[3], labels_conv[4])
            
            node_object = SubElement(node_root, 'object')
            
            node_name = SubElement(node_object, 'name')
            node_name.text = classes[new_label[0]]
                
            node_pose = SubElement(node_object, 'pose')
            node_pose.text = 'Unspecified'
                
                
            node_truncated = SubElement(node_object, 'truncated')
            node_truncated.text = '0'
            
            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = '0'
            
            node_bndbox = SubElement(node_object, 'bndbox')
            
            node_xmin = SubElement(node_bndbox, 'xmin')
            node_xmin.text = str(new_label[1])
            
            node_ymin = SubElement(node_bndbox, 'ymin')
            node_ymin.text = str(new_label[3])
            
            node_xmax = SubElement(node_bndbox, 'xmax')
            node_xmax.text =  str(new_label[2])
            
            node_ymax = SubElement(node_bndbox, 'ymax')
            node_ymax.text = str(new_label[4])
            
            xml = tostring(node_root, pretty_print=True)  
 
        f =  open(outAnnPath, "wb")
        f.write(xml)
        f.close()  
       
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ii", "--input_img", help="Directory of input images",
                    type=str, default="coco/images")
    parser.add_argument("-ia", "--input_ann", help="Directory of input YOLO annotation files (.txt)",
                    type=str, default="coco/yolo")
    parser.add_argument("-oi", "--output_img", help="Directory of output images",
                    type=str, default="coco/images_2")
    parser.add_argument("-oa", "--output_ann", help="Directory of output Pascal VOC annotation files (.xml)",
                    type=str, default="coco/voc")
    parser.add_argument("-c", "--class_file", help="Directory of class file",
                    type=str, default="obj.names")
    args = parser.parse_args()
    inputImgs = args.input_img
    inputAnns = args.input_ann
    outputImgs = args.output_img
    if os.path.isdir(outputImgs) is False:
        os.mkdir(outputImgs)
    outputAnns = args.output_ann
    if os.path.isdir(outputAnns) is False:
        os.mkdir(outputAnns)
    classes = open(args.class_file, "rt")
    YOLO_CLASSES = tuple()
    for line in classes:
        YOLO_CLASSES = YOLO_CLASSES + (line[:-1], )
    xml_transform(YOLO_CLASSES, inputImgs, inputAnns, outputImgs, outputAnns)
    print('Converting YOLO to Pascal VOC finished!')