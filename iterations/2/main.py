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
    """Gets words from list of tags
    """
        
    #List of tags to check
    contentlist = ["title", "h1", "h2", "h3", "h4"
              "h5", "h6", "p", "meta"]
    
    for tag in contentlist:
        
        #Get info from tags
        if tag != "meta":
            raw_list = get_contents(tag, soup)
            
            #Flatten lists
            raw_list = [i for sublist in raw_list if sublist !=None for i in sublist if i != None]
        
        else:
            raw_list = get_attributes(tag, "content", soup)
    
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

def process_word_list(list1,list2):
    """Consider only uncommon words beginning with capitals
    and links.
    """
    common = ['Get','Para','Your','You','Sign','Online','All','Learn','IE=edge','The','None']   
    #Shorten lists
    flist1 = [n for n in list1 if n[0].isupper() or n[:4] == "http" if len(n)>2 and len(n)<200 if n not in common]
    flist2 = [n for n in list2 if n[0].isupper() or n[:4] == "http" if len(n)>2 and len(n)<200 if n not in common]
  
    return flist1, flist2

def compare_list_length(list1, list2):
    """Compares list lengths.
    """
    #Define longer and shorter lists
    if len(list2) > len(list1):
        longer = list2
        shorter = list1
    else:
        longer = list1
        shorter = list2
    return longer, shorter

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
    """ ratio and count of overall and filtered words 
    and the relative filtered word list lengths.
    """    
    
    list1 = get_words(soup1)
    list2 = get_words(soup2)
    flist1,flist2 = process_word_list(list1, list2)
    longer,shorter = compare_list_length(flist1, flist2)
    
    if len(longer) == 0:
        word_list_length = 0
    else:
        word_list_length = len(shorter)/len(longer)
     
    if min(len(list2),len(list1)) == 0:
        overall_ratio = 0
        overall_count = 0
        filtered_word_ratio = 0
        filtered_word_count = 0
        
    else:
        overall_ratio, overall_count = get_rc(list1, list2)

        if min(len(flist2),len(flist1)) == 0:
            filtered_word_ratio = 0
            filtered_word_count = 0
        else:
            filtered_word_ratio,filtered_word_count = get_rc(flist1,flist2)
        
    return overall_ratio, overall_count,\
            filtered_word_ratio, filtered_word_count,\
            word_list_length

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
    overall_word_ratio, overall_word_count,\
    filtered_word_ratio, filtered_word_count,\
    word_list_length,\
    = get_word_data(soup1, soup2)
    
    #meta conent ratio
    meta_content_ratio = get_meta_content_ratio(soup1, soup2)
    
    feature_dict = {"a_no_ratio":a_no_ratio,
                    "img_src_ratio":img_src_ratio,
                    "link_href_ratio":link_href_ratio,
                    "link_href_count":link_href_count,
                    "div_class_ratio":div_class_ratio,
                    "div_class_count":div_class_count,
                    "word_ratio":overall_word_ratio,
                    "word_count":overall_word_count,
                    "meta_content_ratio":meta_content_ratio,
                    "filtered_word_ratio":filtered_word_ratio,
                    "filtered_word_count":filtered_word_count,
                    "word_list_length":word_list_length}
    
    features = pd.DataFrame(feature_dict, index=[0])
    
    return features

#This function loads the model and gives a prediction
def predict(features):
    """Load model and make a prediction
    """
    model = pickle.load(open("htmlc.pkl", 'rb'))
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