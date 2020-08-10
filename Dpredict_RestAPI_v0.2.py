#!/usr/bin/env python
# coding: utf-8

import warnings
import os
import base64
from io import BytesIO

from flask import Flask, request, jsonify
from PIL import Image

from dtnn.dtnn_model import DTNNmodels

warnings.filterwarnings('ignore')

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)

@app.route('/Dpredict', methods=['POST'])
def predict():
    if request.method == 'POST':

        data = request.form
        img = request.files['image']
        form = data['format']
        command = data['command']

        if command == 'skyline_detection':

            output_img, _ = DTNN.predict(img, sky_model)

            result = {}

        elif command == 'view_shielding_rate':

            output_img, rate = DTNN.predict(img, shield_model)

            result = {'shielding_rate': rate}

        if form == 'total_array':
            output = output_img.tolist()
            result['output_img'] = output
        elif form == 'total_base64':
            rawBytes = BytesIO()
            img_buffer = Image.fromarray(output_img.astype('uint8'))
            img_buffer.save(rawBytes, 'PNG')
            rawBytes.seek(0)
            base64_img = base64.b64encode(rawBytes.read())
            output = str(base64_img)
            result['output_img'] = output
        else:
            print('format을 입력해주세요. 현재 지원 format parameter는 total_array, total_base64입니다.')

    #        img_result는 output image를 원래의 사이즈로 다시 키우는 것, 화질이 너무 깨져서 다른 방법 생각해야함
    #        img_result = cv2.resize(output_img, dsize = (input_img.size[0], input_img.size[1]), interpolation=cv2.INTER_CUBIC)
    return jsonify({'command': command, 'result': result})

if __name__ == "__main__":
    DTNN = DTNNmodels()
    sky_model, shield_model = DTNN.load_models()
    app.run(host='0.0.0.0')