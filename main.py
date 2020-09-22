#!/usr/bin/env python
# coding: utf-8

import warnings
import os
import sys

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

import tensorflow as tf

from dtai import process
from dtai.dtnn import Models
from dtsa import spatial_analysis as sa

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)


@app.route('/')
def security():
    return '<h1>Who are you?<h1>'


@app.route('/predict', methods=['GET', 'POST'])
def predict():

    if request.method == 'POST':
        # input image

        img = request.files['image']

        # parameter
        data = request.form
        # response = process.api(img, data)
        dtai = process.Config(img, data)
        response = dtai.api()

    else:
        error = 'Error : Request method is only POST'
        response = jsonify({'Error': error})

    return response


@app.route('/landscape', methods=['GET', 'POST'])
def landscape():

    if request.method == 'POST':
        # input image
        imgs = request.files
        # parameter
        data = request.form
        # response = process.api(img, data)
        dtai = process.Config(imgs, data)
        response = dtai.api()

    else:
        error = 'Error : Request method is only POST'
        response = jsonify({'Error': error})

    return response


@app.route('/spatial-analysis', methods=['GET', 'POST'])
def spatial_analysis():
    if request.method == 'POST':
        content_type = request.mimetype
        if content_type == 'application/json':

            data = request.json
            response = sa.api(data)

        else:
            error = 'Error : Request MIME type can only be application/json'
            response = jsonify({'Error': error})

    else:
        error = 'Error : Request method can only be POST'
        response = jsonify({'Error': error})

    return response


if __name__ == "__main__":
    physical_devices = tf.config.list_physical_devices('GPU')
    try:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    except:
        print('Invalid device or cannot modify virtual devices once initialized.')

    dtai_model = Models()
    dtai_model.load()
    app.run(host='0.0.0.0')
