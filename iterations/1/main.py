#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 11:05:36 2022

@author: intern
"""
import argparse
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import warnings
warnings.filterwarnings("ignore")

#Functions
#These functions support feature extraction functions
def get_soups(path1, path2):
    """Gets html soups
    """
    with open(path1, "r") as f:
        soup1 = f.read()
    with open(path2, "r") as f:
        soup2 = f.read()
    soup1 = BeautifulSoup(soup1,"html.parser")
    soup2 = BeautifulSoup(soup2,"html.parser")
    return soup1, soup2

def get_attributes(tag, attr, soup):
    """Gets attributes for a given tag in soup
    """
    attr_list = [x.get(attr) for x in soup.find_all(tag)]
    return attr_list

def get_contents(tag, soup):
    """Gets contents for a given tag in soup
    """
    content_list = [x.contents for x in soup.find_all(tag)]
    return content_list 

def get_words(soup):
    """Gets words from p tags
    """
        
    #Get p tag contents
    raw_list = get_contents("p",soup)
    
    #Flatten lists
    raw_list = [i for sublist in raw_list for i in sublist]
    
    word_list = []
    for i in raw_list:
        sentence = str(i)
        #Strip non-word portions
        tag_count = sentence.count(">")/2
        sentence = sentence.split(">")[int(tag_count)]
        sentence = sentence.split("<")[0]
        sentence = sentence.replace("\n","")
        sentence = sentence.replace("\t","")
        sentence = sentence.replace("\xa0","")
        #Append words to single list
        words = sentence.split(" ")
        for word in words:
            if len(word)>0:
                word_list.append(word)
    return word_list

def get_rc(list1, list2):
    """Gets ratio and count of items common in both lists
    """
    count1 = 0
    for i in list1:
        if i in list2:
            count1+=1
    count2 = 0
    for i in list2:
        if i in list1:
            count2+=1
    count = max(count1,count2)
    ratio = count/min(len(list1),len(list2))
    return ratio, count

#These functions extract features
def get_a_no_ratio(soup1, soup2):
    """Gets ratio of anchor tag href counts
    """
    len1 = len(get_attributes("a","href", soup1))
    len2 = len(get_attributes("a", "href", soup2))
    if max(len1,len2) == 0:
        ratio = 0
    else:    
        ratio = min(len1,len2)/max(len1,len2)
    return ratio

def get_img_src_ratio(soup1, soup2):
    """img src ratio between 2 soups
    """
    
    #Extract img src
    list1 = get_attributes("img","src", soup1)
    list2 = get_attributes("img","src", soup2)

    #Get img file name while stripping URL, query terms, and whitespaces
    list1 = [i.split("/")[-1].replace(" ","") for i in list1 if i is not None]
    list1 = [i.split("?")[0] for i in list1]
    list2 = [i.split("/")[-1].replace(" ","") for i in list2 if i is not None]
    list2 = [i.split("?")[0] for i in list2]
    
    #If no img src
    if min(len(list1),len(list2)) == 0:
        ratio = 0
        
    #Get ratio
    else:
        ratio, count = get_rc(list1, list2)
        
    return ratio

def get_link_href_data(soup1, soup2):
    """link href ratio and count between 2 soups
    """
    
    #Extract link href
    list1 = get_attributes("link","href",soup1)
    list2 = get_attributes("link","href",soup2)
    
    #Get file name while stripping URL, query terms, whitespaces, and .xhtml
    list1 = [i.split("/")[-1].replace(" ","") for i in list1 if i is not None]
    list1 = [i.split("?")[0] for i in list1]
    list1 = [i.replace(".xhtml","") for i in list1]
    list2 = [i.split("/")[-1].replace(" ","") for i in list2 if i is not None]
    list2 = [i.split("?")[0] for i in list2]
    list2 = [i.replace(".xhtml","") for i in list2]
    
    #If no link href
    if min(len(list1),len(list2)) == 0:
        ratio = 0
        count = 0

    else:
        ratio, count = get_rc(list1, list2)
    
    return ratio, count

def get_div_class_data(soup1, soup2):
    """div class ratio and count between 2 soups
    """
    
    #Extract div class
    list1 = get_attributes("div","class",soup1)
    list2 = get_attributes("div","class",soup2)
    

    list1 = [i for i in list1 if i is not None]
    list2 = [i for i in list2 if i is not None]
    
    #If no div class
    if min(len(list1),len(list2)) == 0:
        ratio = 0
        count = 0

    else:
        ratio, count = get_rc(list1, list2)
    
    return ratio, count

def get_word_data(soup1, soup2):
    """ ratio and count of common words
    """    
    
    list1 = get_words(soup1)
    list2 = get_words(soup2)
    
    
    if min(len(list2),len(list1)) == 0:
        ratio = 0
        count = 0
    else:
        ratio, count = get_rc(list1, list2)
            
    return ratio, count

def get_meta_content_ratio(soup1, soup2):
    """ratio of meta content between 2 soups
    """
    list1 = get_attributes("meta","content",soup1)
    list2 = get_attributes("meta","content",soup2)
    
    #Get meta content
    list1 = [i for i in list1 if i is not None]
    list2 = [i for i in list2 if i is not None]
    
    #If suspected phish has no meta content
    if min(len(list1),len(list2)) == 0:
        ratio = 0

    else:
        ratio, count = get_rc(list1, list2)
        
    return ratio

def extract_features(path1, path2):
    """Extracts features given 2 soups
    """
    #gets soups from paths
    soup1, soup2 = get_soups(path1, path2)
    
    #anchor tag number ratio
    a_no_ratio = get_a_no_ratio(soup1, soup2)
    
    #img src ratio
    img_src_ratio = get_img_src_ratio(soup1, soup2)
    
    #link href ratio and count
    link_href_ratio, link_href_count = get_link_href_data(soup1, soup2)
    
    #div class ratio and count
    div_class_ratio, div_class_count = get_div_class_data(soup1, soup2)
    
    #word ratio and count
    word_ratio, word_count = get_word_data(soup1, soup2)
    
    #meta conent ratio
    meta_content_ratio = get_meta_content_ratio(soup1, soup2)
    
    feature_dict = {"a_no_ratio":a_no_ratio,
                    "img_src_ratio":img_src_ratio,
                    "link_href_ratio":link_href_ratio,
                    "link_href_count":link_href_count,
                    "div_class_ratio":div_class_ratio,
                    "div_class_count":div_class_count,
                    "word_ratio":word_ratio,
                    "word_count":word_count,
                    "meta_content_ratio":meta_content_ratio}
    
    features = pd.DataFrame(feature_dict, index=[0])
    
    return features

#This function loads the model and gives a prediction
def predict(features):
    """Load model and make a prediction
    """
    model = pickle.load(open("iterations/1/htmlc.pkl", 'rb'))
    y = model.predict(features)
    
    return y

#Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html1", help='path containing 1st .html', required = True)
    parser.add_argument("--html2", help='path containing 2nd .html', required = True)
    opts = parser.parse_args()
    
    #Feature extraction
    X = extract_features(opts.html1, opts.html2)
      
    #Prediction
    y = predict(X)
    
    if y==1:
        print("phish")
    else:
        print("not phish")
