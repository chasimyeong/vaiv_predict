#!/usr/bin/env python
# coding: utf-8

import warnings
import os
import sys
import traceback
import logging

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

from common.setting import check_images_folder
# warnings.filterwarnings('ignore')

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

# check images folder
check_images_folder()


def access_log(rq, date, pg):

    request_info = rq.environ
    access_ip = request_info['REMOTE_ADDR']
    access_method = request_info['REQUEST_METHOD']
    access_content = request_info['REQUEST_URI']
    access_date = date

    query = "INSERT INTO access_log (access_ip, access_method, access_content, access_date) VALUES (%s, %s, %s, %s)"
    values = (access_ip, access_method, access_content, access_date)
    pg.execute(query, values)
    pg.commit()
    pg.close()


@app.route('/')
def security():
    date_today = datetime.now(timezone('Asia/Seoul'))
    pg = postgresql.POSTGRESQL()
    access_log(request, date_today, pg)

    return "<h1>Thanks for giving me your IP and address! I'll find you soon<h1>"


# Delete later
@app.route('/landscape', methods=['GET', 'POST'])
def landscape():
    date_today = datetime.now(timezone('Asia/Seoul'))
    pg = postgresql.POSTGRESQL()
    access_log(request, date_today, pg)

    if request.method == 'POST':

        pg = postgresql.POSTGRESQL()

        try:
            # input image
            images = request.files
            # parameter
            data = request.form

            dtai = process.ResponseConfig(images, data)
            response = dtai.api()

            query = "INSERT INTO request_log (request_state, request_content, request_date) VALUES (%s, %s, %s)"
            values = ("SUCCEEDED", data['command'], date_today)
            pg.execute(query, values)
            pg.commit()
            pg.close()

        except Exception as error:
            logging.error(traceback.print_exc())

            response = jsonify({'Error': str(error)})

            query = "INSERT INTO request_log (request_state, request_content, request_date) VALUES (%s, %s, %s)"
            values = ("FAILED", error, date_today)
            pg.execute(query, values)
            pg.commit()
            pg.close()

    else:
        error = 'Error : Request method is only POST'
        response = jsonify({'Error': error})

    return response


@app.route('/ai-analysis', methods=['GET', 'POST'])
def ai_analysis():

    date_today = datetime.now(timezone('Asia/Seoul'))
    pg = postgresql.POSTGRESQL()
    access_log(request, date_today, pg)

    if request.method == 'POST':

        pg = postgresql.POSTGRESQL()

        try:
            # input image
            images = request.files
            # parameter
            data = request.form

            dtai = process.ResponseConfig(images, data)
            response = dtai.api()

            query = "INSERT INTO request_log (request_state, request_content, request_date) VALUES (%s, %s, %s)"
            values = ("SUCCEEDED", data['command'], date_today)
            pg.execute(query, values)
            pg.commit()
            pg.close()

        except Exception as error:
            logging.error(traceback.print_exc())

            response = jsonify({'Error': str(error)})

            query = "INSERT INTO request_log (request_state, request_content, request_date) VALUES (%s, %s, %s)"
            values = ("FAILED", error, date_today)
            pg.execute(query, values)
            pg.commit()
            pg.close()

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
