"""
All Spatial-analysis command value
"""
# Raster info
WCS_LIST = 'wcs_list'
# Raster Analysis
CLIP_WITH_GEOMETRY = 'clip_with_geometry'
LINEAR_LINE_OF_SIGHT = 'linear_line_of_sight'
RASTER_CUT_FILL = 'raster_cut_fill'
RASTER_TO_IMAGE = 'raster_to_image'
STATISTICS_GRID_COVERAGE = 'statistics_grid_coverage'
# Vector Analysis
CALCULATE_AREA = 'calculate_area'
# Spatial analysis command list
COMMAND_LIST = [LINEAR_LINE_OF_SIGHT, RASTER_CUT_FILL, CLIP_WITH_GEOMETRY, CALCULATE_AREA, RASTER_TO_IMAGE,
                STATISTICS_GRID_COVERAGE, WCS_LIST]

"""
geoserver request url
"""
geo_ip = 'localhost'
geo_port = 18080
GEOSERVER_WPS_URL = 'http://{}:{}/geoserver/wps'.format(geo_ip, geo_port)
GEOSERVER_WCS_URL = 'http://{}:{}/geoserver/wcs'.format(geo_ip, geo_port)
GEOSERVER_WFS_URL = 'http://{}:{}/geoserver/wfs'.format(geo_ip, geo_port)

"""
geoserver opengis url
"""
VERSION = ['1.0.0', '1.1.1']
SERVICE = ['WPS', 'WCS']
XMLNS = "http://www.opengis.net/wps/1.0.0"
XMLNS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
XMLNS_WFS = "http://www.opengis.net/wfs"
XMLNS_WPS = "http://www.opengis.net/wps/1.0.0"
XMLNS_OWS = "http://www.opengis.net/ows/1.1"
XMLNS_GML = "http://www.opengis.net/gml"
XMLNS_OGC = "http://www.opengis.net/ogc"
XMLNS_WCS = "http://www.opengis.net/wcs/1.1.1"
XMLNS_XLINK = "http://www.w3.org/1999/xlink"
XSI_SCHEMALOCATION = "http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd"