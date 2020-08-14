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

from dtnn.utils import ColorPalette
from dtnn import image_processing

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

    def __init__(self, file_img, model, color='B'):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model
        self.color = color

    def predict(self, threshold=20):
        # pre-processing image
        input_arr = image_processing.preprocessing_img(self.img)

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = image_processing.clear_img(resize_prediction, threshold)
        ridge = image_processing.y_ridge(clear_pred)

        # final output
        resize_img = np.array(self.img, np.uint8)
        output_img = image_processing.draw_polyline(resize_img, ridge)

        return output_img


class ViewShieldingRate(object):

    def __init__(self, file_img, model):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model

    def predict(self, threshold=20):
        # pre-processing image
        input_arr = image_processing.preprocessing_img(self.img)

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = image_processing.clear_img(resize_prediction, threshold)
        ridge = image_processing.y_ridge(clear_pred)

        # final output
        resize_img = np.array(self.img, np.uint8)
        output_img = image_processing.draw_polyline(resize_img, ridge, color='BL', thickness=1)
        rate = self.shielding_rate(resize_img, ridge)

        return output_img, rate

    def shielding_rate(self, img, contour):
        x = img.shape[1]
        y = img.shape[0]

        contour_area = cv2.contourArea(contour)
        shield_rate = round((contour_area / (x * y)) * 100, 4)

        return shield_rate

