#!/usr/bin/python
#-*-coding: utf-8 -*-
import math
from flask import Flask, render_template, request, json, jsonify
from jinja2 import Template

import GeoData

def km_to_kmm(km_):
    km_ = float(km_)
    km = int(km_)
    m = str(int((km_ - math.trunc(km_))*1000))
    if len(m) == 1:
       m = '00' + m
    if len(m) == 2:
       m = '0' + m
    return "%s+%s"%(str(km),m)

app = Flask(__name__)
app.debug = True

CurrentRoad = GeoData.Road()

@app.route('/')
def input_data():
    RoadsList = CurrentRoad.RoadList()
    return render_template('input.html',RoadsList=RoadsList)

@app.route('/result', methods = ['GET', 'POST'])
def result():
     Dat = request.args.get('Date')
     Rcode = request.args.get('Rcode')
     Begin_km = request.args.get('Begin_km')
     End_km = request.args.get('End_km')


     CurrentAZS = CurrentRoad.RoadAZS(Rcode, Begin_km, End_km, Dat)
     CurrentEXITS = CurrentRoad.RoadExits(CurrentAZS, Begin_km, End_km, Dat)

     table_ = Template("""
     <table>
     <tr>
        <td>Наименование</td>
        <td>Км+м</td>
        <td>Положение</td>
        <td>Покрытие</td>
        <td>Техническое состояние</td>
     </tr>

     {% for EXIT in EXITS %}
     <tr>
        <td>{{ EXIT.name }}</td>
        <td>{{ EXIT.position }}</td>
        <td>{{ EXIT.transverse }}</td>
        <td>{{ EXIT.material }}</td>
        <td>{{ EXIT.tech_condition }}</td>
     </tr>
     {% endfor %}
     </table>
     """.decode('utf-8'))
     table = table_.render(EXITS=CurrentEXITS)


     #print request.json
     #print request.json['Date']
     #print "gggggg " + str(jsonify(result=request.json['Date']))
     #return jsonify(result=request.json['Date'])
     #print Dat
     #print Rcode
     #print km_to_kmm(Begin_km)
     return jsonify(result={'Table': table, 'Dat': Dat, 'Rcode': Rcode, 'Name': CurrentRoad.name(Rcode), 'Begin_km': km_to_kmm(Begin_km), 'End_km': km_to_kmm(End_km) })
     #return jsonify(result={'Dat': Dat, 'Rcode': Rcode, 'Name': CurrentRoad.name(Rcode) })

@app.route('/roadlength')
def roadlength():
     Rcode = request.args.get('Rcode')
     RoadLength = CurrentRoad.RoadLength(Rcode)
     return jsonify({'RoadLength': RoadLength})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
