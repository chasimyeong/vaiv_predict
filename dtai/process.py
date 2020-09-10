#!/usr/bin/env python
# coding: utf-8

import numpy as np

import cv2

import ast

from PIL import ImageColor

from PIL import Image

from flask import jsonify

from dtai import image_processing
from dtai import utils

from dtai.dtnn import Models

# class Config(object):
#     def __init__(self, img, data):
#         self.img = img
#         self.command = data['command']
#         self.img_format = data['format']
#
#         if 'threshold' in data:
#             self.threshold = data['threshold']
#
#     def command_check(self):
#
#
#     def response(self):
#


def api(img, data):

    command = data['command']
    img_format = data['format']
    color = data['color']
    thickness = data['thickness']

    try:
        threshold = int(data['threshold'])
    except:
        threshold = 20

    result = {}

    if command == 'skyline_detection':
        skyline = SkylineDetection(img, Models.models[0], threshold, color, thickness)
        output_img = skyline.predict()

    elif command == 'view_shielding_rate':

        shielding = ViewShieldingRate(img, Models.models[1], threshold, color, thickness)
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

    def __init__(self, file_img, model, threshold, color, thickness):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model
        self.threshold = threshold
        self.color = color
        self.thickness = thickness

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
        resize_img = (np.array(self.img)[:, :, :3]).astype('uint8')
        output_img = image_processing.draw_polyline(resize_img, ridge, self.color, self.thickness)

        return output_img


class ViewShieldingRate(object):

    def __init__(self, file_img, model, threshold, color, thickness):
        self.file_img = file_img
        self.img = Image.open(self.file_img)
        self.model = model
        self.threshold = threshold
        self.color = color
        self.thickness = thickness

    def predict(self):
        # pre-processing image
        input_arr = image_processing.preprocessing(self.img)

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(predictions[0] * 255, dtype='uint8')
        # prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = image_processing.clear_img(resize_prediction, self.threshold)
        ridge = self.contour(clear_pred)

        # final output
        resize_img = (np.array(self.img)[:, :, :3]).astype('uint8')
        output_img = self.draw_contours(resize_img, ridge, self.color, self.thickness)
        # output_img = image_processing.draw_polyline(resize_img, ridge, color='BL', thickness=1)
        rate = self.shielding_rate(resize_img, ridge)

        return output_img, rate

    def shielding_rate(self, img, contour):
        x = img.shape[1]
        y = img.shape[0]

        contour_area = cv2.contourArea(contour[0])
        shield_rate = round((contour_area / (x * y)) * 100, 4)

        return shield_rate
    # def shielding_rate(self, img, contour):
    #     x = img.shape[1]
    #     y = img.shape[0]
    #
    #     contour_area = cv2.contourArea(contour)
    #     shield_rate = round((contour_area / (x * y)) * 100, 4)
    #
    #     return shield_rate

    def contour(self, img_arr):
        contours, _ = cv2.findContours(img_arr.astype('uint8'), cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)

        return contours

    def draw_contours(self, img, contour, color=(0, 0, 0), thickness=1):

        # cp = image_processing.ColorPalette(color)

        if isinstance(color, str):
            if len(color) >= 9:
                color = ast.literal_eval(color)
            else:
                if len(color) == 6:
                    color = '#' + color

                color = ImageColor.getcolor(color, 'RGB')

        if isinstance(thickness, str):
            thickness = int(thickness)

        img_copy = img.copy()
        cv2.drawContours(img_copy, contour, -1, color, thickness, lineType=cv2.LINE_AA)

        return img_copy

    # # ridge와 같은 건데 이부분이 skyline그리는 부분이랑 조금달라서 어떻게 처리할지 고민
    # def contour(self, img_arr):
    #     cols = img_arr.shape[1]
    #     rows = img_arr.shape[0]
    #
    #     ridge = []
    #
    #     for c in range(cols):
    #         for r in range(rows-1, -1, -1):
    #             row = img_arr[r][c]
    #             if row > 0:
    #                 ridge.append([c, r - 5])
    #                 break
    #
    #     #조망차폐율 계산하는 좌표는 따로 구현해야할 듯
    #     for r in range(rows-1, -1, -1):
    #         if img_arr[r][0] != 0:
    #             break
    #         elif r == 0:
    #             ridge.insert(0, [-1, -1])
    #
    #     for r in range(rows-1, -1, -1):
    #         if img_arr[r][cols-1] != 0:
    #             break
    #         elif r == 0:
    #             ridge.append([cols, -1])
    #
    #     ridge.append([cols, rows])
    #     ridge.append([-1, rows])
    #
    #     ridge_array = np.array(ridge)
    #
    #     return ridge_array
