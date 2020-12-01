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
from dtai import shadow_detection
from dtai.dtnn import Models
from dtsa import spatial_analysis as sa

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

physical_devices = tf.config.list_physical_devices('GPU')
try:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
except:
    print('Invalid device or cannot modify virtual devices once initialized.')

dtai_model = Models()
dtai_model.load()


@app.route('/')
def security():
    return "<h1>Thanks for giving me your IP and address! I'll find you soon<h1>"


# To change 'ai' later (reviewing, because 'find_difference' command is not 'ai')
@app.route('/landscape', methods=['GET', 'POST'])
def landscape():

    if request.method == 'POST':
        # input image

        imgs = request.files
        # parameter
        data = request.form
        # response = process.api(img, data)
        dtai = process.Config(imgs, data)
        # print('Request images :', imgs)
        # print('Request data :', data)
        response = dtai.api()

    else:
        error = 'Error : Request method is only POST'
        response = jsonify({'Error': error})

    return response


# @app.route('/sunlight', methods=['GET', 'POST'])
# def sunlight():
#     if request.method == 'POST':
#
#         # input image
#         imgs = request.files
#
#         # parameter
#         data = request.form
#         dtai = shadow_detection.Config(imgs, data)
#         response = dtai.api()
#
#     else:
#         error = 'Error : Request method is only POST'
#         response = jsonify({'Error': error})
#
#     return response


@app.route('/spatial-analysis', methods=['GET', 'POST'])
def spatial_analysis():
    if request.method == 'POST':
        content_type = request.mimetype
        if content_type == 'application/json':

            data = request.json
            dtsa = sa.ResponseConfig(data)
            response = dtsa.api()

        else:
            error = 'Error : Request MIME type can only be application/json'
            response = jsonify({'Error': error})

    else:
        error = 'Error : Request method can only be POST'
        response = jsonify({'Error': error})

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0')
