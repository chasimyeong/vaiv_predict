#!/usr/bin/env python
# coding: utf-8

import warnings
import os
import sys

# Setting for execute .exe
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

import tensorflow as tf

from datetime import datetime
from pytz import timezone

from dtai import process
from dtai.dtnn import Models
from dtsa import spatial_analysis as sa

from db import postgresql

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Setting Gpu Memory
physical_devices = tf.config.list_physical_devices('GPU')
try:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
except:
    print('Invalid device or cannot modify virtual devices once initialized.')

# model load
dtai_model = Models()
dtai_model.load()

# db connection
postgresql.connection_check()

@app.route('/')
def security():
    return "<h1>Thanks for giving me your IP and address! I'll find you soon<h1>"


# Delete later
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


@app.route('/ai-analysis', methods=['GET', 'POST'])
def ai_analysis():

    if request.method == 'POST':

        try:


            # input image
            images = request.files
            # parameter
            data = request.form

            # cur = connection.cursor()
            #
            # date_today = datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
            # print(images)
            # print(data)
            # cur.execute(
            #     """
            #     INSERT INTO input_data (input_images, input_parameters, input_date) VALUES (%s, %s, %s)
            #     """, (images, data, date_today))
            # connection.commit()
            # cur.close()
            dtai = process.Config(images, data)
            response = dtai.api()

        except Exception as error:
            print(error)
            response = jsonify({'Error': error})

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
            dtsa = sa.ResponseConfig(data)
            response = dtsa.api()

        else:
            error = 'Error : Request MIME type can only be application/json'
            response = jsonify({'Error': error})

    else:
        error = 'Error : Request method can only be POST'
        response = jsonify({'Error': error})

    return response


@app.route('/image-analysis', methods=['GET', 'POST'])
def image_analysis():

    if request.method == 'POST':
        # input image

        images = request.files
        # parameter
        data = request.form

        dtai = process.Config(images, data)
        response = dtai.api()

    else:
        error = 'Error : Request method is only POST'
        response = jsonify({'Error': error})

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0')
