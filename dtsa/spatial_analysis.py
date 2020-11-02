# coding: utf-8

from flask import jsonify

import base64
from io import BytesIO

import xmltodict
import json

from dtsa.sa_xml import SARequest, SAParsing
from dtsa.sa_xml import element_execute, identifier, xml_elements, raster_input, element_input, element_response_form
from dtsa import config
from xml.etree.ElementTree import Element, SubElement, ElementTree, dump, fromstring, tostring

from common.utils import get_parameter


# xml같은 경우 띄어쓰기나 이런 사소한 것으로 parsing error가 발생할 수도 있음
# Maintain dictionary types a consistent structure, if you can
class Config(object):

    def __init__(self, data):
        self.command = data['command']
        self.params = data['parameters']

    def api(self):

        result = self.__command()

        return jsonify({'command': self.command, 'result': result})

    def __command(self):

        cl = config.COMMAND_LIST

        # command_list = ["linear_line_of_sight", "raster_cut_fill", "clip_with_geometry",
        #                 "calculate_area", "raster_to_image", "statistics_grid_coverage"]

        if self.command == cl[0]:
            parameter_list = ['fileName', 'coord', 'boundingBox', 'observerPoint', 'observerOffset', 'targetPoint']
            parameter_dict = get_parameter(parameter_list, self.params)
            # LLOS = LinearLineOfSight(param['fileName'], param['coord'], param['boundingBox'],
            #                             param['observerPoint'], param['observerOffset'], param['targetPoint'])
            LLOS = LinearLineOfSight(**parameter_dict)
            output = LLOS.xml_request()

        elif self.command == cl[1]:
            parameter_list = ['fileName', 'coord', 'boundingBox', 'inputGeometry', 'userMeanHeight']
            parameter_dict = get_parameter(parameter_list, self.params)
            # RCF = RasterCutFill(param['fileName'], param['coord'], param['boundingBox'],
            #                           param['inputGeometry'], param['userMeanHeight'])
            RCF = RasterCutFill(**parameter_dict)
            output = RCF.xml_request()

        elif self.command == cl[2]:
            parameter_list = ['fileName', 'clipGeometry']
            parameter_dict = get_parameter(parameter_list, self.params)
            # CWG = ClipWithGeometry(param['fileName'], param['clipGeometry'])
            CWG = ClipWithGeometry(**parameter_dict)
            output = CWG.xml_request()

        elif self.command == cl[3]:
            parameter_list = ['fileName']
            parameter_dict = get_parameter(parameter_list, self.params)
            # CA = CalculateArea(param['fileName'])
            CA = CalculateArea(**parameter_dict)
            output = CA.xml_request()

        elif self.command == cl[4]:
            parameter_list = ['fileName', 'coord', 'boundingBox', 'width', 'height']
            parameter_dict = get_parameter(parameter_list, self.params)
            # RTI = RasterToImage(param['fileName'], param['coord'], param['boundingBox'], param['width'], param['height'])
            RTI = RasterToImage(**parameter_dict)
            output = RTI.xml_request()

        elif self.command == cl[5]:
            parameter_list = ['fileName', 'coord', 'boundingBox', 'cropShape']
            parameter_dict = get_parameter(parameter_list, self.params)
            # SGC = StatisticGridCoverage(param['fileName'], param['coord'], param['boundingBox'])
            SGC = StatisticsGridCoverage(**parameter_dict)
            output = SGC.xml_request()

        else:
            cl_str = ''
            for i, s in enumerate(cl):
                cl_str += s
                if len(cl) == i+1:
                    continue
                cl_str += ', '

            output = "The 'command' parameters that we support are '{}'".format(cl_str)

        return output

    # def __get_parameter(self, parameter_list):
    #
    #     parameter_dict = dict()
    #     for p in parameter_list:
    #         if p in self.params:
    #             parameter_dict[p] = self.params[p]
    #
    #     return parameter_dict


class LinearLineOfSight(object):

    def __init__(self, fileName, observerPoint, targetPoint, coord=None, boundingBox=None, observerOffset=0):
        self.fileName = fileName
        self.observerPoint = observerPoint
        self.observerOffset = str(observerOffset)
        self.targetPoint = targetPoint

        if (not coord) or (not boundingBox):
            geo_response = SARequest.wcs_describe_request(fileName)

            if not coord:
                coord = SAParsing.wcs_describe_parsing(geo_response)[0]

            if not boundingBox:
                boundingBox = SAParsing.wcs_describe_parsing(geo_response)[1]

        self.coord = int(coord)
        self.boundingBox = boundingBox


    def xml_request(self):

        geo_response = SARequest.sa_request(self.xml_create()).text

        try:
            geo_response = self.analysis(geo_response)

        except Exception as e:
            print('Except :', e)

        return geo_response

    # def xml_request(self):
    #
    #     return SARequest.sa_request(self.xml_create, self.analysis)

    @staticmethod
    def analysis(geo_response):

        def coord_parsing(coordinates):
            coord_list = coordinates['feature:LinearLineOfSight']['feature:geom']['gml:MultiLineString']['gml:lineStringMember'][
                'gml:LineString']['gml:coordinates'].split()
            temp_list = []
            for coord in coord_list:
                x, y, _ = coord.split(',')
                temp_list.append([float(x), float(y)])

            return temp_list

        xml_dict = json.loads(json.dumps(xmltodict.parse(geo_response)))
        iter_dict = xml_dict['wfs:FeatureCollection']['gml:featureMember']

        if isinstance(iter_dict, list):
            visible_list = []

            for i in iter_dict:
                visible_list.append(i)
        else:
            visible_list = [iter_dict]

        visible_dict = {}
        for l in visible_list:
            visible = int(l['feature:LinearLineOfSight']['feature:Visible'])
            if visible == 0:
                xy_list = coord_parsing(l)
                visible_dict['invisible'] = xy_list

            else:
                xy_list = coord_parsing(l)
                visible_dict['visible'] = xy_list

        return visible_dict

    def xml_create(self):

        execute = element_execute()

        identifier(execute, 'statistics:LinearLineOfSight')
        # xml_elements(execute, 'ows:Identifier', text='statistics:LinearLineOfSight')
        data_inputs = xml_elements(execute, 'wps:DataInputs')

        # bounding_boxes = [122.99986111111112, 32.999861111111116, 132.0001388888889, 44.00013888888889]
        raster_input(data_inputs, self.fileName, self.coord, self.boundingBox)

        ob_complex_dict = {'mimeType': 'application/wkt'}
        ob_point_dict = {'child': 'wps:ComplexData', 'attribute': ob_complex_dict,
                         'text': 'POINT({} {})'.format(self.observerPoint[0], self.observerPoint[1])}
        element_input(data_inputs, 'observerPoint', ob_point_dict)

        ob_offset_dict = {'child': 'wps:LiteralData', 'text': '{}'.format(self.observerOffset)}
        element_input(data_inputs, 'observerOffset', ob_offset_dict)

        tg_complex_dict = {'mimeType': 'application/wkt'}
        tg_point_dict = {'child': 'wps:ComplexData', 'attribute': tg_complex_dict,
                         'text': 'POINT({} {})'.format(self.targetPoint[0], self.targetPoint[1])}
        element_input(data_inputs, 'targetPoint', tg_point_dict)

        rdo_dict = {'mimeType': 'text/xml; subtype=wfs-collection/1.0'}
        element_response_form(execute, rdo_dict)

        # indent(execute)
        # dump(execute)

        return '<?xml version="1.0" encoding="UTF-8"?>' + tostring(execute, encoding='utf-8').decode('utf-8')

    # def xml_create(self):
    #
    #     xml = SARequest.common(0) + '<ows:Identifier>statistics:LinearLineOfSight</ows:Identifier>' \
    #           '<wps:DataInputs>' \
    #           '<wps:Input>' \
    #           '<ows:Identifier>inputCoverage</ows:Identifier>' \
    #           '<wps:Reference mimeType="image/tiff" ' \
    #           'xlink:href="http://geoserver/wcs" method="POST">' \
    #           '<wps:Body>' \
    #           '<wcs:GetCoverage service="WCS" version="1.1.1">' \
    #           '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
    #           '<wcs:DomainSubset>'\
    #           '<ows:BoundingBox crs="http://www.opengis.net/gml/srs/epsg.xml#' + str(self.coord) + '">'\
    #           '<ows:LowerCorner>' + str(self.boundingBox[0]) + ' ' + str(self.boundingBox[1]) + '</ows:LowerCorner>' \
    #           '<ows:UpperCorner>' + str(self.boundingBox[2]) + ' ' + str(self.boundingBox[3]) + '</ows:UpperCorner>' \
    #           '</ows:BoundingBox>' \
    #           '</wcs:DomainSubset>' \
    #           '<wcs:Output format="image/tiff"/>' \
    #           '</wcs:GetCoverage>' \
    #           '</wps:Body>' \
    #           '</wps:Reference>' \
    #           '</wps:Input>' \
    #           '<wps:Input>' \
    #           '<ows:Identifier>observerPoint</ows:Identifier>' \
    #           '<wps:Data>' \
    #           '<wps:ComplexData mimeType="application/wkt">' \
    #           '<![CDATA[POINT(' + str(self.observerPoint[0]) + ' ' + str(self.observerPoint[1]) + ')]]>' \
    #           '</wps:ComplexData>' \
    #           '</wps:Data>' \
    #           '</wps:Input>' \
    #           '<wps:Input>' \
    #           '<ows:Identifier>observerOffset</ows:Identifier>' \
    #           '<wps:Data>' \
    #           '<wps:LiteralData>' + str(self.observerOffset) + '</wps:LiteralData>' \
    #           '</wps:Data>' \
    #           '</wps:Input>' \
    #           '<wps:Input>' \
    #           '<ows:Identifier>targetPoint</ows:Identifier>' \
    #           '<wps:Data>' \
    #           '<wps:ComplexData mimeType="application/wkt">' \
    #           '<![CDATA[POINT(' + str(self.targetPoint[0]) + ' ' + str(self.targetPoint[1]) + ')]]>' \
    #           '</wps:ComplexData>' \
    #           '</wps:Data>' \
    #           '</wps:Input>' \
    #           '</wps:DataInputs>' + SARequest.common(1)
    #
    #     return xml


class RasterCutFill(SARequest):

    def __init__(self, fileName, inputGeometry, coord=None, boundingBox=None, userMeanHeight=-9999):
        self.fileName = fileName
        self.inputGeometry = inputGeometry
        self.userMeanHeight = userMeanHeight

        if (not coord) or (not boundingBox):
            geo_response = SARequest.wcs_describe_request(fileName)

            if not coord:
                coord = SAParsing.wcs_describe_parsing(geo_response)[0]

            if not boundingBox:
                boundingBox = SAParsing.wcs_describe_parsing(geo_response)[1]

        self.coord = int(coord)
        self.boundingBox = boundingBox

    def xml_request(self):
        geo_response = SARequest.sa_request(self.xml_create()).text

        try:
            geo_response = self.analysis(geo_response)

        except Exception as e:
            print('Except :', e)

        return geo_response

    @staticmethod
    def analysis(geo_response):

        def coord_parsing(coordinates):
            coord_list = coordinates['feature:geom']['gml:MultiPolygon']['gml:polygonMember']

            if not isinstance(coord_list, list):
                coord_list = [coord_list]

            final_coord_list = []
            for c in coord_list:
                coord_dict = {}
                polygon = c['gml:Polygon']
                for k in polygon.keys():
                    if isinstance(polygon[k], list):
                        temp_list = []
                        for p in polygon[k]:
                            temp_list.append(p['gml:LinearRing']['gml:coordinates'].split())


                    else:
                        temp_list = [polygon[k]['gml:LinearRing']['gml:coordinates'].split()]

                    coord_dict[k[4:]] = temp_list

                final_coord_list.append(coord_dict)

            return final_coord_list

        def parsing(parsing_dict):

            parsed_dict = {}

            category = int(parsing_dict['feature:category'])
            if category == -1:
                category = 'fill'

            elif category == 1:
                category = 'cut'

            else:
                category = 'none'

            parsed_dict['area'] = parsing_dict['feature:area']
            parsed_dict['category'] = category
            parsed_dict['count'] = parsing_dict['feature:count']
            parsed_dict['volume'] = parsing_dict['feature:volume']
            parsed_dict['coordinates'] = coord_parsing(parsing_dict)

            return parsed_dict

        xml_dict = json.loads(json.dumps(xmltodict.parse(geo_response)))
        iter_dict = xml_dict['wfs:FeatureCollection']['gml:featureMember']

        if isinstance(iter_dict, list):
            category_list = []

            for i in iter_dict:
                category_list.append(i)
        else:
            category_list = [iter_dict]

        final_list = []
        for l in category_list:

            cutfill_dict = l['feature:CutFill']
            final_list.append(parsing(cutfill_dict))

        return final_list

    # def xml_create(self):
    #
    #     execute = element_execute()
    #
    #     identifier(execute, 'statistics:RasterCutFill')
    #     data_inputs = xml_elements(execute, 'wps:DataInputs')
    #
    #     # bounding_boxes = [122.99986111111112, 32.999861111111116, 132.0001388888889, 44.00013888888889]
    #     raster_input(data_inputs, self.fileName, self.coord, self.boundingBox)
    #
    #     ob_complex_dict = {'mimeType': 'application/wkt'}
    #     ob_point_dict = {'child': 'wps:ComplexData', 'attribute': ob_complex_dict,
    #                      'text': 'POINT({} {})'.format(self.observerPoint[0], self.observerPoint[1])}
    #     element_input(data_inputs, 'observerPoint', ob_point_dict)
    #
    #     ob_offset_dict = {'child': 'wps:LiteralData', 'text': '{}'.format(self.observerOffset)}
    #     element_input(data_inputs, 'observerOffset', ob_offset_dict)
    #
    #     tg_complex_dict = {'mimeType': 'application/wkt'}
    #     tg_point_dict = {'child': 'wps:ComplexData', 'attribute': tg_complex_dict,
    #                      'text': 'POINT({} {})'.format(self.targetPoint[0], self.targetPoint[1])}
    #     element_input(data_inputs, 'targetPoint', tg_point_dict)
    #
    #     rdo_dict = {'mimeType': 'text/xml; subtype=wfs-collection/1.0'}
    #     element_response_form(execute, rdo_dict)
    #
    #     # indent(execute)
    #     # dump(execute)
    #
    #     return '<?xml version="1.0" encoding="UTF-8"?>' + tostring(execute, encoding='utf-8').decode('utf-8')

    def xml_create(self):

        xml = SARequest.common(0) + '<ows:Identifier>statistics:RasterCutFill</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>inputCoverage</ows:Identifier>' \
              '<wps:Reference mimeType="image/tiff" ' \
              'xlink:href="http://geoserver/wcs" method="POST">' \
              '<wps:Body>' \
              '<wcs:GetCoverage service="WCS" version="1.1.1">' \
              '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
              '<wcs:DomainSubset>'\
              '<ows:BoundingBox crs="http://www.opengis.net/gml/srs/epsg.xml#' + str(self.coord) + '">'\
              '<ows:LowerCorner>' + str(self.boundingBox[0]) + ' ' + str(self.boundingBox[1]) + '</ows:LowerCorner>' \
              '<ows:UpperCorner>' + str(self.boundingBox[2]) + ' ' + str(self.boundingBox[3]) + '</ows:UpperCorner>' \
              '</ows:BoundingBox>' \
              '</wcs:DomainSubset>' \
              '<wcs:Output format="image/tiff"/>' \
              '</wcs:GetCoverage>' \
              '</wps:Body>' \
              '</wps:Reference>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>cropShape</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:ComplexData mimeType="application/wkt">' \
              '<![CDATA[MULTIPOLYGON(((' + str(self.inputGeometry) + ')))]]>' \
              '</wps:ComplexData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>baseHeight</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:LiteralData>' + str(self.userMeanHeight) + '</wps:LiteralData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '</wps:DataInputs>' + SARequest.common(1)

        return xml


class ClipWithGeometry(SARequest):
    def __init__(self, fileName, clipGeometry):
        self.fileName = fileName
        self.clipGeometry = clipGeometry

    def xml_request(self):
        geo_response = SARequest.sa_request(self.xml_create()).text

        try:
            geo_response = self.analysis(geo_response)

        except Exception as e:
            print('Except :', e)

        return geo_response

    @staticmethod
    def analysis(geo_response):
        xml_dict = json.loads(json.dumps(xmltodict.parse(geo_response)))
        iter_dict = xml_dict['wfs:FeatureCollection']['gml:featureMember']

        return geo_response

    def xml_create(self):

        xml = SARequest.common(0) + '<ows:Identifier>statistics:ClipWithGeometry</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>inputFeatures</ows:Identifier>' \
              '<wps:Reference mimeType="text/xml" xlink:href="http://geoserver/wfs" method="POST">' \
              '<wps:Body>' \
              '<wfs:GetFeature service="WFS" version="1.0.0" outputFormat="GML2" xmlns:lhdt="lhdt">' \
              '<wfs:Query typeName="' + self.fileName + '"/>' \
              '</wfs:GetFeature>' \
              '</wps:Body>' \
              '</wps:Reference>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>clipGeometry</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:ComplexData mimeType="application/wkt">' \
              '<![CDATA[MULTIPOLYGON(((' + str(self.clipGeometry) + ')))]]>' \
              '</wps:ComplexData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '</wps:DataInputs>' + SARequest.common(1)

        return xml


# 아래와 같은 경우는 geoserver에 레이어가 등록되어 있는 것의 면적을 구해주는 것으로 검토 필요.
class CalculateArea(SARequest):
    def __init__(self, fileName):
        self.fileName = fileName

    @staticmethod
    def analysis(geo_response):
        xml_dict = json.loads(json.dumps(xmltodict.parse(geo_response)))
        iter_dict = xml_dict['wfs:FeatureCollection']['gml:featureMember']

        return iter_dict

    def xml_request(self):
        geo_response = SARequest.sa_request(self.xml_create()).text

        try:
            geo_response = self.analysis(geo_response)

        except Exception as e:
            print('Except :', e)

        return geo_response

    def xml_create(self):

        xml = SARequest.common(0) + '<ows:Identifier>statistics:CalculateArea</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>inputFeatures</ows:Identifier>' \
              '<wps:Reference mimeType="text/xml" ' \
              'xlink:href="http://geoserver/wfs" method="POST">' \
              '<wps:Body>' \
              '<wfs:GetFeature service="WFS" version="1.0.0" outputFormat="GML2" xmlns:lhdt="lhdt">' \
              '<wfs:Query typeName="' + self.fileName + '"/>' \
              '</wfs:GetFeature>' \
              '</wps:Body>' \
              '</wps:Reference>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>areaUnit</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:LiteralData>Default</wps:LiteralData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>areaUnit</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:LiteralData>Default</wps:LiteralData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '</wps:DataInputs>' + SARequest.common(1)

        return xml


# Hold for a while
class RasterToImage(SARequest):

    def __init__(self, fileName, coord= None, boundingBox=None, width=256, height=256):
        self.fileName = fileName
        self.width = width
        self.height = height

        if (not coord) or (not boundingBox):
            geo_response = SARequest.wcs_describe_request(fileName)

            if not coord:
                coord = SAParsing.wcs_describe_parsing(geo_response)[0]

            if not boundingBox:
                boundingBox = SAParsing.wcs_describe_parsing(geo_response)[1]

        self.coord = int(coord)
        self.boundingBox = boundingBox

    @staticmethod
    def analysis(geo_response):
        # output = geo_response.decode('utf-8')

        output = base64.b64encode(geo_response).decode('utf-8')
        return output

    def xml_request(self):

        geo_response = SARequest.sa_request(self.xml_create()).text

        try:
            geo_response = self.analysis(geo_response)

        except Exception as e:
            print('Except :', e)

        return geo_response

    def xml_create(self):

        xml = SARequest.common(0) + '<ows:Identifier>statistics:RasterToImage</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>coverage</ows:Identifier>' \
              '<wps:Reference mimeType="image/tiff" ' \
              'xlink:href="http://geoserver/wcs" method="POST">' \
              '<wps:Body>' \
              '<wcs:GetCoverage service="WCS" version="1.1.1">' \
              '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
              '<wcs:DomainSubset>'\
              '</wcs:DomainSubset>' \
              '<wcs:Output format="image/tiff"/>' \
              '</wcs:GetCoverage>' \
              '</wps:Body>' \
              '</wps:Reference>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>width</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:LiteralData>' + str(self.width) + '</wps:LiteralData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>height</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:LiteralData>' + str(self.height) + '</wps:LiteralData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '</wps:DataInputs>' \
              '<wps:ResponseForm>' \
              '<wps:RawDataOutput mimeType="image/png">' \
              '<ows:Identifier>result</ows:Identifier>' \
              '</wps:RawDataOutput>' \
              '</wps:ResponseForm>' \
              '</wps:Execute>'
        print(xml)

        return xml


class StatisticsGridCoverage(SARequest):

    def __init__(self, fileName, cropShape, coord=None, boundingBox=None):
        self.fileName = fileName
        self.coord = coord
        self.boundingBox = boundingBox
        self.cropShape = cropShape

        if (not coord) or (not boundingBox):
            geo_response = SARequest.wcs_describe_request(fileName)

            if not coord:
                coord = SAParsing.wcs_describe_parsing(geo_response)[0]

            if not boundingBox:
                boundingBox = SAParsing.wcs_describe_parsing(geo_response)[1]

        self.coord = int(coord)
        self.boundingBox = boundingBox

    @staticmethod
    def analysis(geo_response):
        xml_dict = json.loads(json.dumps(xmltodict.parse(geo_response)))
        iter_dict = xml_dict['DataStatistics']['Item']

        return iter_dict

    def xml_request(self):
        geo_response = SARequest.sa_request(self.xml_create()).text

        try:
            geo_response = self.analysis(geo_response)

        except Exception as e:
            print('Except :', e)

        return geo_response


    def xml_create(self):

        xml = SARequest.common(0) + '<ows:Identifier>statistics:StatisticsGridCoverage</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>inputCoverage</ows:Identifier>' \
              '<wps:Reference mimeType="image/tiff" xlink:href="http://geoserver/wcs" method="POST">' \
              '<wps:Body>' \
              '<wcs:GetCoverage service="WCS" version="1.1.1">' \
              '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
              '<wcs:DomainSubset>'\
              '<ows:BoundingBox crs="http://www.opengis.net/gml/srs/epsg.xml#' + str(self.coord) + '">'\
              '<ows:LowerCorner>' + str(self.boundingBox[0]) + ' ' + str(self.boundingBox[1]) + '</ows:LowerCorner>' \
              '<ows:UpperCorner>' + str(self.boundingBox[2]) + ' ' + str(self.boundingBox[3]) + '</ows:UpperCorner>' \
              '</ows:BoundingBox>' \
              '</wcs:DomainSubset>' \
              '<wcs:Output format="image/tiff"/>' \
              '</wcs:GetCoverage>' \
              '</wps:Body>' \
              '</wps:Reference>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>cropShape</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:ComplexData mimeType="application/wkt">' \
              '<![CDATA[POLYGON((' + str(self.cropShape) + '))]]></wps:ComplexData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '</wps:DataInputs>' \
              '<wps:ResponseForm>' \
              '<wps:RawDataOutput mimeType="text/xml">' \
              '<ows:Identifier>result</ows:Identifier>' \
              '</wps:RawDataOutput>' \
              '</wps:ResponseForm>' \
              '</wps:Execute>'

        return xml

    # def xml_create(self):
    #
    #     xml = SARequest.common(0) + '<ows:Identifier>statistics:StatisticsGridCoverage</ows:Identifier>' \
    #           '<wps:DataInputs>' \
    #           '<wps:Input>' \
    #           '<ows:Identifier>inputCoverage</ows:Identifier>' \
    #           '<wps:Reference mimeType="image/tiff" xlink:href="http://geoserver/wcs" method="POST">' \
    #           '<wps:Body>' \
    #           '<wcs:GetCoverage service="WCS" version="1.1.1">' \
    #           '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
    #           '<wcs:DomainSubset>'\
    #           '<ows:BoundingBox crs="http://www.opengis.net/gml/srs/epsg.xml#' + str(self.coord) + '">'\
    #           '<ows:LowerCorner>' + str(self.boundingBox[0]) + ' ' + str(self.boundingBox[1]) + '</ows:LowerCorner>' \
    #           '<ows:UpperCorner>' + str(self.boundingBox[2]) + ' ' + str(self.boundingBox[3]) + '</ows:UpperCorner>' \
    #           '</ows:BoundingBox>' \
    #           '</wcs:DomainSubset>' \
    #           '<wcs:Output format="image/tiff"/>' \
    #           '</wcs:GetCoverage>' \
    #           '</wps:Body>' \
    #           '</wps:Reference>' \
    #           '</wps:Input>' \
    #           '</wps:DataInputs>' \
    #           '<wps:ResponseForm>' \
    #           '<wps:RawDataOutput mimeType="text/xml">' \
    #           '<ows:Identifier>result</ows:Identifier>' \
    #           '</wps:RawDataOutput>' \
    #           '</wps:ResponseForm>' \
    #           '</wps:Execute>'
    #
    #     print(xml)
    #     return xml

# class RasterReclass(SARequest):
#     def __init__(self, fileName):
#         self.fileName = fileName
#
#     @staticmethod
#     def analysis(geo_response):
#         xml_dict = json.loads(json.dumps(xmltodict.parse(geo_response)))
#         iter_dict = xml_dict['wfs:FeatureCollection']['gml:featureMember']
#
#         return iter_dict
#
#     def xml_request(self):
#         return super().sa_request(self.xml_create, self.analysis)
#
#     def xml_create(self):
#
#         xml = SARequest.common(0) + '<ows:Identifier>statistics:RasterReclass</ows:Identifier>' \
#               '<wps:DataInputs>' \
#               '<wps:Input>' \
#               '<ows:Identifier>inputCoverage</ows:Identifier>' \
#               '<wps:Reference mimeType="image/tiff" ' \
#               'xlink:href="http://geoserver/wcs" method="POST">' \
#               '<wps:Body>' \
#               '<wcs:GetCoverage service="WCS" version="1.1.1">' \
#               '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
#               '<wcs:DomainSubset>'\
#               '<ows:BoundingBox crs="http://www.opengis.net/gml/srs/epsg.xml#' + self.coord + '">'\
#               '<ows:LowerCorner>' + str(self.boundingBox[0]) + ' ' + str(self.boundingBox[1]) + '</ows:LowerCorner>' \
#               '<ows:UpperCorner>' + str(self.boundingBox[2]) + ' ' + str(self.boundingBox[3]) + '</ows:UpperCorner>' \
#               '</ows:BoundingBox>' \
#               '</wcs:DomainSubset>' \
#               '<wcs:Output format="image/tiff"/>' \
#               '</wcs:GetCoverage>' \
#               '</wps:Body>' \
#               '</wps:Reference>' \
#               '</wps:Input>' \
#               '<wps:Input>' \
#               '<ows:Identifier>ranges</ows:Identifier>' \
#               '<wps:Data>' \
#               '<wps:LiteralData>0.0 30.0 1; 30.0 270.0 2; 270.0 365.0 3</wps:LiteralData>' \
#               '</wps:Data>' \
#               '</wps:Input>' \
#               '</wps:DataInputs>' + SARequest.common(1)
#
#         return xml


if __name__ == "__main__":
    # data = 'ds:sejong_dem'
    # coord = '4326'
    # inputCoverage = [122.99986111111112, 32.999861111111116,132.0001388888889, 44.00013888888889]
    # observerPoint = [127.2222222222, 36.499999999999]
    # observerOffset = 1.8
    # targetPoint = [127.29999999999, 36.52222222222]
    #
    # print(LinearLineOfSight(data, coord, inputCoverage, observerPoint, observerOffset, targetPoint).xml_create())
    print('main')
