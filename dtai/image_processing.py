#!/usr/bin/env python
# coding: utf-8

import numpy as np
import cv2

import ast

from PIL import ImageColor

from dtai.utils import ColorPalette


def preprocessing(img, cmap):
    # if cmap == 'gray':
    #     cmap = 'L'
    # elif cmap == 'rgb':
    #     cmap = 'RGB'

    one_ch_img = img.convert(cmap)
    input_arr = np.array(one_ch_img.resize((256, 256))) / 255
    input_arr = input_arr.reshape((1,) + input_arr.shape)

    return input_arr


def clear_img(img_arr, threshold):
    _, clear = cv2.threshold(img_arr, int(threshold), 255, cv2.THRESH_BINARY)
    # clear = np.where(img_arr < threshold, 0, img_arr)
    # clear = np.where(clear > 0, 255, clear)

    return clear


def y_ridge(img_arr):
    cols = img_arr.shape[1]
    rows = img_arr.shape[0]

    ridge = []

    for c in range(cols):
        for r in range(rows-1, -1, -1):
            row = img_arr[r][c]
            if row > 0:
                ridge.append([c, r-5])
                break

    ridge_array = np.array(ridge)

    return ridge_array


def draw_polyline(img, ridge, color=(51, 51, 255), thickness=5):
    # cp = ColorPalette(color)
    if isinstance(color, str):
        if len(color) >= 9:
            color = ast.literal_eval(color)
        else:
            if len(color) == 6:
                color = '#' + color

            color = ImageColor.getcolor(color, 'RGB')

    if isinstance(thickness, str):
        thickness = int(thickness)

    ridge = ridge.astype(np.int32)
    polyline_img = cv2.polylines(img, [ridge], False, color, thickness, lineType=cv2.LINE_AA)

    return polyline_img