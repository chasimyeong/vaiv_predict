from common.path import *


def process_folder(pro):
    os.makedirs(pro)
    os.makedirs(path_images_input_output(pro)[0])
    os.makedirs(path_images_input_output(pro)[1])


def check_images_folder():
    if not os.path.isdir(IMAGES_PATH):
        os.makedirs(IMAGES_PATH)
        process_folder(SKYLINE_IMAGES_PATH)
        process_folder(SHIELDING_IMAGES_PATH)
        process_folder(SHADOW_IMAGES_PATH)
    else:
        if not os.path.isdir(SKYLINE_IMAGES_PATH):
            process_folder(SKYLINE_IMAGES_PATH)
        if not os.path.isdir(SHIELDING_IMAGES_PATH):
            process_folder(SHIELDING_IMAGES_PATH)
        if not os.path.isdir(SHADOW_IMAGES_PATH):
            process_folder(SHADOW_IMAGES_PATH)
