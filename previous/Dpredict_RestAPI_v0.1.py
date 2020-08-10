#!/usr/bin/env python
# coding: utf-8

import warnings
import os

import numpy as np

import cv2
import base64
from PIL import Image
from io import BytesIO

from keras.models import model_from_json
from keras.optimizers import Adam
import keras.backend as K

from flask import Flask, request, jsonify
from PIL import Image

warnings.filterwarnings('ignore')

ROOT_DIR = os.path.abspath('../')
models_path = os.path.join(ROOT_DIR, 'models')
weights_path = os.path.join(models_path, 'weights')

best_model_file = os.path.join(models_path, 'model.json')
best_weight_file = os.path.join(weights_path, 'best_weight.hdf5')

print("base models path :", models_path)

if not os.path.isdir(models_path):
    os.makedirs(models_path)
if not os.path.isdir(weights_path):
    os.makedirs(weights_path)

K.clear_session()
K.set_image_data_format('channels_last')
K.set_floatx('float64')

json_file = open(best_model_file, "r")
loaded_model_json = json_file.read() 
json_file.close()

unet = model_from_json(loaded_model_json)

unet.load_weights(best_weight_file)

unet.compile(optimizer=Adam(lr=1e-4), loss='binary_crossentropy', metrics = ['mse', 'mae'])

app = Flask (__name__)

def img_prediction(file_img):
    img = Image.open(file_img)
    
    input_arr = np.array(img.resize((256, 256)))/255
    input_arr = input_arr.reshape((1, ) + input_arr.shape)
    
    predictions = unet.predict(input_arr)
    predictions = np.array(np.round(predictions[0] * 255, 0), dtype = 'int')
    return img, predictions

def clear_img(img, threshold= 40):
    '''
    img는 array
    '''
    clear = np.where(img < threshold, 0, img)
    clear = np.where(clear > 0, 255, clear)
    
    return clear

def y_ridge(img):
    cols = img.shape[1]
    rows = img.shape[0]

    ridge = []

    for c in range(cols):
        for r in range(rows):
            row = img[r][c]
            if row > 0:
                ridge.append([c, r])
                break

    ridge_array = np.array(ridge)
    
    return ridge_array

def draw_skyline(img, ridge):
    
    ridge = ridge.astype(np.int32)
    
    polyline_img = cv2.polylines(img, [ridge], False, (255, 0, 0))
    
    return polyline_img

@app.route('/skylinePredict', methods = ['POST'])
def predict():
    if request.method == 'POST':
        files = request.files

        img = files['image']
        form = files['format']

        input_img, prediction = img_prediction(img)

        clear_pred = clear_img(prediction)
        ridge = y_ridge(clear_pred)

        resize_img = np.array(input_img.resize((256, 256)), np.uint8)
        output_img = draw_skyline(resize_img, ridge)

        if form == 'total_array':
            output = output_img.tolist()
        elif form == 'total_base64':
            rawBytes = BytesIO()
            img_buffer = Image.fromarray(output_img.astype('uint8'))
            img_buffer.save(rawBytes, 'PNG')
            rawBytes.seek(0)
            base64_img = base64.b64encode(rawBytes.read())
            output = str(base64_img)
        else:
            print('format을 입력해주세요. 현재 지원 format parameter는 total_array, total_base64입니다.')

        #        img_result는 output image를 원래의 사이즈로 다시 키우는 것, 화질이 너무 깨져서 다른 방법 생각해야함
        #        img_result = cv2.resize(output_img, dsize = (input_img.size[0], input_img.size[1]), interpolation=cv2.INTER_CUBIC)

    return jsonify({'output_img': output})

if __name__ == "__main__":
    app.run(host='0.0.0.0')