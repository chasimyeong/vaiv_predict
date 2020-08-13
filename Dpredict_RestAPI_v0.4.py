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
from flask_cors import CORS

from dtnn import dtnn
from dtnn import utils
from dtnn import spatial_analysis as sa

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
    if request.method == 'POST':

        data = request.form
        command = data['command']
        param = data['parameter']

        if command == "linear_line_of_sight":
            LLOS = sa.LinearLineOfSight(param['fileName'], param['coord'], param['inputCoverage'],
                                            param['observerPoint'], param['observerOffset'], param['targetPoint'])
            response = LLOS.analysis()
        elif command == "calculate_cut_fill":
            CCF = sa.CalculateCutFill
            response = CCF.analysis()

        else:
            response = "The 'command' parameters that we support are 'linear_line_of_sight', " \
                      "'calculate_cut_fill'"
        return jsonify({'command': command, 'result': response})


if __name__ == "__main__":
    sky_model, shield_model = dtnn.load_models()
    app.run(host='0.0.0.0')
