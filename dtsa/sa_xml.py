# coding: utf-8
import requests

import base64
from io import BytesIO
from PIL import Image
import numpy as np

from xml.etree.ElementTree import Element, SubElement, ElementTree, dump, fromstring, tostring

from dtsa import config

# debugging
def indent(elem, level=0):
    i = "\n" + level*" "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + " "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

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

# def xml_create(command, fileName, coord):
#     execute = element_execute()
#
#     identifier(execute, 'statistics:LinearLineOfSight')
#     # xml_elements(execute, 'ows:Identifier', text='statistics:LinearLineOfSight')
#     data_inputs = xml_elements(execute, 'wps:DataInputs')
#
#     bounding_boxes = [122.99986111111112, 32.999861111111116, 132.0001388888889, 44.00013888888889]
#     raster_input(data_inputs, 'lhdt:srtm_korea_dem', 'http://www.opengis.net/gml/srs/epsg.xml#4326', bounding_boxes)
#
#     ob_complex_dict = {'mimeType': 'application/wkt'}
#     ob_point_dict = {'child': 'wps:ComplexData', 'attribute': ob_complex_dict, 'text': 'POINT(126.99986111111112 38.999861111111116)'}
#     element_input(data_inputs, 'observerPoint', ob_point_dict)
#
#     ob_offset_dict = {'child': 'wps:LiteralData', 'text': '1.8'}
#     element_input(data_inputs, 'observerOffset', ob_offset_dict)
#
#     tg_complex_dict = {'mimeType': 'application/wkt'}
#     tg_point_dict = {'child': 'wps:ComplexData', 'attribute': tg_complex_dict, 'text': 'POINT(126.0001388888889 38.00013888888889)'}
#     element_input(data_inputs, 'targetPoint', tg_point_dict)
#
#     rdo_dict = {'mimeType': 'text/xml; subtype=wfs-collection/1.0'}
#     element_response_form(execute, rdo_dict)
#
#     # indent(execute)
#     # dump(execute)
#
#     return '<?xml version="1.0" encoding="UTF-8"?>' + tostring(execute, encoding='utf-8').decode('utf-8')

def element_execute():
    version = ['1.0.0', '1.1.1']
    service = ['WPS', 'WCS', 'WFS']

    xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
    xmlns = "http://www.opengis.net/wps/1.0.0"
    xmlns_wfs = "http://www.opengis.net/wfs"
    xmlns_wps = "http://www.opengis.net/wps/1.0.0"
    xmlns_ows = "http://www.opengis.net/ows/1.1"
    xmlns_gml = "http://www.opengis.net/gml"
    xmlns_ogc = "http://www.opengis.net/ogc"
    xmlns_wcs = "http://www.opengis.net/wcs/1.1.1"
    xmlns_xlink = "http://www.w3.org/1999/xlink"
    xsi_schemaLocation = "http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd"

    execute = Element('wps:Execute')
    execute.attrib['version'] = version[0]
    execute.attrib['service'] = service[0]
    execute.attrib['xmlns:xsi'] = xmlns_xsi
    execute.attrib['xmlns'] = xmlns
    execute.attrib['xmlns:wfs'] = xmlns_wfs
    execute.attrib['xmlns:wps'] = xmlns_wps
    execute.attrib['xmlns:ows'] = xmlns_ows
    execute.attrib['xmlns:gml'] = xmlns_gml
    execute.attrib['xmlns:ogc'] = xmlns_ogc
    execute.attrib['xmlns:wcs'] = xmlns_wcs
    execute.attrib['xmlns:xlink'] = xmlns_xlink
    execute.attrib['xsi:schemaLocation'] = xsi_schemaLocation

    return execute


def raster_input(data_inputs, file_name, crs, bounding_boxes):
    #data_inputs은 고정값일 수 있음
    e_input = xml_elements(data_inputs, 'wps:Input')
    identifier(e_input, 'inputCoverage')
    ref_dict = {'mimeType': 'image/tiff', 'xlink:href': 'http://geoserver/wcs', 'method': 'POST'}
    reference = xml_elements(e_input, 'wps:Reference', attribute=ref_dict)
    body = xml_elements(reference, 'wps:Body')
    cover_dict = {'service': 'WCS', 'version': '1.1.1'}
    get_coverage = xml_elements(body, 'wcs:GetCoverage', attribute=cover_dict)
    identifier(get_coverage, file_name)
    # xml_elements(get_coverage, 'ows:Identifier', text='fileName')

    if (not crs) and (not bounding_boxes):
        pass
    else:
        domain_subset = xml_elements(get_coverage, 'wcs:DomainSubset')
        bounding_dict = {'crs': 'http://www.opengis.net/gml/srs/epsg.xml#{}'.format(str(crs))}
        bounding_box = xml_elements(domain_subset, 'ows:BoundingBox', attribute=bounding_dict)
        xml_elements(bounding_box, 'ows:LowerCorner', text='{} {}'.format(bounding_boxes[0], bounding_boxes[1]))
        xml_elements(bounding_box, 'ows:UpperCorner', text='{} {}'.format(bounding_boxes[2], bounding_boxes[3]))

    output_dict = {'format': 'image/tiff'}
    xml_elements(get_coverage, 'wcs:Output', attribute=output_dict)


def identifier(parent, text):
    xml_elements(parent, 'ows:Identifier', text=text)

def element_input(data_inputs, option, e_dict):
    #data_inputs은 고정값일 수 있음
    #e_dict = {'child' : 'wps:??', 'attribute' : dict or str, 'text' : 'value'}
    e_input = xml_elements(data_inputs, 'wps:Input')
    identifier(e_input, option)
    data = xml_elements(e_input, 'wps:Data')
    xml_elements(data, **e_dict)

def element_response_form(execute, rdo_dict):
    #execute는 고정값일 수 있음
    response_form = xml_elements(execute, 'wps:ResponseForm')
    # rdo_dict = {'mimeType': 'text/xml; subtype=wfs-collection/1.0'}
    raw_data_output = xml_elements(response_form, 'wps:RawDataOutput', rdo_dict)
    identifier(raw_data_output, 'result')

def xml_elements(parent, child, attribute=None, text=None):
    c = Element(child)

    if attribute:
        for k, v in attribute.items():
            c.attrib[k] = v
    parent.append(c)

    if text:
        c.text = text

    return c


class SARequest(object):

    @staticmethod
    def sa_request(created_xml):
        url = config.GEOSERVER_WPS_URL
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        geo_response = requests.post(url, data=created_xml, headers=headers)
        return geo_response

    @staticmethod
    def wcs_describe_request(coverage):
        # http://127.0.0.1:18080/geoserver/wcs?service=WCS&VERSION=1.1.1&request=DescribeCoverage&identifiers=lhdt:srtm_korea_dem
        url = config.GEOSERVER_WCS_URL
        service = 'wcs'
        version = '1.1.1'
        request_name = 'DescribeCoverage'
        raster_name = coverage
        params = {'service': service,
                  'version': version,
                  'request': request_name,
                  'identifiers': raster_name}
        # get_url = url + '?service=wcs&version=1.1.1&request=DescribeCoverage&identifiers=' + raster_name
        describe_response = requests.get(url, params=params)

        return describe_response

    @staticmethod
    def wfs_describe_request(coverage):
        # http://127.0.0.1:18080/geoserver/wcs?service=WCS&VERSION=1.1.1&request=DescribeCoverage&identifiers=lhdt:srtm_korea_dem
        url = config.GEOSERVER_WCS_URL
        raster_name = coverage
        get_url = url + '?service=wcs&version=1.1.1&request=DescribeCoverage&identifiers=' + raster_name
        describe_response = requests.get(get_url)

        return describe_response

    # 곧 지워질 거임
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


class SAParsing(object):
    @staticmethod
    def wcs_describe_parsing(geo_response):
        # bounding box와 좌표 추출
        note = fromstring(geo_response)

        ns = {'wcs': 'http://www.opengis.net/wcs/1.1.1',
              'ows': 'http://www.opengis.net/ows/1.1'}

        bounding_element = [c for c in
                            note.findall('wcs:CoverageDescription/wcs:Domain/wcs:SpatialDomain/ows:BoundingBox[2]/*',
                                         ns)]
        coord = note.find('wcs:CoverageDescription/wcs:Domain/wcs:SpatialDomain/ows:BoundingBox[2]', ns).attrib['crs'][
                -4:]

        bounding_box = []
        for b in bounding_element:
            y, x = b.text.split(' ')
            bounding_box.append(x)
            bounding_box.append(y)

        return coord, bounding_box


# class SARequest(object):
#
#     @staticmethod
#     def sa_request(created_xml, parsing_xml):
#         url = 'http://localhost:18080/geoserver/wps'
#         headers = {'Content-Type': 'text/xml;charset=utf-8'}
#         geo_response = requests.post(url, data=created_xml(), headers=headers).text
#         try:
#             geo_response = parsing_xml(geo_response)
#         except Exception as e:
#             print('Except :', e)
#             return geo_response
#
#         return geo_response

    # tiff -> image로 변환할때 사용, 아직 뭐가 문제가 있어서 사용하지 못함(다른걸로 대체하여 삭제될 수도 있음)
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

import xmltodict

if __name__ == '__main__':
    geo_response = SARequest.wcs_describe_request('lhdt:srtm_korea_dem').text
    note = fromstring(geo_response)
    ns = {'wcs': 'http://www.opengis.net/wcs/1.1.1',
          'ows': 'http://www.opengis.net/ows/1.1'}

    bounding_element = [c for c in note.findall('wcs:CoverageDescription/wcs:Domain/wcs:SpatialDomain/ows:BoundingBox[2]/*', ns)]
    coord = note.find('wcs:CoverageDescription/wcs:Domain/wcs:SpatialDomain/ows:BoundingBox[2]', ns).attrib['crs'][-4:]

    bounding_box = []
    for b in bounding_element:
        y, x = b.text.split(' ')
        bounding_box.append(x)
        bounding_box.append(y)
        print(bounding_box)
