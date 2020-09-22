#!/usr/bin/env python
# coding: utf-8

import os

from keras.models import load_model
import keras.backend as K

from keras.models import model_from_json

# Model index
SKYLINE_MODEL = 0
VIEW_SHIELDING_MODEL = 1


class Models(object):

    # Models
    models = []

    def __init__(self):
        self.ROOT_DIR = os.path.abspath('')
        self.models_path = os.path.join(self.ROOT_DIR, 'models')
        self.weights_path = os.path.join(self.models_path, 'weights')

    def load(self):
        # models_path
        skyline_model_path = os.path.join(self.models_path, 'unet_sl_1024_1_model.json')
        view_shielding_model_path = os.path.join(self.models_path, 'unet_vs_1024_1_model.json')

        # models load
        skyline_model = self.__keras_model(skyline_model_path)
        view_shielding_model = self.__keras_model(view_shielding_model_path)

        # weights_path
        skyline_weight_path = os.path.join(self.weights_path, 'unet_sl_1024_1_weight_white_building.hdf5')
        view_shielding_weight_path = os.path.join(self.weights_path, 'unet_vs_1024_1_weight.hdf5')

        # weights load
        skyline_model.load_weights(skyline_weight_path)
        view_shielding_model.load_weights(view_shielding_weight_path)
        Models.models = [skyline_model, view_shielding_model]

    # def load_models(self):
    #     json_file = open("model.json", "r")
    #     loaded_model_json = json_file.read()
    #     json_file.close()
    #     loaded_model = model_from_json(loaded_model_json)

    @staticmethod
    def __keras_model(model_file):

        K.set_image_data_format('channels_last')
        K.set_floatx('float64')

        json_file = open(model_file, "r")
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)

        return model

    # @staticmethod
    # def __keras_model(model_file):
    #
    #     K.set_image_data_format('channels_last')
    #     K.set_floatx('float64')
    #     model = load_model(model_file)
    #
    #     return model
