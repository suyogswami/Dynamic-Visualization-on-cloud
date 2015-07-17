
from __future__ import unicode_literals
import googlemaps
from flask import Flask
from flask import request, abort
from flask import render_template
from time import gmtime
import timeit
from datetime import datetime
import csv
import os
from flask import Flask, request, send_from_directory
app = Flask(__name__)

app = Flask(__name__, static_url_path='')

@app.route('/templates/<path:path>')
def send_js(path):
    return send_from_directory('templates', path)

@app.route('/', methods=['POST', 'GET'])
def welcome2():
    if request.method == "GET":
        return render_template('table.html')

@app.route('/display', methods=['POST', 'GET'])
def welcome():
        source = request.form.get('source')
        dest = request.form.get('dest')
        mode = request.form.get('mode').lower()
        cli=googlemaps.Client(key="")
        dir=cli.directions(source,dest,mode=mode,departure_time= datetime.now())
        #print(dir)
        dir_encoded = dir[0].get('overview_polyline').get('points')
        duration=dir[0].get('legs')[0].get('duration').get('text')
        print (dir[0].get('legs')[0].get('duration').get('text'))
        dir_list=[]
        for i in range(len(dir[0].get('legs')[0].get('steps'))):
            direction=dir[0].get('legs')[0].get('steps')[i].get('html_instructions')
            direction=direction.replace("<b>","")
            direction=direction.replace("</b>","")
            direction=direction.replace('<div style="font-size:0.9em">',"")
            direction=direction.replace('</div>',"")
            dir_list.append(direction)
        #print(dir_list)
        latlngs = decode_line(dir_encoded)
        path = "C:/PA10/templates/goodgeocode1.csv"
        with open(path, 'w',newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(['Latitude','Longitude','Time','Id'])
            j=1
            for latlng in latlngs:
                if j==1:
                    id=source
                elif j==len(latlngs):
                    id=dest
                else:
                    id="Along route"
                spamwriter.writerow([(latlng[0]),(latlng[1]),j,'route 1',id])
                j=j+1
        csvfile.close()

        csv1 = open(path,'r')
        geo = csv.reader(csv1)
        rows = list(geo)
        totalrows = len(rows)
        #print (totalrows)
        template =     """
        { "type": "Feature", "properties": { "latitude": %s, "longitude": %s, "time": %s, "id": %s, "name":%s }, "geometry": { "type": "Point", "coordinates": [ %s, %s ] } },"""

        template1 =    """
        { "type": "Feature", "properties": { "latitude": %s, "longitude": %s, "time": %s, "id": %s, "name":%s }, "geometry": { "type": "Point", "coordinates": [ %s, %s ] } }"""
        # the head of the geojson file
        output = """
        {
        "type": "FeatureCollection",
        "number":%s,
        "features": [ """ %(totalrows-2)
        # loop through the csv by row skipping the first
        iter = 0

        csv1 = open(path,'r')
        geojs = csv.reader(csv1)

        for row in geojs:
            iter += 1
            if iter >= 2 and iter != totalrows:
                lat = row[0]
                lon = row[1]
                time = row[2]
                id = row[3]
                id = "\""+id+ "\" "
                name = row[4]
                name = "\""+name+ "\" "
                output += template % (row[0],row[1],row[2],id,name,row[1],row[0])
            elif iter == totalrows:
                lat = row[0]
                lon = row[1]
                time = row[2]
                id = row[3]
                id = "\""+id+ "\" "
                name = row[4]
                name = "\""+name+ "\" "
                output += template1% (row[0],row[1],row[2],id,name,row[1],row[0])

        #print (output)
        # the tail of the geojson file
        output +="""
        ]
        }
            """

        # opens an geoJSON file to write the output to
        path2 = "C:/PA10/templates/output1.geojson"
        outFileHandle = open(path2, "w")
        outFileHandle.write(output)
        outFileHandle.close()
        return render_template('leafletmap.html',duration=duration,dir_list=dir_list,source=source, dest=dest)



def decode_line(encoded):

    """Decodes a polyline that was encoded using the Google Maps method.

    See http://code.google.com/apis/maps/documentation/polylinealgorithm.html

    This is a straightforward Python port of Mark McClure's JavaScript polyline decoder
    (http://facstaff.unca.edu/mcmcclur/GoogleMaps/EncodePolyline/decode.js)
    and Peter Chng's PHP polyline decode
    (http://unitstep.net/blog/2008/08/02/decoding-google-maps-encoded-polylines-using-php/)
    """

    encoded_len = len(encoded)
    index = 0
    array = []
    lat = 0
    lng = 0

    while index < encoded_len:

        b = 0
        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat

        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng

        array.append((lat * 1e-5, lng * 1e-5))

    return array

if __name__ == '__main__':
        app.debug = True
        app.run('0.0.0.0')
