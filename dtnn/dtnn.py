#!/usr/bin/env python
# coding: utf-8
# v0.2

import warnings
import os
import numpy as np

import cv2

from keras.models import model_from_json
from keras.optimizers import Adam
import keras.backend as K

from PIL import Image
warnings.filterwarnings('ignore')

# Setting initial models and weights path
# fold path
ROOT_DIR = os.path.abspath('')
models_path = os.path.join(ROOT_DIR, 'models')
weights_path = os.path.join(models_path, 'weights')

# models
# The number after the model name refers to the channel
unet1_model_file = os.path.join(models_path, 'unet1_model.json')
unet3_model_file = os.path.join(models_path, 'unet3_model.json')

# weights
unet_weight_skyline_file = os.path.join(weights_path, 'skyline_detection_1.hdf5')
unet_weight_shielding_file = os.path.join(weights_path, 'view_shielding_rate_1.hdf5')


def load_models():
    # models load
    K.clear_session()
    sky_unet = unet_model(unet1_model_file, unet_weight_skyline_file)
    shield_unet = unet_model(unet1_model_file, unet_weight_shielding_file)

    return sky_unet, shield_unet


def unet_model(model_file, weight_file):
    # unet model
    K.set_image_data_format('channels_last')
    K.set_floatx('float64')

    json_file = open(model_file, "r")
    loaded_model_json = json_file.read()
    json_file.close()

    unet = model_from_json(loaded_model_json)
    unet.load_weights(weight_file)

    unet.compile(optimizer=Adam(lr=1e-4), loss='binary_crossentropy', metrics=['mse', 'mae'])
    return unet


class SkylineDetection(object):

    def __init__(self, file_img, model):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model

    def predict(self, threshold=20):
        # pre-processing image
        input_arr = self.preprocessing_img(self.img)

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = self.clear_img(resize_prediction, threshold)
        ridge = self.y_ridge(clear_pred)

        # final output
        resize_img = np.array(self.img, np.uint8)
        output_img = self.draw_skyline(resize_img, ridge)

        return output_img

    def preprocessing_img(self, img):
        one_ch_img = img.convert('L')
        input_arr = np.array(one_ch_img.resize((256, 256))) / 255
        input_arr = input_arr.reshape((1,) + input_arr.shape)

        return input_arr

    def clear_img(self, img_arr, threshold):
        clear = np.where(img_arr < threshold, 0, img_arr)
        clear = np.where(clear > 0, 255, clear)

        return clear

    def y_ridge(self, img_arr):
        cols = img_arr.shape[1]
        rows = img_arr.shape[0]

        ridge = []

        for c in range(cols):
            for r in range(rows):
                row = img_arr[r][c]
                if row > 0:
                    ridge.append([c, r])
                    break

        ridge.append([cols + 1, rows + 1])
        ridge.append([0, rows + 1])
        ridge_array = np.array(ridge)

        return ridge_array

    def draw_skyline(self, img, ridge):

        ridge = ridge.astype(np.int32)

        polyline_img = cv2.polylines(img, [ridge], False, (255, 0, 0))

        return polyline_img


class ViewShieldingRate(object):

    def __init__(self, file_img, model):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model

    def predict(self, threshold=20):
        # pre-processing image
        input_arr = self.preprocessing_img(self.img)

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = self.clear_img(resize_prediction, threshold)
        ridge = self.y_ridge(clear_pred)

        # final output
        resize_img = np.array(self.img, np.uint8)
        output_img = self.draw_skyline(resize_img, ridge)
        rate = self.shielding_rate(resize_img, ridge)

        return output_img, rate

    def preprocessing_img(self, img):
        one_ch_img = img.convert('L')
        input_arr = np.array(one_ch_img.resize((256, 256))) / 255
        input_arr = input_arr.reshape((1,) + input_arr.shape)

        return input_arr

    def clear_img(self, img_arr, threshold):
        clear = np.where(img_arr < threshold, 0, img_arr)
        clear = np.where(clear > 0, 255, clear)

        return clear

    def y_ridge(self, img_arr):
        cols = img_arr.shape[1]
        rows = img_arr.shape[0]

        ridge = []

        for c in range(cols):
            for r in range(rows):
                row = img_arr[r][c]
                if row > 0:
                    ridge.append([c, r])
                    break

        ridge.append([cols + 1, rows + 1])
        ridge.append([0, rows + 1])
        ridge_array = np.array(ridge)

        return ridge_array

    def draw_skyline(self, img, ridge):

        ridge = ridge.astype(np.int32)

        polyline_img = cv2.polylines(img, [ridge], False, (255, 0, 0))

        return polyline_img

    def shielding_rate(self, img, contour):
        x = img.shape[1]
        y = img.shape[0]

        contour_area = cv2.contourArea(contour)
        shield_rate = round((contour_area / (x * y)) * 100, 4)

        return shield_rate

