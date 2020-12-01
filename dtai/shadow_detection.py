# import numpy as np
#
# import cv2
#
# import ast
#
# import json
#
# from PIL import ImageColor
# from PIL import Image
#
# from skimage.measure import compare_ssim
#
# from flask import jsonify
#
# from dtai import image_processing
# from dtai import utils
#
# from dtai import dtnn
# from dtai.dtnn import Models
#
#
# # Maintain dictionary types a consistent structure, if you can
# class Config(object):
#
#     def __init__(self, imgs, data):
#         self.imgs = imgs.getlist('images')
#         self.parameters = json.loads(data.get('parameters'))
#         self.command = data.get('command')
#         # self.img_format = data.get('format')
#
#     def api(self):
#         result = self.__command_check()
#         # output_format = utils.OutputFormat(result['output_img'], self.img_format)
#         # result['output_img'] = output_format.trans_format()
#
#         return jsonify({'command': self.command, 'result': result})
#
#     def __command_check(self):
#
#         command_list = ["shadow_detection"]
#
#         if self.command == command_list[0]:
#             parameter_list = ['shape_attributes', "threshold"]
#             parameter_dict = self.__get_parameter(parameter_list)
#             sd = ShadowDetection(self.imgs, **parameter_dict)
#             output = sd.predict()
#
#         else:
#             output = "The 'command' parameters that we support are {}".format(command_list)
#
#             return jsonify({'command': self.command, 'result': output})
#
#         return output
#
#     def __get_parameter(self, parameter_list):
#
#         parameter_dict = dict()
#         for p in parameter_list:
#             if p in self.parameters:
#                 parameter_dict[p] = self.parameters[p]
#
#         return parameter_dict
#
#
# class ShadowDetection(object):
#     def __init__(self, imgs, shape_attributes, threshold=250):
#         self.imgs = [Image.open(i) for i in imgs]
#         self.shape_attributes = [np.array(s) for s in shape_attributes]
#         self.threshold = threshold
#         self.model = Models.models[dtnn.SHADOW_DETECTION]
#
#     def predict(self):
#
#         # pre-processing image
#
#         processing_images = []
#         images_area = []
#
#         for img, c in zip(self.imgs, self.shape_attributes):
#
#             height = img.size[1]
#             width = img.size[0]
#
#             mask = np.zeros((height, width), dtype=np.uint8)
#             pts = [c]
#             cv2.fillPoly(mask, pts, 255)
#             img = np.array(img)
#             img = cv2.bitwise_and(img, img, mask=mask)
#             cnt = c
#             rect = cv2.minAreaRect(cnt)
#             box = cv2.boxPoints(rect)
#             # box = np.int0(box)
#
#             def order_points(pts):
#                 rect = np.zeros((4, 2), dtype='float32')
#
#                 s = pts.sum(axis=1)
#                 rect[0] = pts[np.argmin(s)]
#                 rect[2] = pts[np.argmax(s)]
#
#                 diff = np.diff(pts, axis=1)
#                 rect[1] = pts[np.argmin(diff)]
#                 rect[3] = pts[np.argmax(diff)]
#
#                 return rect
#
#             rect = order_points(box)
#             (topLeft, topRight, bottomRight, bottomLeft) = rect
#
#             def euclidean_distance(a, b):
#                 return np.sqrt(np.sum((a - b) ** 2))
#
#             width = int(np.round(euclidean_distance(topLeft, topRight), 0))
#             height = int(np.round(euclidean_distance(topLeft, bottomLeft), 0))
#
#             dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype='float32')
#             M = cv2.getPerspectiveTransform(rect, dst)
#
#             warped = cv2.warpPerspective(img, M, (width, height))
#             img_area = cv2.contourArea(c)
#
#             processing_images.append(warped)
#             images_area.append(img_area)
#
#         # prediction output
#
#         output_rate = []
#
#         for w, a in zip(processing_images, images_area):
#             w = Image.fromarray(w)
#             input_arr = image_processing.preprocessing(w, 'RGB')
#             predictions = self.model.predict(input_arr)
#             prediction = np.array(np.round(predictions[0] * 255, 0), dtype='uint8')
#             resize_prediction = cv2.resize(prediction, dsize=(w.size[0], w.size[1]),
#                                        interpolation=cv2.INTER_CUBIC)
#
#             # after-processing image
#             clear_pred = image_processing.clear_img(resize_prediction, self.threshold)
#
#             ct = self.contour(clear_pred)
#             shadow_rate = 0
#             for c in ct:
#                 shadow_rate += cv2.contourArea(c)
#             rate = round((shadow_rate/a) * 100, 4)
#             output_rate.append(rate)
#
#         return {'output_rate': output_rate}
#
#
#     def contour(self, img_arr):
#         contours, _ = cv2.findContours(img_arr.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
#
#         return contours
