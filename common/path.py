import os

# Top level path in module
ROOT_DIR = os.path.abspath('')

# images path
IMAGES_PATH = os.path.join(ROOT_DIR, 'images')

SKYLINE_IMAGES_PATH = os.path.join(IMAGES_PATH, 'skyline')
SHIELDING_IMAGES_PATH = os.path.join(IMAGES_PATH, 'shielding')
SHADOW_IMAGES_PATH = os.path.join(IMAGES_PATH, 'shadow')


def path_images_input_output(top):
    input_path = os.path.join(top, 'input')
    output_path = os.path.join(top, 'output')

    return input_path, output_path


def path_command_check(command=None):
    if command == 'skyline':
        process_path = SKYLINE_IMAGES_PATH
    elif command == 'shielding':
        process_path = SHIELDING_IMAGES_PATH
    elif command == 'shadow':
        process_path = SHADOW_IMAGES_PATH
    else:
        process_path = 'temp'

    input_path = path_images_input_output(process_path)[0]
    output_path = path_images_input_output(process_path)[0]

    return input_path, output_path
