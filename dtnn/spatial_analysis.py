

import requests

# xml같은 경우 띄어쓰기나 이런 사소한 것으로 parsing error가 발생할 수도 있음


class LinearLineOfSight(object):

    def __init__(self, fileName, coord, inputCoverage, observerPoint, observerOffset, targetPoint):
        self.fileName = fileName
        self.coord = coord
        self.inputCoverage = inputCoverage
        self.observerPoint = observerPoint
        self.observerOffset = observerOffset
        self.targetPoint = targetPoint

    def analysis(self):

        url = 'http://localhost:8080/geoserver/wps'
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        georesponse = requests.post(url, data = self.xml_create(), headers=headers).text

        return georesponse

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
              '<ows:LowerCorner>' + str(self.inputCoverage[0]) + ' ' + str(self.inputCoverage[1]) + '</ows:LowerCorner>' \
              '<ows:UpperCorner>' + str(self.inputCoverage[2]) + ' ' + str(self.inputCoverage[3]) + '</ows:UpperCorner>' \
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

    def __init__(self, fileName, coord, inputCoverage, observerPoint, observerOffset, targetPoint):
        self.fileName = fileName
        self.coord = coord
        self.inputCoverage = inputCoverage
        self.observerPoint = observerPoint
        self.observerOffset = observerOffset
        self.targetPoint = targetPoint

    def analysis(self):

        url = 'http://localhost:8080/geoserver/wps'
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        georesponse = requests.post(url, data = self.xml_create(), headers=headers).text

        return georesponse

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
              '<ows:LowerCorner>' + str(self.inputCoverage[0]) + ' ' + str(self.inputCoverage[1]) + '</ows:LowerCorner>' \
              '<ows:UpperCorner>' + str(self.inputCoverage[2]) + ' ' + str(self.inputCoverage[3]) + '</ows:UpperCorner>' \
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


if __name__ == "__main__":
    data = 'ds:sejong_dem'
    coord = '4326'
    inputCoverage = [122.99986111111112, 32.999861111111116,132.0001388888889, 44.00013888888889]
    observerPoint = [127.2222222222, 36.499999999999]
    observerOffset = 1.8
    targetPoint = [127.29999999999, 36.52222222222]

    print(LinearLineOfSight(data, coord, inputCoverage, observerPoint, observerOffset, targetPoint).xml_create())
