import numpy as np
import cv2

from dtnn.utils import ColorPalette

def preprocessing_img(img):
    one_ch_img = img.convert('L')
    input_arr = np.array(one_ch_img.resize((256, 256))) / 255
    input_arr = input_arr.reshape((1,) + input_arr.shape)

    return input_arr

# threshold를 parameter로 제공해보자
def clear_img(img_arr, threshold):

    # _, clear = cv2.threshold(img_arr, threshold, 255, cv2.THRESH_BINARY)
    clear = np.where(img_arr < threshold, 0, img_arr)
    clear = np.where(clear > 0, 255, clear)

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


def draw_polyline(img, ridge, color='B', thickness=5):
    # png 파일 받을 경우 투명색으로 색칠됨
    cp = ColorPalette(color)

    ridge = ridge.astype(np.int32)
    polyline_img = cv2.polylines(img, [ridge], False, cp.color_mapping(), thickness, lineType=cv2.LINE_AA)

    return polyline_img