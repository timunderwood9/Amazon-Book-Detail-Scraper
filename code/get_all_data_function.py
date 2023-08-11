#So this will be the first, and probably simpler, creation of my get_all_data module, it uses just funcitons


import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
from fake_useragent import UserAgent 
import link_collector
from datetime import datetime
import os
import re


# Helper function to get a BeautifulSoup object from a URL


# Helper functions to extract data from the BeautifulSoup object

#helper function for creating product details list to find specific items in
def details_list(soup):
    #div id with most of the product details we'll want
    detail_div = soup.find('div', {'id' : "detailBulletsWrapper_feature_div"})
    #create the list of elements in the product detail list
    #you really need to change the error to make sense with however you loop the program
    if detail_div is None:
        print('Failed to find details list, trying again')
        soup = get_soup_ua_session(links[current_link_index])
        detail_div = soup.find('div', {'id' : "detailBulletsWrapper_feature_div"})
        return detail_div
    
    if detail_div is None:
        raise ValueError('no details list')

    list_items = detail_div.find_all('span', {'class' : 'a-list-item'} )
    
    return list_items

#helper function to strip numbers out of strings, uses regular expressions
def digit_find(text):
    pattern = '\d+(\.\d+)?'
    #keep in mind that re.search stops after the first find, it actually seems like that is the standard
    match = re.search(pattern, text) 
    output = match.group() 
    return output



def get_asin(soup):
    items = details_list(soup)
    
    
    for item in items:
        if 'ASIN' in item.text:
            ASIN_span = item.find_all('span')[-1]
            ASIN = ASIN_span.text.strip()
            
            return ASIN
        
def get_publication_date(soup):
    items = details_list(soup)

    for item in items:
        if 'Publication date' in item.text:
            pub_date_span = item.find_all('span')[-1]
            pub_date_str = pub_date_span.text.strip()
            pub_date_time = datetime.strptime(pub_date_str, "%B %d, %Y")
            pub_date = datetime.strftime(pub_date_time, "%Y-%m-%d")

    return pub_date

def get_print_length(soup):
    items = details_list(soup)
    for item in items:
        if 'Print length' in item.text:
            length_set = item.find_all('span')
            length_text = " ".join(tag.text for tag in length_set)

            length = digit_find(length_text)
        
    return length 

def get_rank(soup):
    items = details_list(soup)
    for item in items:
        if 'Best Sellers' in item.text:
            rank_text = item.text
            rank = digit_find(rank_text)
    return rank

#I'm definitely seeing how using a class is an easy way to make the code less redundant
#though I think there are methods to make it equally clean with higher order functions
#If a class actually is a specific type of higher order function?
#except, no, because the class also has attributes

def get_rating(soup):    
    items = details_list(soup)
    for item in items:
        if 'Customer Reviews' in item.text:
            rating_span = item.find_all('span')[1]
            rating = rating_span.find('span', {'class' : 'a-size-base a-color-base'} )
            rating = rating.text.strip()
    return rating
    
def get_how_many_reviwes(soup):
    items = details_list(soup)
    for item in items:
        if 'Customer Reviews' in item.text:
            number_text = item.find_all('span')[-1].text
            number = digit_find(number_text)
        return number
    

def check_KU(soup):
    element = soup.find('span', {'id': 'tmm-ku-upsell'})
    if element == None:
        KU = 'N'
    else:
        KU = 'Y'
    return KU

#because Amazon structures the page differently if it is a KU book, we need to first check
#
def get_price(soup, KU):

    if KU == 'N':
        element = soup.find('span', {'id' : 'kindle-price'})
        price = element.text.strip()
        return price
    
    #use regular experssion matching, based on the d = digits, the sections bounded by \ and . for decimal
    else:
        element = soup.find('a', {'class' : "a-size-mini a-link-normal"})
        text = element.text.strip()
        pattern = r"\d+\.\d+"
        match = re.search(pattern, text)
        price = match.group()
        return price

#need to have an output for cases where there is no visible paperback edition
def get_paperback_price (soup):
    element = soup.find('a', {'id' : 'a-autoid-9-announce'})
    if element == None:
        return 'None'
    else:
        text = element.text.strip()
        price = digit_find(text)
        return price

def get_author_name (soup):
    element = soup.find('span', {'class' : 'author notFaded'})
    text = element.text.strip()
    name = text.replace("\n(Author)", "")
    return name

def get_title(soup):
    element = soup.find('span', {'id' : 'productTitle'})
    title = element.text.strip()
    return title

def get_blurb(soup):
    div = soup.find('div', {'id' : 'bookDescription_feature_div'})
    blurb = div.text
    return blurb

def get_top_reviews(soup):
    outer_div = soup.find ('div', {'id' : 'cm-cr-dp-review-list'})
    review_divs = outer_div.find_all('div', {'class' :"a-section review aok-relative"})
    reviews = []


    for review_div in review_divs:
        div = review_div.find('div', {'data-hook' : 'review-collapsed'})
        review_dirty = div.text
        review = review_dirty.replace('\n', ' ')
        reviews.append(review)
    return reviews

#Why would I want to have it output the list? It might be a bit more memory efficient, but the dictionary is probably a better approach for writing into the text?

def get_all_data(soup):
    ASIN = get_asin(soup)
    title = get_title(soup)
    author_name = get_author_name(soup)
    KU = check_KU(soup)
    price = get_price(soup, KU)
    paperback_price = get_paperback_price(soup)
    rank = get_rank(soup)
    pub_date = get_publication_date(soup)
    print_length = get_print_length(soup)
    review_rating = get_rating
    review_quantity = get_how_many_reviwes
    blurb = get_blurb(soup)
    reviews = get_top_reviews(soup)

    return {'ASIN': ASIN,
            'title': title,
            'author_name': author_name,
            'KU': KU,
            'price': price,
            'paperback_price': paperback_price,
            'rank': rank,
            'pub_date': pub_date,
            'print_length': print_length,
            'review_rating': review_rating,
            'review_quantity': review_quantity,
            'blurb': blurb,
            'reviews': reviews}