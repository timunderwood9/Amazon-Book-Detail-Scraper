

from selenium import webdriver
from bs4 import BeautifulSoup
import link_collector
from datetime import datetime
import os
import get_all_data_class
import csv
import  traceback
import json
import logging
import sys
from selenium.webdriver.chrome.options import Options
import re
import lxml

# Helper function to get a BeautifulSoup object from a URL
def get_soup_selenium(url): #just going to leave this here for the moment as an example of a selenium function
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537')

    # Initiate driver with options
    driver = webdriver.Chrome(options=chrome_options)



    # Get URL
    driver.get(url)

    # Pass the page source to BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Close the browser
    driver.quit()
    return soup



#A key function, this is where we get the list of links to check, it will also create a new list
#if the list of links is more than a month old, or does not exist
#it creates the list by calling on the imported list collector module, which is a seperate script I wrote
def load_links_list():
    #check existence
    if not os.path.exists('links.txt'):
        link_collector.collect_links()

    #check date
    creation_time = os.path.getctime('links.txt')
    creation_date = datetime.fromtimestamp(creation_time)
    current_date = datetime.now()
    difference = current_date - creation_date

    if difference.days > 1:
        link_collector.collect_links()
    
    #open links.txt and turn it into a list of links
    with open ('links.txt', 'r') as file:
        links = file.readlines()
        links = [link.strip() for link in links]
    return links

#I'm just going to run the full scrape off of my mobile hotspot instead of putting in
#a random delay to minimize chances of getting the ip blocked
def write_to_csv():
    current_date = datetime.today().day
    links = load_links_list()
    print (f'There are {len(links)} links')

    suffix = 0
#just inserting a try except block to simply write a new csv file if I have the old one open,
# did this because I was annoyed while testing by the error popping up.
# myabe it isn't best practice to leave it in the code?
    while True:
        try:
            filename = f'books-data-{current_date}'
            if suffix > 0:
                filename += f'-{suffix}'
            filename += '.csv'


        #you need to open with nothing showing up as the newline so that csv will write to it correctly
        #csv handles setting up the new line, so the open program doesn't have to do anything
            with open (filename, 'w', newline = '', encoding = 'utf-8') as file: 
                writer = csv.writer(file, quoting=csv.QUOTE_ALL)

                #initialize with the dictionary keys as the column headers
                book = get_all_data_class.BookData.from_url(links[0])
                data = book.get_all_data()
                reviews = data.pop('reviews')


                #enumerate is cool, it counts through the items in the list, and then does the thing 
                #to each item. 
                if reviews != None:
                    for i, review in enumerate(reviews):
                        #data is the dictionary, and data['new string'] = value creates the new key/value pair
                        data[f'review-{i+1}'] = review
                    
                headers = data.keys()
                writer.writerow(headers)
                
                link_number = 0

                for link in links:
                    print (link_number)
                    link_number += 1

                    try:
                        book = get_all_data_class.BookData.from_url(link)
                        data = book.get_all_data()
                        reviews = data.pop('reviews')
                        if reviews != None:

                            for i, review in enumerate(reviews):
                                #data is the dictionary, and data['new string'] = value creates the new key/value pair
                                data[f'review-{i+1}'] = review
                                
                        writer.writerow(data.values())
                    #reason to not use this always is that it involves encoding into utf-8 and then decoding, which takes extra resources, best to just use when necessary
                    except UnicodeEncodeError:
                        #you have to create a new dictionary to write from, because you can't directly modify the data.values() with .encode since it doesn't call on dictionary objects
                        #note that because they are strings, you can do encode and decode on the values
                        
                        cleaned_data = {key: value.encode('utf-8', 'ignore').decode('utf-8') if value is not None else None for key, value in data.items() }
                        #apparently writerow tries to build the entire thing before it writes anything, so it won't start writing a row if there is an Unicode exception
                        writer.writerow(cleaned_data.values())


                    except Exception as e:
                        print (f'Something went wrong with {link}: {e}') #not links[i] because we aren't using an index loop
                        traceback.print_exc()
                        continue
                    
            break

        except PermissionError:
         # If a PermissionError was raised, increment the suffix and try again
            suffix += 1
                
def write_to_json():
    current_date = datetime.today().day
    links = load_links_list()
    filename = f'books-data-{current_date}.json'
    link_number = 0

    data = []

    for link in links:
        print (link_number)
        link_number += 1

        try:
            book = get_all_data_class.BookData.from_url(link)
            book_data = book.get_all_data()
            data.append(book_data)
        except Exception as e:
            print(f'Something went wrong with {link}: {e}' )
            logging.exception (f'Something went wrong with {link}: {e}')


            #supposedly no continue needed because the except block shows up at the end of the loop
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
                

def write_to_file():
    user_input = input('.csv, JSON or both?>')
    user_input_lower_case = user_input.lower()
    if user_input_lower_case.__contains__('.csv'):
        write_to_csv()
    elif user_input_lower_case.__contains__('json'):
        write_to_json()
    elif user_input_lower_case.__contains__('both'):
        write_to_csv()
        write_to_json()
    

logging.basicConfig(filename='scraper.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s')

write_to_csv()


# book = get_all_data_class.BookData('https://www.amazon.com/Their-Cottage-Ramsgate-Prejudice-Variation-ebook/dp/B09X45KB8Z')
# data = book.get_all_data()
# print (data)

