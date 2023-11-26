#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 图片处理，需要PIL库

import os
import re
import shutil
import tempfile
import time
from datetime import datetime
from functools import reduce

import cv2
import pytesseract
from PIL import Image

from click_positioning import CONTINUOUS_SCREENCAP_START_Y, CONTINUOUS_SCREENCAP_END_Y, CONTINUOUS_SCREENCAP_START_X, \
    CONTINUOUS_SCREENCAP_END_X
from util.adb_utils import AdbUtils
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

PATH = lambda p: os.path.abspath(p)


class ImageUtils(object):

    def __init__(self, device_id=""):
        """
        初始化，获取系统临时文件存放目录
        """
        self.utils = AdbUtils(device_id)
        self.tempFile = tempfile.gettempdir()

    def screenShot(self):
        """
        截取设备屏幕
        """
        self.utils.sync_shell("screencap -p /data/local/tmp/temp.png")
        time.sleep(1)
        timestamp = datetime.timestamp(datetime.now())
        image_name = "screen"+str(timestamp)+".png"
        self.utils.sync_adb("pull /data/local/tmp/temp.png %s/%s" % (self.tempFile, image_name))
        time.sleep(1)
        return image_name


    def screenShot_xy(self, x1,y1,x2,y2):
        """
        截取设备屏幕
        """
        self.utils.sync_shell("screencap -s '%s,%s,%s,%s'  -p /data/local/tmp/temp.png" % (x1,y1,x2,y2))
        time.sleep(1)
        timestamp = datetime.timestamp(datetime.now())
        image_name = "screen"+str(timestamp)+".png"
        self.utils.sync_adb("pull /data/local/tmp/temp.png %s/%s" % (self.tempFile, image_name))
        time.sleep(1)
        return image_name

    def writeToFile(self, dirPath, imageName):
        """
        将截屏文件写到本地
        usage: screenShot().writeToFile("d:\\screen", "image.png")
        """
        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)
        shutil.move(PATH("%s/%s" % (self.tempFile, imageName)), PATH("%s/%s" % (dirPath, imageName)))
        self.utils.shell("rm /data/local/tmp/temp.png")

    def loadImage(self, imageName):
        """
        加载本地图片
        usage: lodImage("d:\\screen\\image.png")
        """
        if os.path.isfile(imageName):
            load = Image.open(imageName)
            return load
        else:
            print("image is not exist")

    def subImage(self, box):
        """
        截取指定像素区域的图片
        usage: box = (100, 100, 600, 600)
              screenShot().subImage(box)
        """
        image = Image.open(PATH("%s/temp.png" % self.tempFile))
        newImage = image.crop(box)
        newImage.save(PATH("%s/temp.png" % self.tempFile))

        return self

    # http://testerhome.com/topics/202
    def sameAs(self, loadImage):
        """
        比较两张截图的相似度，完全相似返回True
        usage： load = loadImage("d:\\screen\\image.png")
                screen().subImage(100, 100, 400, 400).sameAs(load)
        """
        import math
        import operator

        image1 = Image.open(PATH("%s/temp.png" % self.tempFile))
        image2 = loadImage

        histogram1 = image1.histogram()
        histogram2 = image2.histogram()

        differ = math.sqrt(reduce(operator.add, list(map(lambda a, b: (a - b) ** 2, \
                                                         histogram1, histogram2))) / len(histogram1))
        if differ == 0:
            return True
        else:
            return False


    def has_words(self, file, start_x=0, end_x=960, start_y=0, end_y=540) -> str:
        # 读取图像
        image = cv2.imread(file)
        cropped = image[start_y:end_y, start_x:end_x]  # 裁剪坐标为[y0:y1, x0:x1]
        cv2.imwrite(file, cropped)
        time.sleep(1)
        texts = pytesseract.image_to_string(cv2.imread(file), lang='chi_sim')
        texts = re.sub(r"\s", "", texts)
        print(texts)
        return texts


    def has_words_paddle(self, file, start_x=0, end_x=960, start_y=0, end_y=540) -> str:
        img = cv2.imread(file)
        cropped = img[start_y:end_y,start_x:end_x] # 裁剪坐标为[y0:y1, x0:x1]
        cv2.imwrite(file, cropped)
        time.sleep(1)
        result = ocr.ocr(file, cls=True)
        print(result)
        if result:
            return result[0][0][1][0]
        else:
            return ""


