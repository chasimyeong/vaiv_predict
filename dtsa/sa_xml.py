# coding: utf-8
import requests

import base64
from io import BytesIO
from PIL import Image
import numpy as np


class SARequest(object):

    @staticmethod
    def sa_request(created_xml, parsing_xml):
        url = 'http://localhost:18080/geoserver/wps'
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        geo_response = requests.post(url, data=created_xml(), headers=headers).text
        try:
            geo_response = parsing_xml(geo_response)
        except Exception as e:
            print('Except :', e)
            return geo_response

        return geo_response

    # @staticmethod
    # def sa_request_image(created_xml, parsing_xml):
    #     url = 'http://localhost:18080/geoserver/wps'
    #     headers = {'Content-Type': 'text/xml;charset=utf-8'}
    #     geo_response = requests.post(url, data=created_xml(), headers=headers)
    #     # print(np.unique(np.array(Image.open(BytesIO(geo_response)))))
    #     # def array2base64(test):
    #     #     raw_bytes = BytesIO()
    #     #     img_buffer = Image.fromarray(test.astype('uint8'))
    #     #     img_buffer.save(raw_bytes, 'PNG')
    #     #     raw_bytes.seek(0)
    #     #     base64_img = base64.b64encode(raw_bytes.read())
    #     #     output_img = base64_img.decode('utf-8')
    #     #     return output_img
    #     #
    #     # geo_response = array2base64(geo_response)
    #     geo_response = geo_response.content
    #     try:
    #         geo_response = parsing_xml(geo_response)
    #     except Exception as e:
    #         print('Except :', e)
    #         return geo_response
    #
    #     return geo_response

    @staticmethod
    def common(bool):
        if not bool:
            header = '<?xml version="1.0" encoding="UTF-8"?>' \
                  '<wps:Execute version="1.0.0" service="WPS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                  'xmlns="http://www.opengis.net/wps/1.0.0" xmlns:wfs="http://www.opengis.net/wfs" ' \
                  'xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" ' \
                  'xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" ' \
                  'xmlns:wcs="http://www.opengis.net/wcs/1.1.1" xmlns:xlink="http://www.w3.org/1999/xlink" ' \
                  'xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">'
        else:
            header = '<wps:ResponseForm>' \
                  '<wps:RawDataOutput mimeType="application/vnd.geo+json; subtype=wfs-collection/1.0">' \
                  '<ows:Identifier>result</ows:Identifier>' \
                  '</wps:RawDataOutput>' \
                  '</wps:ResponseForm>' \
                  '</wps:Execute>'

        return header

    # @staticmethod
    # def common(bool):
    #     if not bool:
    #         header = '<?xml version="1.0" encoding="UTF-8"?>' \
    #               '<wps:Execute version="1.0.0" service="WPS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
    #               'xmlns="http://www.opengis.net/wps/1.0.0" xmlns:wfs="http://www.opengis.net/wfs" ' \
    #               'xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" ' \
    #               'xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" ' \
    #               'xmlns:wcs="http://www.opengis.net/wcs/1.1.1" xmlns:xlink="http://www.w3.org/1999/xlink" ' \
    #               'xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">'
    #     else:
    #         header = '<wps:ResponseForm>' \
    #               '<wps:RawDataOutput mimeType="application/vnd.geo+json; subtype=wfs-collection/1.0">' \
    #               '<ows:Identifier>result</ows:Identifier>' \
    #               '</wps:RawDataOutput>' \
    #               '</wps:ResponseForm>' \
    #               '</wps:Execute>'
    #
    #     return header

