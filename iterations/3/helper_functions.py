#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 11:14:43 2022

@author: intern
"""
from bs4 import BeautifulSoup
import pandas as pd
from copy import deepcopy
import pickle

#Functions
#These functions support feature extraction functions
def get_soups_filepath(path1, path2):
    """Gets html soups given file paths
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

def get_words(raw_list):
    """Gets words from a list of raw content
    """
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

def process_word_tag(list1, list2, to_extend1, to_extend2):
    """Gets ratio and count and stores content for other aggregated features
    e.g. Words in h1 tag should be also included in overall and filtered
    word features
    """
    list1 = get_words(list1)
    list2 = get_words(list2)
    to_extend1.extend(list1)
    to_extend2.extend(list2)
    retain1 = deepcopy(list1)
    retain2 = deepcopy(list2)
    list1 = [i.lower for i in list1]
    list2 = [i.lower for i in list2]
    ratio, count = get_rc(list1,list2)
    return ratio, count, retain1, retain2

def process_word_list(list1,list2):
    """Consider only uncommon words beginning with capitals
    and links.
    """
    common = ['Get','Para','Your','You','Sign','Online','All','Learn','IE=edge','The','None']   
    #Shorten lists
    flist1 = [n for n in list1 if n[0].isupper() or n[:4] == "http" if len(n)>2 and len(n)<200 if n not in common]
    flist2 = [n for n in list2 if n[0].isupper() or n[:4] == "http" if len(n)>2 and len(n)<200 if n not in common]
  
    return flist1, flist2

def get_stylelist(soup):
    """gets entire div and style tags from soup
    """
    stylelist = []
    divs = [str(i) for i in soup.find_all('div') if i is not None]
    styles = [str(i) for i in soup.find_all('style') if i is not None]
    stylelist.extend(divs)
    stylelist.extend(styles)
    return stylelist

def all_files(i):
    """find all file names given string
    """
    files = []
    start = 0
    while start != -1:
    
        #Look for file name extensions bounded by " in html source code
        #e.g. .svg" or .png" or .css" or .xhtml", etc
        start = i.find('.')
        #Initialize search variables for start of file name
        a = -1
        b = -1
    
        #Check for distance between . and "
        #File extensions are generally 3 to 6 characters or below including '.'
        #e.g. .tz or .htmlx
        if '"' in i[start+1:start+6]:
            length = i[start:].find('"')
            fileend = start+length
    
            #Additional screen in case . occurs soon before "
            check = i[start+1:fileend]
            #non-filename codes usually end with ) or ;
            proceed = True
            exclude = [')',";",'.']
            for e in exclude:
                if e in check:
                    proceed = False
        #Look for start of file name
            if proceed:
                a = i[:start].rfind("/")
                b = i[:start].rfind('"')        
                #If start of file name found
                if a!=-1 or b!=-1:
                    filestart = max(a,b)+1
                    filename = i[filestart:fileend]
                    if filename!='di':
                        files.append(filename)
            #Prepare for next iteration        
            i = i[start+1:]
        else:
            i = i[start+1:]
    return files

def files_from_lists(stylelist):
    """looks for filenames given a list of strings
    """
    files = []
    for i in stylelist:
        subfiles = all_files(i)
        if len(subfiles)!=0:
            files.extend(subfiles)
    return files

def flatten_list(fatlist):
    """Flattens list of lists
    """
    flatlist = \
        [i for sublist in fatlist if sublist !=None for i in sublist if i != None]
    
    return flatlist

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

def get_rc(list1, list2):
    """Gets ratio and count of items common in both lists
    """
    longer, shorter = compare_list_length(list1, list2)
    if len(shorter) == 0:
        count = 0
        ratio = 0
    else:
        count = 0
        for i in longer:
            if i in shorter:
                count+=1
        ratio = count/len(shorter)
    return ratio, count

def get_rc_url(list1, list2):
    """ratio and count of list1 (substrings) presence in list2 (strings)
    """
    count = 0
    ratio = 0
    list1 = [i for i in list1 if i is not None]
    list2 = [i for i in list2 if i is not None]
    if len(list1) != 0:
        for i in list1:
            for j in list2:
                if i in j:
                    count+=1
                    break
        ratio = count/len(list1)
    return ratio, count

def get_2LD(url):
    """Gets 2nd Level domain given a URL
    """
    try:
        highlevel = url.split("/")[2]
        domain = highlevel.split(".")
        if len(domain[-1]) == 2:
            if len(domain[-2]) == 3:
                result = domain[-3]
            else:
                result = domain[-2]
        else:
            result = domain[-2]
    
    except IndexError:
        result = None
    return result

def filter_url(list1,list2):
    """Filters raw url lists for common terms and strips them to 2LD
    """
    common = ['w3','co','facebook','www','google','twitter','googletagmanager','t','schema',
         'youtube','com','instagram','google-analytics','bb','googleapis','apple','linkedin','w','bt','doubleclick',
         'gstatic','ne','b','fi','go','img','nfl','ont','tiktok','post','yimg','coinmarketcap','amazonaws','irs']
    list1 = [i for i in list1 if i is not None]
    list2 = [i for i in list2 if i is not None]
    dlist1 = [get_2LD(i) for i in list1 if get_2LD(i) is not None and get_2LD(i) not in common]
    dlist2 = [get_2LD(i) for i in list2 if get_2LD(i) is not None and get_2LD(i) not in common]
    return(dlist1,dlist2)

#These functions extract raw strings
def raw_urls(soup1,soup2):
    """gets lists that may contain urls
    """
    urls = {}
    urls['alist1'] = get_attributes("a","href",soup1)
    urls['alist2'] = get_attributes("a","href",soup2)
    urls['linklist1'] = get_attributes("link","href",soup1)
    urls['linklist2'] = get_attributes("link","href",soup2)
    urls['all1'] = str(soup1)
    urls['all2'] = str(soup2)
    return urls

def raw_words(soup1,soup2):
    """gets lists of raw words from certain html tags and attributes
    """
    words = {}
    words['metacontent1'] = get_attributes('meta', 'content', soup1)
    words['metacontent2'] = get_attributes('meta', 'content', soup2)
    words['title1'] = flatten_list(get_contents('title',soup1))
    words['title2'] = flatten_list(get_contents('title',soup2))
    words['h11'] = flatten_list(get_contents('h1',soup1))
    words['h12'] = flatten_list(get_contents('h1',soup2))
    words['h21'] = flatten_list(get_contents('h2',soup1))
    words['h22'] = flatten_list(get_contents('h2',soup2))
    words['h31'] = flatten_list(get_contents('h3',soup1))
    words['h32'] = flatten_list(get_contents('h3',soup2))
    words['h41'] = flatten_list(get_contents('h4',soup1))
    words['h42'] = flatten_list(get_contents('h4',soup2))
    words['h51'] = flatten_list(get_contents('h5',soup1))
    words['h52'] = flatten_list(get_contents('h5',soup2))
    words['h61'] = flatten_list(get_contents('h6',soup1))
    words['h62'] = flatten_list(get_contents('h6',soup2))
    words['p1'] = flatten_list(get_contents('p',soup1))
    words['p2'] = flatten_list(get_contents('p',soup2))
    words['div1'] = flatten_list(get_contents('div',soup1))
    words['div2'] = flatten_list(get_contents('div',soup2))
    words['a1'] = flatten_list(get_contents('a',soup1))
    words['a2'] = flatten_list(get_contents('a',soup2))
    words['button1'] = flatten_list(get_contents('button',soup1))
    words['button2'] = flatten_list(get_contents('button',soup2))
    
    return words

#These functions extract features
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
    
    #Get ratio
    ratio,_ = get_rc(list1,list2)
        
    return ratio

def get_URL_features(raw):
    """Takes in dictionary of raw data and returns dictionary of features
    """
    url_features = {}
    
    #a_no_ratio
    longer, shorter = compare_list_length(raw['alist1'],raw['alist2'])
    if len(shorter) == 0:
        url_features['a_no_ratio'] = 0
    else:
        url_features['a_no_ratio'] = len(shorter)/len(longer)
    
    #2ld_a_href_ratio and 2ld_a_href_count
    #Get second level domains
    dlist1 = [get_2LD(i) for i in raw["alist1"] if i is not None]
    dlist2 = [get_2LD(i) for i in raw["alist2"] if i is not None]
    alist1 = [i for i in raw['alist1'] if i is not None]
    alist2 = [i for i in raw['alist2'] if i is not None]
    #Create count of second level domain matches in URLs of the other
    ratio1,count1 = get_rc_url(dlist1, alist2)
    ratio2,count2 = get_rc_url(dlist2, alist1)

    ratio = max(ratio1,ratio2)
    count = max(count1,count2)
    url_features['2ld_a_href_ratio'] = ratio
    url_features['2ld_a_href_count'] = count
  
    #link_href_ratio and link_href_count
    linklist1 = raw["linklist1"]
    linklist2 = raw["linklist2"]
    #Get file name while stripping URL, query terms, whitespaces, and .xhtml
    list1 = [i.split("/")[-1].replace(" ","") for i in linklist1 if i is not None]
    list1 = [i.split("?")[0] for i in list1]
    list1 = [i.replace(".xhtml","") for i in list1]
    list2 = [i.split("/")[-1].replace(" ","") for i in linklist2 if i is not None]
    list2 = [i.split("?")[0] for i in list2]
    list2 = [i.replace(".xhtml","") for i in list2]
    ratio, count = get_rc(list1, list2)
    url_features['link_href_ratio'] = ratio
    url_features['link_href_count'] = count
    
    #2ld_link_href_ratio and 2ld_link_href_count
    #Get second level domains
    dlist1 = [get_2LD(i) for i in linklist1 if i is not None]
    dlist2 = [get_2LD(i) for i in linklist2 if i is not None]
    dlist1 = [i for i in dlist1 if i is not None]
    dlist2 = [i for i in dlist2 if i is not None]
    linklist1 = [i for i in raw['linklist1'] if i is not None]
    linklist2 = [i for i in raw['linklist2'] if i is not None]
    #Create count of second level domain matches in URLs of other
    ratio1,count1 = get_rc_url(dlist1, linklist2)
    ratio2,count2 = get_rc_url(dlist2, linklist1)

    ratio = max(ratio1,ratio2)
    count = max(count1,count2)
    url_features['2ld_link_href_ratio'] = ratio
    url_features['2ld_link_href_count'] = count
    
    #all_2ld_ratio and all_2ld_count   
    soup1 = raw['all1']
    soup2 = raw['all2']
    urls1 = []
    status = 0
    while status != 1:
        try:
            start = soup1.index('"http')+1
            length = soup1[start:].index('"')
            to_add = soup1[start:start+length]
            urls1.append(to_add)
            soup1 = soup1[start+length:]

        except ValueError:
            status = 1
    
    urls2 = []
    status = 0
    while status != 1:
        try:
            start = soup2.index('"http')+1
            length = soup2[start:].index('"')
            to_add = soup2[start:start+length]
            urls2.append(to_add)
            soup2 = soup2[start+length:]
        except ValueError:
            status = 1
    
    urls1a = []
    for i in urls1:
        try:
            end = i.index("?")
            urls1a.append(i[:end])
        except ValueError:
            urls1a.append(i)
    
    urls2a = []
    for i in urls2:
        try:
            end = i.index("?")
            urls2a.append(i[:end])
        except ValueError:
            urls2a.append(i) 
    
    dlist1,dlist2 = filter_url(urls1a, urls2a)
    ratio1,count1 = get_rc_url(dlist1, urls2a)
    ratio2,count2 = get_rc_url(dlist2, urls1a)
 
    ratio = max(ratio1,ratio2)
    count = max(count1,count2)    
 
    url_features['all_2ld_ratio'] = ratio
    url_features['all_2ld_count'] = count
    
    return url_features

def get_word_features(words):
    """Gets word features given dictionary of tag-sorted words
    """
    #Setup word_features dictionary
    word_features = {}
    
    #Setup lists for collecting all words for overall comparison
    overall_words1 = []
    overall_words2 = []
    headers1 = []
    headers2 = []
    
    #meta tag, content attribute
    meta_content_ratio,_,_,_=\
    process_word_tag(words['metacontent1'],
                     words['metacontent2'],
                     overall_words1, 
                     overall_words2)
    word_features['meta_content_ratio'] = meta_content_ratio

    #title tag
    title_ratio,title_count,_,_=\
    process_word_tag(words['title1'],
                     words['title2'],
                     overall_words1,
                     overall_words2)
    word_features['title_ratio'] = title_ratio
    word_features['title_count'] = title_count

    #h1 tag
    h1_ratio,h1_count,list1,list2 =\
    process_word_tag(words['h11'],
                     words['h12'],
                     overall_words1, 
                     overall_words2)
    headers1.extend(list1)
    headers2.extend(list2)
    word_features['h1_ratio'] = h1_ratio
    word_features['h1_count'] = h1_count
    
    #h2 tag
    h2_ratio,h2_count,list1,list2 =\
    process_word_tag(words['h21'],
                     words['h22'],
                     overall_words1, 
                     overall_words2)
    headers1.extend(list1)
    headers2.extend(list2)
    word_features['h2_ratio'] = h2_ratio
    word_features['h2_count'] = h2_count

    #h3 tag
    h3_ratio,h3_count,list1,list2 =\
    process_word_tag(words['h31'],
                     words['h32'],
                     overall_words1, 
                     overall_words2)
    headers1.extend(list1)
    headers2.extend(list2)
    word_features['h3_ratio'] = h3_ratio
    word_features['h3_count'] = h3_count
    
    #h4 tag
    h4_ratio,h4_count,list1,list2 =\
    process_word_tag(words['h41'],
                     words['h42'],
                     overall_words1, 
                     overall_words2)
    headers1.extend(list1)
    headers2.extend(list2)
    word_features['h4_ratio'] = h4_ratio
    word_features['h4_count'] = h4_count
    
    #h5 tag
    h5_ratio,h5_count,list1,list2 =\
    process_word_tag(words['h51'],
                     words['h52'],
                     overall_words1, 
                     overall_words2)
    headers1.extend(list1)
    headers2.extend(list2)
    word_features['h5_ratio'] = h5_ratio
    word_features['h5_count'] = h5_count
    
    #h6 tag
    h6_ratio,h6_count,list1,list2 =\
    process_word_tag(words['h61'],
                     words['h62'],
                     overall_words1, 
                     overall_words2)
    headers1.extend(list1)
    headers2.extend(list2)
    word_features['h6_ratio'] = h6_ratio
    word_features['h6_count'] = h6_count
    
    #across all headers
    _,headers_count =\
    get_rc(headers1,headers2)
    word_features['headers_count'] = headers_count
    
    #p tag
    p_ratio,p_count,_,_ =\
    process_word_tag(words['p1'],
                     words['p2'],
                     overall_words1, 
                     overall_words2)
    word_features['p_ratio'] = p_ratio
    word_features['p_count'] = p_count
    
    #div tag
    div_ratio,div_count,_,_ =\
    process_word_tag(words['div1'],
                     words['div2'],
                     overall_words1, 
                     overall_words2)
    word_features['div_ratio'] = div_ratio
    word_features['div_count'] = div_count
    
    #a tag
    a_ratio,a_count,_,_ =\
    process_word_tag(words['a1'],
                     words['a2'],
                     overall_words1, 
                     overall_words2)
    word_features['a_ratio'] = a_ratio
    word_features['a_count'] = a_count
    
    #button tag
    button_ratio,button_count,_,_ =\
    process_word_tag(words['button1'],
                     words['button2'],
                     overall_words1, 
                     overall_words2)
    word_features['button_ratio'] = button_ratio
    word_features['button_count'] = button_count
    
    #Overall words    
    filtered1, filtered2 =\
    process_word_list(overall_words1,overall_words2)
    overall_words1 = [i.lower() for i in overall_words1]
    overall_words2 = [i.lower() for i in overall_words2]
    overall_word_ratio,overall_word_count =\
    get_rc(overall_words1,overall_words2)
    word_features['overall_word_ratio'] = overall_word_ratio
    word_features['overall_word_count'] = overall_word_count
    
    #Filtered words
    filtered1 = [i.lower() for i in filtered1]
    filtered2 = [i.lower() for i in filtered2]
    filtered_word_ratio,filtered_word_count =\
    get_rc(filtered1,filtered2)
    word_features['filtered_word_ratio'] = filtered_word_ratio
    word_features['filtered_word_count'] = filtered_word_count
    
    #Filtered words list length
    longer, shorter = compare_list_length(filtered1, filtered2)
    if len(shorter) == 0:
        ratio = 0
    else:
        ratio = len(shorter)/len(longer)
    word_features['filtered_word_list_length'] = ratio
    
    return word_features

def get_div_class_data(soup1, soup2):
    """div class ratio and count between 2 soups
    """
    
    #Extract div class
    list1 = get_attributes("div","class",soup1)
    list2 = get_attributes("div","class",soup2)
    

    list1 = [i for i in list1 if i is not None]
    list2 = [i for i in list2 if i is not None]
    

    ratio, count = get_rc(list1, list2)
    
    return ratio, count

#Main feature extraction function
def extract_features(soup1, soup2):
    """Extracts features given 2 soups
    """
    
    #Initialize feature dict
    feature_dict = {}
    
    #get raw urls
    raw_dict = raw_urls(soup1, soup2)
    #get url features
    url_feature_dict = get_URL_features(raw_dict)
    feature_dict.update(url_feature_dict)
    
    #img src ratio
    img_src_ratio = get_img_src_ratio(soup1, soup2)
    feature_dict['img_src_ratio'] = img_src_ratio
    
    #get raw words
    words_dict = raw_words(soup1, soup2)
    #get word features
    words_feature_dict = get_word_features(words_dict)
    feature_dict.update(words_feature_dict)
    
    #div class ratio and count
    div_class_ratio, div_class_count = get_div_class_data(soup1, soup2)
    feature_dict['div_class_ratio'] = div_class_ratio
    feature_dict['div_class_count'] = div_class_count
    
    #style features
    stylelist1 = get_stylelist(soup1)
    stylelist2 = get_stylelist(soup2)
    filelist1 = files_from_lists(stylelist1)
    filelist2 = files_from_lists(stylelist2)
    ratio, count = get_rc(filelist1,filelist2)
    feature_dict['style_file_ratio'] = ratio
    feature_dict['style_file_count'] = count
    
    #all files features
    soup1 = str(soup1)
    soup2 = str(soup2)
    filelist1 = all_files(soup1)
    filelist2 = all_files(soup2)
    ratio, count = get_rc(filelist1,filelist2)
    feature_dict['all_files_ratio'] = ratio
    feature_dict['all_files_count'] = count

    features = pd.DataFrame(feature_dict, index=[0])
    cols = ['a_no_ratio', 'img_src_ratio', 'link_href_ratio', 'link_href_count',
       '2ld_a_href_ratio', '2ld_a_href_count', '2ld_link_href_ratio',
       '2ld_link_href_count', 'all_2ld_ratio', 'all_2ld_count',
       'meta_content_ratio', 'title_ratio', 'title_count', 'h1_ratio',
       'h1_count', 'h2_ratio', 'h2_count', 'h3_ratio', 'h3_count', 'h4_ratio',
       'h4_count', 'h5_ratio', 'h5_count', 'h6_ratio', 'h6_count',
       'headers_count', 'p_ratio', 'p_count', 'div_ratio', 'div_count',
       'a_ratio', 'a_count', 'button_ratio', 'button_count',
       'overall_word_ratio', 'overall_word_count', 'filtered_word_ratio',
       'filtered_word_count', 'filtered_word_list_length', 'div_class_ratio',
       'div_class_count', 'style_file_ratio', 'style_file_count',
       'all_files_ratio', 'all_files_count']
    features = features[cols]
    
    return features

#This function loads the summary scaler and produces a summary
def summarize(features, path):
    """Load scaler, transform features and produce summary
    """

    scaler = pickle.load(open(f"{path}0_scaler.pkl", 'rb'))
    scaled = scaler.transform(features)
    X = pd.DataFrame(scaled, index=features.index, columns=features.columns)
    
    #Domain related columns
    columns = [X['a_no_ratio'].iloc[0],X['2ld_a_href_ratio'].iloc[0],X['2ld_a_href_count'].iloc[0],
               X['2ld_link_href_ratio'].iloc[0],X['2ld_link_href_count'].iloc[0],X['all_2ld_ratio'].iloc[0],
               X['all_2ld_count'].iloc[0]]
    if max(columns)<1:
        domain = 'Low'
    elif max(columns)<2:
        domain = "Moderate"
    else:
        domain = "High"
        
    #Image source related columns
    columns = [X['img_src_ratio'].iloc[0]]
    if max(columns)<1:
        img = 'Low'
    elif max(columns)<2:
        img = "Moderate"
    else:
        img = "High"

    #Word related columns
    columns = [X['meta_content_ratio'].iloc[0],X['title_ratio'].iloc[0],X['title_count'].iloc[0],
               X['h1_ratio'].iloc[0],X['h1_count'].iloc[0],X['h2_ratio'].iloc[0],X['h2_count'].iloc[0],X['h3_ratio'].iloc[0],
               X['h3_count'].iloc[0],X['h4_ratio'].iloc[0],X['h4_count'].iloc[0],X['h5_ratio'].iloc[0],X['h5_count'].iloc[0],
               X['h6_ratio'].iloc[0],X['h6_count'].iloc[0],X['headers_count'].iloc[0],X['p_ratio'].iloc[0],
               X['p_count'].iloc[0],X['div_ratio'].iloc[0],X['div_count'].iloc[0],X['a_ratio'].iloc[0],X['a_count'].iloc[0],
               X['button_ratio'].iloc[0],X['button_count'].iloc[0],X['overall_word_ratio'].iloc[0],
               X['overall_word_count'].iloc[0],X['filtered_word_ratio'].iloc[0],X['filtered_word_count'].iloc[0],
               X['filtered_word_list_length'].iloc[0]]
    if max(columns)<1:
        word = 'Low'
    elif max(columns)<2:
        word = "Moderate"
    else:
        word = "High"
        
    #Style related columns
    columns = [X['div_class_ratio'].iloc[0],X['div_class_count'].iloc[0],X['style_file_ratio'].iloc[0],
               X['style_file_count'].iloc[0]]
    if max(columns)<1:
        style = 'Low'
    elif max(columns)<2:
        style = "Moderate"
    else:
        style = "High"
        
    #File reference related columns
    columns = [X['link_href_ratio'].iloc[0],X['link_href_count'].iloc[0],X['all_files_ratio'].iloc[0],X['all_files_count'].iloc[0]]
    if max(columns)<1:
        file = 'Low'
    elif max(columns)<2:
        file = "Moderate"
    else:
        file = "High"
    
    summary = f"Domain similarity: {domain}\nImage source similarity: {img}\nWord similarity: {word}\nStyle similarity: {style}\nFile reference similarity: {file}"
    
    return summary

#This function loads the prediction standardscaler and transforms features
def scale(features, path):
    """Load scaler and transform features
    """
    scaler = pickle.load(open(f"{path}scaler.pkl", 'rb'))
    X = scaler.transform(features)
    X = pd.DataFrame(X, index=features.index, columns=features.columns)
    
    return X

#This function loads the model and gives a prediction
def predict(features, path):
    """Load model and make a prediction
    """
    model = pickle.load(open(f"{path}htmlc.pkl", 'rb'))
    y = model.predict(features)
    
    return y