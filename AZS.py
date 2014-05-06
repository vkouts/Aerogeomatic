#!/usr/bin/python
#-*-coding: utf-8 -*-
from flask import Flask, render_template, request, json, jsonify
import GeoData

app = Flask(__name__)

CurrentRoad = GeoData.Road()

@app.route('/')
def input_data():
    Road1 = GeoData.Road()
    RoadsList = Road1.List()
    return render_template('input.html',RoadsList=RoadsList)

@app.route('/result', methods = ['GET', 'POST'])
def result():
     Dat = request.args.get('Date')
     Rcode = request.args.get('Rcode')
     #print request.json
     #print request.json['Date']
     #print "gggggg " + str(jsonify(result=request.json['Date']))
     #return jsonify(result=request.json['Date'])
     #print Dat
     #print Rcode
     return jsonify(result={'Dat': Dat, 'Rcode': Rcode, 'Test': 'testetete' })

@app.route('/roadlength')
def roadlength():
     Rcode = request.args.get('Rcode')
     RoadLength = CurrentRoad.length(Rcode)
     return jsonify({'RoadLength': RoadLength})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
