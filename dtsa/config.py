"""
All Spatial-analysis command value
"""
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
                STATISTICS_GRID_COVERAGE]

"""
geoserver request url
"""
geo_ip = 'localhost'
geo_port = 18080
GEOSERVER_WPS_URL = 'http://{}:{}/geoserver/wps'.format(geo_ip, geo_port)
GEOSERVER_WCS_URL = 'http://{}:{}/geoserver/wcs'.format(geo_ip, geo_port)
GEOSERVER_WFS_URL = 'http://{}:{}/geoserver/wfs'.format(geo_ip, geo_port)
