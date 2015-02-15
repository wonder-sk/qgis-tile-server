# -*- coding: utf-8 -*-
#
# Copyright (C) 2015  Martin Dobias
#
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# ----- configuration part ----- #

# path to QGIS installation dir
qgis_path = '/home/martin/qgis/git-master/creator/output'
# path where tiles will be stored
tile_path = '/tmp/tiles'
# QGIS project file to be used
project_file = '/data/gis/tst-countries.qgs'

# main page with the Leaflet map
index_html = """
<!DOCTYPE html><html><head>
<title>QGIS tile server</title>
<link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.7.3/leaflet.css" />
<style>
body { padding: 0; margin: 0; }
html, body, #map { height: 100%; width: 100%; }
</style></head><body>
<div id="map"></div>
<script src="http://cdn.leafletjs.com/leaflet-0.7.3/leaflet.js"></script>
<script>
var map = L.map('map').setView([0, 0], 3);
L.tileLayer('/{z}/{x}/{y}/',
    { maxZoom: 10, attribution: '<a href="https://github.com/wonder-sk/qgis-tile-server">QGIS tile server</a>'}).addTo(map);
</script></body></html>"""


# ----- QGIS part ----- #

import math, sys, os
os.environ['QGIS_PREFIX_PATH'] = qgis_path
sys.path.append(qgis_path+'/python')
from qgis.core import *
from PyQt4.QtCore import QSize

qgis_app, ms, ct = None, None, None

def init_rendering():
    """ load project, setup map parameters """
    global qgis_app, ms, ct
    qgis_app = QgsApplication([], False, qgis_path)
    qgis_app.initQgis()
    QgsProject.instance().setFileName(project_file)
    QgsProject.instance().read()
    ms = QgsMapSettings()
    ms.setOutputSize(QSize(256,256))
    ms.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3857"))
    ms.setCrsTransformEnabled(True)
    ms.setLayers(QgsProject.instance().layerTreeRoot().findLayerIds())
    ct = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), QgsCoordinateReferenceSystem("EPSG:3857"))

def num2deg(xtile, ytile, zoom):
    """ conversion of X,Y + zoom to lat/lon coordinates - from OSM wiki """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def make_tile(z,x,y, tile_filename):
    """ render the tile to given filename """
    top,left = num2deg(x,y,z)
    bottom,right = num2deg(x+1,y+1,z)
    ms.setExtent(QgsRectangle(ct.transform(left,bottom),ct.transform(right,top)))
    job = QgsMapRendererSequentialJob(ms)
    job.start()
    job.waitForFinished()
    job.renderedImage().save(tile_filename)


# ----- Flask part ----- #

from flask import Flask, Response
app = Flask(__name__)

@app.route("/")
def index_page():
    return index_html

@app.route("/<int:z>/<int:x>/<int:y>/")
def get_tile(z,x,y):
    tile_filename = tile_path+"/%d/%d/%d.png" % (z,x,y)
    if not os.path.exists(tile_filename):
      if not os.path.exists(os.path.dirname(tile_filename)):
        os.makedirs(os.path.dirname(tile_filename))
      make_tile(z,x,y, tile_filename)
    return Response( open(tile_filename).read(), mimetype='image/png')

# wipe out the tile path (if it exsits)
if os.path.exists(tile_path):
  import shutil; shutil.rmtree(tile_path)
os.makedirs(tile_path)

init_rendering()

if __name__ == "__main__":
    app.run(debug=True)
