#!/usr/bin/env python
# coding: utf-8

import os

from keras.models import load_model
import keras.backend as K


class Models(object):

    # Model index
    SKYLINE_MODEL = 0
    VIEW_SHIELDING_MODEL = 1

    # Models
    models = []

    def __init__(self):
        self.ROOT_DIR = os.path.abspath('')
        self.models_path = os.path.join(self.ROOT_DIR, 'models')

    def load_models(self):

        # models_path
        skyline_model_path = os.path.join(self.models_path, 'skyline_model.hdf5')
        view_shielding_model_path = os.path.join(self.models_path, 'view_shielding_model.hdf5')

        # models load
        skyline_model = self.__keras_model(skyline_model_path)
        view_shielding_model = self.__keras_model(view_shielding_model_path)

        Models.models = [skyline_model, view_shielding_model]

    @staticmethod
    def __keras_model(model_file):

        K.set_image_data_format('channels_last')
        K.set_floatx('float64')
        model = load_model(model_file)

        return model
