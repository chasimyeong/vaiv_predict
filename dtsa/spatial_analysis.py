
from flask import jsonify

import requests

import xmltodict
import json

# xml같은 경우 띄어쓰기나 이런 사소한 것으로 parsing error가 발생할 수도 있음


def api(data):

    command = data['command']
    param = data['parameter']

    if command == "linear_line_of_sight":
        LLOS = LinearLineOfSight(param['fileName'], param['coord'], param['boundingBox'],
                                    param['observerPoint'], param['observerOffset'], param['targetPoint'])
        result = LLOS.xml_request()
    elif command == "calculate_cut_fill":
        CCF = CalculateCutFill(param['fileName'], param['coord'], param['boundingBox'],
                                  param['inputGeometry'], param['userMeanHeight'])
        result = CCF.xml_request()

    elif command == "calculate_area":
        CA = CalculateArea(param['fileName'])
        result = CA.xml_request()

    else:
        result = "The 'command' parameters that we support are 'linear_line_of_sight', " \
                   "'calculate_cut_fill'"

    return jsonify({'command': command, 'result': result})


class LinearLineOfSight(object):

    def __init__(self, fileName, coord, boundingBox, observerPoint, observerOffset, targetPoint):
        self.fileName = fileName
        self.coord = coord
        self.boundingBox = boundingBox
        self.observerPoint = observerPoint
        self.observerOffset = observerOffset
        self.targetPoint = targetPoint

    def xml_request(self):

        url = 'http://localhost:18080/geoserver/wps'
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        geo_response = requests.post(url, data=self.xml_create(), headers=headers).text
        print(geo_response)
        geo_response = self.analysis(geo_response)

        return geo_response

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

        # if not isinstance(self.inputCoverage, list):
        #     return print('inputCoverage는 list형식으로만 지원합니다.')

        xml = '<?xml version="1.0" encoding="UTF-8"?>' \
              '<wps:Execute version="1.0.0" service="WPS" '\
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wps/1.0.0" ' \
              'xmlns:wfs="http://www.opengis.net/wfs" xmlns:wps="http://www.opengis.net/wps/1.0.0" ' \
              'xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" ' \
              'xmlns:ogc="http://www.opengis.net/ogc" xmlns:wcs="http://www.opengis.net/wcs/1.1.1" ' \
              'xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ' \
              'http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">' \
              '<ows:Identifier>statistics:LinearLineOfSight</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>inputCoverage</ows:Identifier>' \
              '<wps:Reference mimeType="image/tiff" ' \
              'xlink:href="http://geoserver/wcs" method="POST">' \
              '<wps:Body>' \
              '<wcs:GetCoverage service="WCS" version="1.1.1">' \
              '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
              '<wcs:DomainSubset>'\
              '<ows:BoundingBox crs="http://www.opengis.net/gml/srs/epsg.xml#' + self.coord + '">'\
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
              '<ows:Identifier>observerPoint</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:ComplexData mimeType="application/wkt">' \
              '<![CDATA[POINT(' + str(self.observerPoint[0]) + ' ' + str(self.observerPoint[1]) + ')]]>' \
              '</wps:ComplexData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>observerOffset</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:LiteralData>' + str(self.observerOffset) + '</wps:LiteralData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '<wps:Input>' \
              '<ows:Identifier>targetPoint</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:ComplexData mimeType="application/wkt">' \
              '<![CDATA[POINT(' + str(self.targetPoint[0]) + ' ' + str(self.targetPoint[1]) + ')]]>' \
              '</wps:ComplexData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '</wps:DataInputs>' \
              '<wps:ResponseForm>' \
              '<wps:RawDataOutput mimeType="application/vnd.geo+json; subtype=wfs-collection/1.0">'\
              '<ows:Identifier>result</ows:Identifier>' \
              '</wps:RawDataOutput>' \
              '</wps:ResponseForm>' \
              '</wps:Execute>'

        return xml


class CalculateCutFill(object):

    def __init__(self, fileName, coord, boundingBox, inputGeometry, userMeanHeight=-9999):
        self.fileName = fileName
        self.coord = coord
        self.boundingBox = boundingBox
        self.inputGeometry = inputGeometry
        self.userMeanHeight = userMeanHeight

    def xml_request(self):

        url = 'http://localhost:18080/geoserver/wps'
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        print(self.xml_create())
        geo_response = requests.post(url, data=self.xml_create(), headers=headers).text
        geo_response = self.analysis(geo_response)
        return geo_response

    @staticmethod
    def analysis(geo_response):

        def coord_parsing(coordinates):
            coord_list = coordinates['feature:geom']['gml:MultiPolygon']['gml:polygonMember']

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

                    coord_dict[k] = temp_list

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

    def xml_create(self):

        # if not isinstance(self.inputCoverage, list):
        #     return print('inputCoverage는 list형식으로만 지원합니다.')

        xml = '<?xml version="1.0" encoding="UTF-8"?>' \
              '<wps:Execute version="1.0.0" service="WPS" '\
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wps/1.0.0" ' \
              'xmlns:wfs="http://www.opengis.net/wfs" xmlns:wps="http://www.opengis.net/wps/1.0.0" ' \
              'xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" ' \
              'xmlns:ogc="http://www.opengis.net/ogc" xmlns:wcs="http://www.opengis.net/wcs/1.1.1" ' \
              'xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ' \
              'http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">' \
              '<ows:Identifier>statistics:RasterCutFill</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>inputCoverage</ows:Identifier>' \
              '<wps:Reference mimeType="image/tiff" ' \
              'xlink:href="http://geoserver/wcs" method="POST">' \
              '<wps:Body>' \
              '<wcs:GetCoverage service="WCS" version="1.1.1">' \
              '<ows:Identifier>' + self.fileName + '</ows:Identifier>' \
              '<wcs:DomainSubset>'\
              '<ows:BoundingBox crs="http://www.opengis.net/gml/srs/epsg.xml#' + self.coord + '">'\
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
              '</wps:DataInputs>' \
              '<wps:ResponseForm>' \
              '<wps:RawDataOutput mimeType="application/vnd.geo+json; subtype=wfs-collection/1.0">'\
              '<ows:Identifier>result</ows:Identifier>' \
              '</wps:RawDataOutput>' \
              '</wps:ResponseForm>' \
              '</wps:Execute>'

        return xml

class CalculateArea(object):
    def __init__(self, fileName):
        self.fileName = fileName

    @staticmethod
    #내일 이부분 만들고 테스트 해보기
    #그전에 geoserver layer 등록해야됨
    #적당한 shape?을 찾아야할듯 이전에 했던거 잘 기억해서 해보자구~
    def analysis(geo_response):
        final = []
        return final

    def xml_request(self):

        url = 'http://localhost:18080/geoserver/wps'
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        geo_response = requests.post(url, data=self.xml_create(), headers=headers).text
        geo_response = self.analysis(geo_response)
        return geo_response

    def xml_create(self):

        xml = '<?xml version="1.0" encoding="UTF-8"?>' \
              '<wps:Execute version="1.0.0" service="WPS" ' \
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wps/1.0.0" ' \
              'xmlns:wfs="http://www.opengis.net/wfs" xmlns:wps="http://www.opengis.net/wps/1.0.0" ' \
              'xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" ' \
              'xmlns:ogc="http://www.opengis.net/ogc" xmlns:wcs="http://www.opengis.net/wcs/1.1.1" ' \
              'xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ' \
              'http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">' \
              '<ows:Identifier>statistics:CalculateArea</ows:Identifier>' \
              '<wps:DataInputs>' \
              '<wps:Input>' \
              '<ows:Identifier>inputFeatures</ows:Identifier>' \
              '<wps:Reference mimeType="text/xml" ' \
              'xlink:href="http://geoserver/wfs" method="POST">' \
              '<wps:Body>' \
              '<wfs:GetFeature service="WFS" version="1.0.0" outputFormat="GML2" xmlns:lhdt="lhdt">' \
              '<wfs:Query typeName=' + self.fileName + '/>' \
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
              '<ows:Identifier>areaUnit</ows:Identifier>' \
              '<wps:Data>' \
              '<wps:LiteralData>Default</wps:LiteralData>' \
              '</wps:Data>' \
              '</wps:Input>' \
              '</wps:DataInputs>' \
              '<wps:ResponseForm>' \
              '<wps:RawDataOutput mimeType="application/vnd.geo+json; subtype=wfs-collection/1.0">' \
              '<ows:Identifier>result</ows:Identifier>' \
              '</wps:RawDataOutput>' \
              '</wps:ResponseForm>' \
              '</wps:Execute>'

        return xml

if __name__ == "__main__":
    data = 'ds:sejong_dem'
    coord = '4326'
    inputCoverage = [122.99986111111112, 32.999861111111116,132.0001388888889, 44.00013888888889]
    observerPoint = [127.2222222222, 36.499999999999]
    observerOffset = 1.8
    targetPoint = [127.29999999999, 36.52222222222]

    print(LinearLineOfSight(data, coord, inputCoverage, observerPoint, observerOffset, targetPoint).xml_create())
