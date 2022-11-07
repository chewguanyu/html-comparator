#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 10:48:40 2022

@author: intern
"""

from flask import Flask
from helper_functions import *

app = Flask(__name__)

from flask import Flask,render_template,request
 
@app.route('/')
def form():
    return render_template('form.html')
 
@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files
        
        #Turn file contents into strings and get rid of binary indicators
        a = str(f.getlist('File')[0].read()[:-1])[2:-1]
        b = str(f.getlist('File')[1].read()[:-1])[2:-1]
        
        #Turn files into soups
        soup1 = BeautifulSoup(a, 'html.parser')
        soup2 = BeautifulSoup(b, 'html.parser')
        
        ##Feature extraction
        features = extract_features(soup1, soup2)
        
        #Transform features for summary
        #When needed, define directory of 0_scaler.pkl in path
        path="iterations/3/"
        summary = summarize(features, path)
        summary = summary.split('\n')

        #Transform features for prediction
        X = scale(features, path)

        #Prediction
        y = predict(X, path)
        
        if y==1:
            prediction = "One page is a phish of the other."
        else:
            prediction = "Neither page is a phish of the other."
            
        result = (f"<p>Prediction: {prediction}</p>"
                  f"<p>{summary[0]}<br>"
                  f"Comparison of webpages found in the submitted source codes.</p>"
                  f"<p>{summary[1]}<br>"
                  f"Comparison of image storage used by the submitted source codes.</p>"
                  f"<p>{summary[2]}<br>"
                  f"Comparison of words found in the submitted source codes.</p>"
                  f"<p>{summary[3]}<br>"
                  f"Comparison of styles used by the submitted source codes.</p>"
                  f"<p>{summary[4]}<br>"
                  f"Comparison of external resources used by the submitted source codes.</p>")
        
    return result
        

app.run(host='localhost', port=5000)
