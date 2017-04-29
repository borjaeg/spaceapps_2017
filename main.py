# coding: utf-8
from flask import Flask, Response, json, render_template
import psycopg2
import osgeo.ogr
from osgeo import gdal
import os
import numpy as np
from skimage import io, exposure
from scipy import ndimage
from scipy.misc import imsave


app = Flask(__name__)

@app.route("/")
def hello():

    return render_template("index.html")


@app.route("/get_water_by_geom/<string:x_min>/<string:y_min>/<string:x_max>/<string:y_max>")
def get_rivers_by_geometry(x_min, y_min, x_max, y_max):
    connection = psycopg2.connect(database="postgis_in_action",user="b3j90", password="")
    cursor = connection.cursor()
    query = """
    SELECT row_to_json(fc)
                    FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
                    FROM (SELECT 'Feature' As type, ST_AsgeoJSON(geom)::json As geometry
                            , row_to_json((SELECT l FROM (SELECT name) As l)) As properties
                    FROM public.water As lg
                          WHERE geom && ST_MakeEnvelope(%xmin, %ymin, %xmax, %ymax, 4326)
                          AND name IS NOT null
                         ) As f )  As fc
            """.replace('%xmin', x_min).replace('%ymin', y_min).replace('%xmax', x_max).replace('%ymax', y_max)

    app.logger.info(query)
            
    cursor.execute(query)

    for l in cursor:
        data = l[0]

    connection.close()

    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')

    return resp


@app.route("/get_giovanni_precipitation_data/<string:x_min>/<string:y_min>/<string:x_max>/<string:y_max>")
def get_giovanni_precipitation_data_2(x_min, y_min, x_max, y_max):
    connection = psycopg2.connect(database="postgis_in_action",user="b3j90", password="")
    cursor = connection.cursor()
    vsipath = '/tmp/from_postgis.png'

    cursor.execute("SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';")
    cursor.execute("""
                    SELECT ST_AsPNG(ST_Clip(rast, 
                    ST_MakeEnvelope(%xmin, %ymin, 
                    %xmax, %ymax, 4326)))
                    from gpm_precipitation
                    """.replace('%xmin', x_min).replace('%ymin', y_min).replace('%xmax', x_max).replace('%ymax', y_max))
                                
    newFile = open(vsipath, "wb")
    newFileByteArray = bytearray(bytes(cursor.fetchone()[0]))
    newFile.write(newFileByteArray)
    newFile.close()

    tif = gdal.Open(vsipath)
    tifArray = tif.ReadAsArray()
    tifArray = np.swapaxes(tifArray,0,2)
    tifArray = np.swapaxes(tifArray,0,1)
    img_eq = exposure.equalize_hist(tifArray)
    imsave('/tmp/rgb_gradient.png', img_eq)
    with open("/tmp/rgb_gradient.png", "rb") as imageFile:
        f = imageFile.read()
        b = bytearray(f)

    resp = Response(b, status=200, mimetype='image/png')
    connection.close()

    return resp


if __name__ == "__main__":
    app.run(debug=True)
