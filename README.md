# QGIS tile server

This is an attempt to create a working map tile server based on QGIS map renderer for use in web maps. As a bonus, the tile server also serves home page with a map based on Leaflet. All that in about 100 lines of code!

Requirements:

* QGIS  (for rendering)
* Flask (for server side)

How to use:

* edit paths in the header of tileserver.py file
* run ```python tileserver.py```
* in your web browser, go to ```http://localhost:5000/```
