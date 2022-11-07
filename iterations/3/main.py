#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from helper_functions import *
import argparse
import warnings
warnings.filterwarnings("ignore")

#Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html1", help='path containing 1st .html', required = True)
    parser.add_argument("--html2", help='path containing 2nd .html', required = True)
    opts = parser.parse_args()
    
    #Path of relevant iteration
    path = ""
    
    #Get soups
    soup1, soup2 = get_soups_filepath(opts.html1, opts.html2)
    
    #Feature extraction
    features = extract_features(soup1, soup2)
    
    #Transform features for summary
    summary = summarize(features, path)

    #Transform features for prediction
    X = scale(features, path)

    #Prediction
    y = predict(X, path)
    
    print('\n')
    
    if y==1:
        print("Prediction: One page is a phish of the other.")
    else:
        print("Prediction: Neither page is a phish of the other.")
    
    print(summary+'\n')
