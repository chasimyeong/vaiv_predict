import numpy as np
import cv2

from dtnn.utils import ColorPalette


def preprocessing_img(img):
    one_ch_img = img.convert('L')
    input_arr = np.array(one_ch_img.resize((256, 256))) / 255
    input_arr = input_arr.reshape((1,) + input_arr.shape)

    return input_arr


def clear_img(img_arr, threshold):
    clear = np.where(img_arr < threshold, 0, img_arr)
    clear = np.where(clear > 0, 255, clear)

    return clear


def y_ridge(img_arr):
    cols = img_arr.shape[1]
    rows = img_arr.shape[0]

    ridge = []

    for c in range(cols):
        for r in range(rows):
            row = img_arr[r][c]
            if row > 0:
                ridge.append([c, r])
                break

    ridge_array = np.array(ridge)

    return ridge_array


def draw_polyline(img, ridge, color='W', thickness=5):
    cp = ColorPalette(color)

    ridge = ridge.astype(np.int32)

    polyline_img = cv2.polylines(img, [ridge], False, cp.color_mapping(), thickness, lineType=cv2.LINE_AA)

    return polyline_img