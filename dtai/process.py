#!/usr/bin/env python
# coding: utf-8

import numpy as np

import cv2

import ast

import json

from PIL import ImageColor
from PIL import Image

from skimage.measure import compare_ssim

from flask import jsonify

from dtai import image_processing
from dtai import utils

from dtai import dtnn
from dtai.dtnn import Models


# Maintain dictionary types a consistent structure, if you can
class Config(object):

    def __init__(self, images, data):
        self.data = data
        self.images = images.getlist('images')
        self.parameters = json.loads(data.get('parameters'))
        self.command = data.get('command')

        # Delete later
        try:
            self.img_format = data.get('format')
        except Exception as e:
            print(e)
            self.img_format = False

    def api(self):
        result = self.__command_check()

        if 'output_img' in result:

            """
            Change to the code below
            #img_format = self.parameters['format']
            """
            if self.img_format:
                img_format = self.img_format
            elif 'format' in self.parameters:
                img_format = self.parameters['format']
            else:
                img_format = 'base64'

            output_format = utils.OutputFormat(result['output_img'], img_format)
            result['output_img'] = output_format.trans_format()

        return jsonify({'command': self.command, 'result': result})

    def __command_check(self):

        command_list = ["skyline_detection", "view_shielding_rate", "find_difference", "shadow_detection"]

        if self.command == command_list[0]:
            parameter_list = ['threshold', 'color', 'thickness', 'pred_type']
            parameter_dict = self.__get_parameter(parameter_list)
            sld = SkylineDetection(self.images, **parameter_dict)
            output = sld.predict()

        elif self.command == command_list[1]:
            parameter_list = ['threshold', 'color', 'thickness']
            parameter_dict = self.__get_parameter(parameter_list)
            vsr = ViewShieldingRate(self.images, **parameter_dict)
            output = vsr.predict()

        elif self.command == command_list[2]:
            parameter_list = ['color', 'alpha']
            parameter_dict = self.__get_parameter(parameter_list)
            fd = FindDifference(self.images, **parameter_dict)
            output = fd.result()

        elif self.command == command_list[3]:
            parameter_list = ['points', "threshold"]
            parameter_dict = self.__get_parameter(parameter_list)
            sd = ShadowDetection(self.images, **parameter_dict)
            output = sd.predict()

        else:
            output = "The 'command' parameters that we support are {}".format(command_list)

            return jsonify({'command': self.command, 'result': output})

        return output

    def __get_parameter(self, parameter_list):

        parameter_dict = dict()
        for p in parameter_list:
            if p in self.parameters:
                parameter_dict[p] = self.parameters[p]

        return parameter_dict


class SkylineDetection(object):

    def __init__(self, img_file, threshold=20, color=(0, 0, 0), thickness=1, pred_type='seg'):
        self.img = Image.open(img_file[0])
        self.threshold = threshold
        self.color = color
        self.thickness = thickness
        self.pred_type = pred_type
        if pred_type == 'line':
            self.model = Models.models[dtnn.SKYLINE_MODEL]
        else:
            self.model = Models.models[dtnn.SKYLINE_SEG_MODEL]

    def predict(self):
        # pre-processing image
        if self.pred_type == 'line':
            input_arr = image_processing.preprocessing(self.img, 'L')
        else:
            input_arr = image_processing.preprocessing(self.img, 'RGB')

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = image_processing.clear_img(resize_prediction, self.threshold)
        if self.pred_type == 'line':
            ridge = image_processing.y_ridge(clear_pred)
            # final output
            resize_img = (np.array(self.img)[:, :, :3]).astype('uint8')
            output_img = image_processing.draw_polyline(resize_img, ridge, self.color, self.thickness)
        else:
            ridge = self.contour(clear_pred)
            # final output
            resize_img = (np.array(self.img)[:, :, :3]).astype('uint8')
            output_img = self.draw_contours(resize_img, ridge, self.color, self.thickness)

        # # final output
        # resize_img = (np.array(self.img)[:, :, :3]).astype('uint8')
        # output_img = image_processing.draw_polyline(resize_img, ridge, self.color, self.thickness)

        return {'output_img': output_img}

    def contour(self, img_arr):
        contours, _ = cv2.findContours(img_arr.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

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


class ViewShieldingRate(object):

    def __init__(self, img_file, threshold=20, color=(0, 0, 0), thickness=1):
        self.img = Image.open(img_file[0])
        self.threshold = threshold
        self.color = color
        self.thickness = thickness
        self.model = Models.models[dtnn.VIEW_SHIELDING_MODEL]

    def predict(self):
        # pre-processing image
        input_arr = image_processing.preprocessing(self.img, 'RGB')

        # prediction output
        predictions = self.model.predict(input_arr)
        prediction = np.array(predictions[0] * 255, dtype='uint8')
        # prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
        resize_prediction = cv2.resize(prediction, dsize=(self.img.size[0], self.img.size[1]), interpolation=cv2.INTER_CUBIC)

        # after-processing image
        clear_pred = image_processing.clear_img(resize_prediction, self.threshold)
        # cv2.floodFill(clear_pred, None, (0, self.img.size[1] - 1), 255)

        ridge = self.contour(clear_pred)


        # final output
        resize_img = (np.array(self.img)[:, :, :3]).astype('uint8')
        output_img = self.draw_contours(resize_img, ridge, self.color, self.thickness)
        # output_img = image_processing.draw_polyline(resize_img, ridge, color='BL', thickness=1)
        rate = self.shielding_rate(resize_img, ridge)
        return {'output_img': resize_prediction, 'shielding_rate': rate}
        # return {'output_img': output_img, 'shielding_rate': rate}

    def shielding_rate(self, img, contour):
        x = img.shape[1]
        y = img.shape[0]

        contour_area = 0
        for c in contour:
            contour_area += cv2.contourArea(c)
        # contour_area = cv2.contourArea(contour[0])
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
        contours, _ = cv2.findContours(img_arr.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

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


class FindDifference(object):

    def __init__(self, img_file, color='[0, 0, 0]', alpha=0.8):
        # imgs = img_file.getlist('images')
        imgs = img_file
        #추후 png인지 아닌지에 따라 다르게 처리하도록 할 것
        self.before_img = np.array(Image.open(imgs[0]).convert('RGB'))
        self.after_img = np.array(Image.open(imgs[1]).convert('RGB'))
        self.color = ast.literal_eval(color)
        self.alpha = float(alpha)

    def result(self):
        before, detection = self.__img2rgba()
        final_before = Image.fromarray(before)
        final_detection = Image.fromarray(detection)
        final = np.array(Image.alpha_composite(final_before, final_detection))

        return {'output_img': final}

    def __difference_img(self):
        gray_before = cv2.cvtColor(self.before_img, cv2.COLOR_RGB2GRAY)
        gray_after = cv2.cvtColor(self.after_img, cv2.COLOR_RGB2GRAY)

        # 주석처리된 부분은 픽셀값만 계산하는 것이 아닌 채도? 뭐 등등 계산해서 도출해냄
        # (score, diff) = compare_ssim(gray_before, gray_after, full=True)
        # diff = (255 - (diff * 255)).astype("uint8")
        absdiff = cv2.absdiff(gray_before, gray_after)  # 우선 이걸 사용하도록

        _, thres = cv2.threshold(absdiff, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        return thres

    def __img2rgba(self):
        thres = self.__difference_img()
        before_img_4 = cv2.cvtColor(self.before_img, cv2.COLOR_RGB2RGBA)
        thres_4 = cv2.cvtColor(thres, cv2.COLOR_GRAY2RGBA)

        color_thres_4 = thres_4.copy()
        print(self.color + [int(255 * self.alpha)])
        color_thres_4[thres == 255] = self.color + [int(255 * self.alpha)]
        color_thres_4[thres != 255] = [0, 0, 0, 0]

        return before_img_4, color_thres_4


class ShadowDetection(object):

    def __init__(self, imgs, points, threshold=250):
        self.imgs = [Image.open(i) for i in imgs]
        self.points = [np.array(s) for s in points]
        self.threshold = threshold
        self.model = Models.models[dtnn.SHADOW_DETECTION]

    def predict(self):

        output = {}

        # pre-processing image

        processing_images = []
        images_area = []

        for img, c in zip(self.imgs, self.points):

            height = img.size[1]
            width = img.size[0]

            mask = np.zeros((height, width), dtype=np.uint8)
            pts = [c]
            cv2.fillPoly(mask, pts, 255)
            img = np.array(img)
            img = cv2.bitwise_and(img, img, mask=mask)
            cnt = c
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            # box = np.int0(box)

            def order_points(pts):
                rect = np.zeros((4, 2), dtype='float32')

                s = pts.sum(axis=1)
                rect[0] = pts[np.argmin(s)]
                rect[2] = pts[np.argmax(s)]

                diff = np.diff(pts, axis=1)
                rect[1] = pts[np.argmin(diff)]
                rect[3] = pts[np.argmax(diff)]

                return rect

            rect = order_points(box)
            (topLeft, topRight, bottomRight, bottomLeft) = rect

            def euclidean_distance(a, b):
                return np.sqrt(np.sum((a - b) ** 2))

            width = int(np.round(euclidean_distance(topLeft, topRight), 0))
            height = int(np.round(euclidean_distance(topLeft, bottomLeft), 0))

            dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype='float32')
            M = cv2.getPerspectiveTransform(rect, dst)

            warped = cv2.warpPerspective(img, M, (width, height))
            img_area = cv2.contourArea(c)

            processing_images.append(warped)
            images_area.append(img_area)

        # prediction output
        output_rate = []
        predict_images = []

        for w, a in zip(processing_images, images_area):
            w = Image.fromarray(w)
            input_arr = image_processing.preprocessing(w, 'RGB')
            predictions = self.model.predict(input_arr)
            prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
            resize_prediction = cv2.resize(prediction, dsize=(w.size[0], w.size[1]),
                                       interpolation=cv2.INTER_CUBIC)

            # after-processing image
            clear_pred = image_processing.clear_img(resize_prediction, self.threshold)
            predict_images.append(clear_pred)

            ct = self.contour(clear_pred)
            shadow_rate = 0
            for c in ct:
                shadow_rate += cv2.contourArea(c)
            rate = round((shadow_rate/a) * 100, 4)
            output_rate.append(rate)

        output['output_img'] = predict_images
        output['output_rate'] = output_rate

        return output

    def contour(self, img_arr):
        contours, _ = cv2.findContours(img_arr.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

        return contours
