#!/usr/bin/python
#-*-coding: utf-8 -*-
import math
from flask import Flask, render_template, request, json, jsonify
from jinja2 import Template
import GeoData


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
     <table class='result'>
     <tr>
        <th class='result'>Наименование</td>
        <th class='result'>Км+м</td>
        <th class='result'>Положение</td>
        <th class='result'>Покрытие</td>
        <th class='result'>Техническое состояние</td>
     </tr>

     {% for EXIT in EXITS %}
     <tr>
        <td class='result'>{{ EXIT.name }}</td>
        <td class='result'>{{ EXIT.position }}</td>
        <td class='result'>{{ EXIT.transverse }}</td>
        <td class='result'>{{ EXIT.material }}</td>
        <td class='result'>{{ EXIT.tech_condition }}</td>
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
     return jsonify(result={'Table': table, 'Dat': Dat, 'Rcode': Rcode, 'Name': CurrentRoad.name(Rcode), 'Begin_km': GeoData.km_to_kmm(Begin_km), 'End_km': GeoData.km_to_kmm(End_km) })
     #return jsonify(result={'Dat': Dat, 'Rcode': Rcode, 'Name': CurrentRoad.name(Rcode) })

@app.route('/roadlength')
def roadlength():
     Rcode = request.args.get('Rcode')
     RoadLength = CurrentRoad.RoadLength(Rcode)
     return jsonify({'RoadLength': RoadLength})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
