#!/usr/bin/env python
# coding: utf-8
# v0.2

import warnings
import os
import numpy as np

import cv2
warnings.filterwarnings('ignore')

from keras.models import model_from_json
from keras.optimizers import Adam
import keras.backend as K

from PIL import Image

class DTNNmodels:
    
    def __init__(self):
        #초기 모델 및 가중치 경로 설정
        self.ROOT_DIR = os.path.abspath('./')
        self.models_path = os.path.join(self.ROOT_DIR, 'models')
        self.weights_path = os.path.join(self.models_path, 'weights')

        self.unet_model_file = os.path.join(self.models_path, 'unet1_model.json')
        
        self.unet_weight_skyline_file = os.path.join(self.weights_path, 'skyline_detection_1channel.hdf5')
        self.unet_weight_shielding_file = os.path.join(self.weights_path, 'view_shielding_rate_1channel.hdf5')
        
    def load_models(self):
        #model load
        K.clear_session()
        self.sky_unet = self.__unet_model(self.unet_model_file, self.unet_weight_skyline_file)
        self.shield_unet = self.__unet_model(self.unet_model_file, self.unet_weight_shielding_file)
        
        return self.sky_unet, self.shield_unet

    def __unet_model(self, model_file, weight_file):
        #unet model
        K.set_image_data_format('channels_last')
        K.set_floatx('float64')

        json_file = open(model_file, "r")
        loaded_model_json = json_file.read() 
        json_file.close()

        unet = model_from_json(loaded_model_json)
        unet.load_weights(weight_file)

        unet.compile(optimizer=Adam(lr=1e-4), loss='binary_crossentropy', metrics = ['mse', 'mae'])    
        return unet
    
    def predict(self, file_img, model, threshold = 20):
        
        input_img, img_arr = self.__preprocessing_img(file_img)
        
        predictions = model.predict(img_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype = 'int')
        
        clear_pred = self.__clear_img(prediction, threshold)
        ridge = self.__y_ridge(clear_pred)
        
        resize_img = np.array(input_img.resize((256,256)), np.uint8)
        output_img = self.__draw_skyline(resize_img, ridge)
        rate = self.__shielding_rate(resize_img, ridge)
        
        return output_img, rate
        
    def __preprocessing_img(self, file_img):
        img = Image.open(file_img)
        one_ch_img = img.convert('L')
        input_arr = np.array(one_ch_img.resize((256, 256)))/255
        input_arr = input_arr.reshape((1, ) + input_arr.shape)
        
        return img, input_arr
        
    def __clear_img(self, img_arr, threshold):
        clear = np.where(img_arr < threshold, 0, img_arr)
        clear = np.where(clear > 0, 255, clear)
    
        return clear

    def __y_ridge(self, img_arr):
        cols = img_arr.shape[1]
        rows = img_arr.shape[0]

        ridge = []

        for c in range(cols):
            for r in range(rows):
                row = img_arr[r][c]
                if row > 0:
                    ridge.append([c, r])
                    break

        ridge.append([cols+1, rows+1])
        ridge.append([0, rows+1])            
        ridge_array = np.array(ridge)

        return ridge_array

    def __draw_skyline(self, img, ridge):

        ridge = ridge.astype(np.int32)

        polyline_img = cv2.polylines(img, [ridge], False, (255, 0, 0))

        return polyline_img
    
    def __shielding_rate(self, img, contour):
        x = img.shape[1]
        y = img.shape[0]

        contour_area = cv2.contourArea(contour)
        shield_rate = round((contour_area/(x*y)) * 100, 4)

        return shield_rate

