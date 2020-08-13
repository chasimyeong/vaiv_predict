#!/usr/bin/env python
# coding: utf-8

import warnings
import os
import sys

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(__file__))

from flask import Flask, request, jsonify

from dtnn import dtnn
from dtnn import utils
warnings.filterwarnings('ignore')

app = Flask(__name__)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # input image
        img = request.files['image']

        # parameter
        data = request.form
        command = data['command']
        img_format = data['format']

        result = {}

        if command == 'skyline_detection':

            skyline = dtnn.SkylineDetection(img, sky_model)
            output_img = skyline.predict(threshold=20)

        elif command == 'view_shielding_rate':

            shielding = dtnn.ViewShieldingRate(img, shield_model)
            output_img, shielding_rate = shielding.predict(threshold=20)
            result['shielding_rate'] = shielding_rate

        else:
            command = "The 'command' parameters that we support are 'skyline_detection', " \
                      "'view_shielding_rate'"

            return jsonify({'Error': command})

        output_format = utils.OutputFormat(output_img, img_format)
        final_img = output_format.trans_format()
        result['output_img'] = final_img

        return jsonify({'command': command, 'result': result})

    else:
        error = 'Error : Request method is only POST'
        return jsonify({'Error': error})

@app.route('/spatial-analysis', methods=['GET', 'POST'])
def spatial_analysis():



    return jsonify({'Error': 'Error'})


if __name__ == "__main__":
    sky_model, shield_model = dtnn.load_models()
    app.run(host='0.0.0.0')
