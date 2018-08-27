from flask import Flask, render_template, request
from gevent.wsgi import WSGIServer

import numpy as numpy
import os
from requete import *


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():

	return render_template('index.html')


@app.route('/getUserData', methods=['GET'])
def getUserData():

	return render_template('getUserData.html')


@app.route('/analyseUserData', methods=['GET', 'POST'])
def analyseUserData():

	if request.method == 'POST':

		savePath = save_csv()
		plotUrl =  getHourlyAnalysis(savePath)

		return render_template('analyseUserData.html', csvpath = savePath, ploturl = plotUrl)


	return render_template('getUserData.html')


@app.route('/importConsoData', methods=['GET'])
def importConsoData():

	return render_template('importConsoData.html')


@app.route('/analyseConsoData', methods=['GET', 'POST'])
def analyseConsoData():

	if request.method == 'POST':

		saveCsvPath = save_json()
		leakage, jsonUrl = getLeakageAnalysis(saveCsvPath)

		return render_template('analyseConsoData.html', leakage = leakage, jsonUrl =jsonUrl )



	return render_template('importConsoData.html')



if __name__ == "__main__":
    http_server = WSGIServer(('', 8080), app)
    http_server.serve_forever()