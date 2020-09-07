#!/usr/bin/env python
# coding: utf-8
# v0.2

import os
import numpy as np

import cv2

from keras.models import model_from_json
from keras.optimizers import Adam
import keras.backend as K

from PIL import Image

from flask import jsonify

from dtnn import image_processing
from dtnn import utils


def load_models():
    global models

    # Setting initial models and weights path
    # fold path
    ROOT_DIR = os.path.abspath('')
    models_path = os.path.join(ROOT_DIR, 'models')
    weights_path = os.path.join(models_path, 'weights')

    # models
    # The number after the model name refers to the channel
    unet_sl_model_file = os.path.join(models_path, 'unet_sl_model.json')
    unet_sr_model_file = os.path.join(models_path, 'unet_sr_model.json')

    # weights
    unet_weight_skyline_file = os.path.join(weights_path, 'skyline_detection_1.hdf5')
    unet_weight_shielding_file = os.path.join(weights_path, 'view_shielding_rate_1.hdf5')

    # models load
    K.clear_session()
    sky_unet = unet_model(unet_sl_model_file, unet_weight_skyline_file)
    shield_unet = unet_model(unet_sr_model_file, unet_weight_shielding_file)

    models = [sky_unet, shield_unet]

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


def check_command(img, data):

    command = data['command']
    img_format = data['format']

    result = {}

    if command == 'skyline_detection':
        try:
            threshold = int(data['threshold'])
        except:
            threshold = 20
        skyline = SkylineDetection(img, models[0], threshold)
        output_img = skyline.predict()

    elif command == 'view_shielding_rate':
        try:
            threshold = int(data['threshold'])
        except:
            threshold = 20
        shielding = ViewShieldingRate(img, models[1], threshold)
        output_img, shielding_rate = shielding.predict()
        result['shielding_rate'] = shielding_rate

    else:
        command = "The 'command' parameters that we support are 'skyline_detection', " \
                  "'view_shielding_rate'"

        return jsonify({'Error': command})

    output_format = utils.OutputFormat(output_img, img_format)
    final_img = output_format.trans_format()
    result['output_img'] = final_img

    return jsonify({'command': command, 'result': result})


class SkylineDetection(object):

    def __init__(self, file_img, model, threshold):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model
        self.threshold = threshold

    def predict(self):
        # pre-processing image
        input_arr = image_processing.preprocessing(self.img)

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = image_processing.clear_img(resize_prediction, self.threshold)
        ridge = image_processing.y_ridge(clear_pred)

        # final output
        resize_img = np.array(self.img, np.uint8)
        output_img = image_processing.draw_polyline(resize_img, ridge)

        return output_img


class ViewShieldingRate(object):

    def __init__(self, file_img, model, threshold):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model
        self.threshold = threshold

    def predict(self):
        # pre-processing image
        input_arr = image_processing.preprocessing(self.img)

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = image_processing.clear_img(resize_prediction, self.threshold)
        ridge = self.contour(clear_pred)

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

    # ridge와 같은 건데 이부분이 skyline그리는 부분이랑 조금달라서 어떻게 처리할지 고민
    def contour(self, img_arr):
        cols = img_arr.shape[1]
        rows = img_arr.shape[0]

        ridge = []

        for c in range(cols):
            for r in range(rows-1, -1, -1):
                row = img_arr[r][c]
                if row > 0:
                    ridge.append([c, r - 5])
                    break

        #조망차폐율 계산하는 좌표는 따로 구현해야할 듯
        for r in range(rows-1, -1, -1):
            if img_arr[r][0] != 0:
                break
            elif r == 0:
                ridge.insert(0, [-1, -1])

        for r in range(rows-1, -1, -1):
            if img_arr[r][cols-1] != 0:
                break
            elif r == 0:
                ridge.append([cols, -1])

        ridge.append([cols, rows])
        ridge.append([-1, rows])

        ridge_array = np.array(ridge)

        return ridge_array
