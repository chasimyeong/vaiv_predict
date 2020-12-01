# coding: utf-8

import base64
from io import BytesIO
from PIL import Image

import numpy as np


class OutputFormat(object):
    def __init__(self, output_img, img_format):
        if isinstance(output_img, list):
            self.output_img = output_img
        elif isinstance(output_img, np.ndarray):
            self.output_img = [output_img]

        self.img_format = img_format

    def trans_format(self):
        trans_output = []
        if self.img_format == 'array':

            for i in self.output_img:
                trans_output.append(self.array2list(i))

        elif self.img_format == 'base64':

            for i in self.output_img:
                trans_output.append(self.array2base64(i))

        else:
            trans_output = "The 'format' parameters that we support are 'array', 'base64'"

        if len(trans_output) == 1:
            trans_output = trans_output[0]

        return trans_output

    def array2list(self, before_img):
        output_img = before_img.tolist()
        return output_img

    def array2base64(self, before_img):
        raw_bytes = BytesIO()
        img_buffer = Image.fromarray(before_img.astype('uint8'))
        img_buffer.save(raw_bytes, 'PNG')
        raw_bytes.seek(0)
        base64_img = base64.b64encode(raw_bytes.read())
        output_img = base64_img.decode('utf-8')
        return output_img


class ColorPalette(object):

    def __init__(self, color):
        self.color = color

    def color_mapping(self):
        if self.color == 'R':
            return self.red()
        elif self.color == 'Y':
            return self.yellow()
        elif self.color == 'G':
            return self.green()
        elif self.color == 'B':
            return self.blue()
        elif self.color == 'BL':
            return self.black()
        elif self.color == 'W':
            return self.white()

    @staticmethod
    def red():
        return 255, 51, 51

    @staticmethod
    def yellow():
        return 255, 255, 51

    @staticmethod
    def green():
        return 51, 255, 51

    @staticmethod
    def blue():
        return 51, 51, 255

    @staticmethod
    def black():
        return 0, 0, 0

    @staticmethod
    def white():
        return 255, 255, 255