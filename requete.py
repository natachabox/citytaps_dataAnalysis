from flask import request, make_response, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import base64 
import io
import json

def save_csv():

    if request.method == 'POST':

        # Get the file from post request
        f = request.files['csv']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        #get the file url
        def change_path(path):
            return path.replace("\\", "/")

        correct_path = change_path(file_path)
        
        return  correct_path


def getHourlyAnalysis(path):

	#create dataframe from csv
	df = pd.read_csv(path)
	df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
	df = df.set_index('timestamp')
	#resample one ourly basis 'H', and grouby hour and take average
	hourdf = df.resample('H').sum()
	hourdfavg = hourdf.groupby(hourdf.index.hour).mean()

	# create plot
	plt.rcParams['figure.figsize'] = 20,5
	plt.xlabel('Hour', fontsize=16)
	plt.ylabel('Consumption in Liters', fontsize=16)
	plt.title('Barchart - Mean consumption per Hour',fontsize=20)
	plt.bar(hourdfavg.index, hourdfavg['consumption'])

	#save plot
	url = "static/images/userplot.png"
	plt.savefig(url)

	return url



def save_json():

    if request.method == 'POST':

        # Get the file from post request
        f = request.files['json']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        def change_path(path):
            return path.replace("\\", "/")

        correct_path = change_path(file_path)
        
        return  correct_path


def getLeakageAnalysis(path):

	with open(path, encoding='utf-8') as data_file:
		data = json.loads(data_file.read())
	df = pd.DataFrame(data)
	# creating column with average consommation for 3 last hours
	df['consoRolling'] = df['consommation'].rolling(window=3).mean()
	# creating column to store potential leakage for test
	df['leakage'] = 0
	for i in range(2, len(df)):
		df['leakage'][i] = (df['consommation'][i] >= 15 and df['consommation'][i-1] >= 15 and df['consommation'][i-2] >= 15)
   
   	#storing potential leak lines 
	potentialLeak = []
	x = 0
	while x < (len(df)):
		if df['leakage'][x]:
			n = x
			i = 0
			while df['leakage'][n+1]:

				n+=1
				x+=1
				i+= 1

			oneLeak= df.iloc[x-2-i:n+1].drop(columns=['consoRolling', 'leakage'])
			leakDict = oneLeak.to_dict('records')
			for j in range(len(leakDict)):
				leakDict[j] = { k:int(v) for k,v in leakDict[j].items() }

			potentialLeak.append(leakDict)

		x += 1

	# create dictionary of lines to save
	#leakToSave = pd.Series(potentialLeak).to_json(orient='values')
	jsonUrl = 'output/data_leakage_natacha.json' 
	with open(jsonUrl, 'w') as outfile:  
		json.dump(potentialLeak, outfile, indent=1)

	return potentialLeak, jsonUrl

