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

from dtnn import dtnn
from dtsa import spatial_analysis as sa

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['GET', 'POST'])
def predict():

    if request.method == 'POST':
        # input image
        img = request.files['image']

        # parameter
        data = request.form

        response = dtnn.check_command(img, data)

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
            response = sa.check_command(data)

        else:
            error = 'Error : Request MIME type can only be application/json'
            response = jsonify({'Error': error})

    else:
        error = 'Error : Request method can only be POST'
        response = jsonify({'Error': error})

    return response


if __name__ == "__main__":
    dtnn.load_models()
    app.run(host='0.0.0.0')
