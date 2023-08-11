#Second version, I'm going to create a BookData class that will have the required attributes and methods


import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import lxml

#we need self to intialize, and soup is the input for a given instance
class BookData:
    def __init__ (self, url, soup):
        self.url = url
        self.soup = soup
        self.details_list = self.get_details_list()
        self.KU = self.check_KU()

    @staticmethod
    def from_url (url):
        soup = BookData.load_website(url)
        return BookData (url, soup)

        

    def load_website(url): #just going to leave this here for the moment as an example of a selenium function
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
        

#helper function for creating product details list to find specific items in
    def get_details_list(self):
        #div id with most of the product details we'll want
        detail_div = self.soup.find('div', {'id' : "detailBulletsWrapper_feature_div"})
        #create the list of elements in the product detail list
        #you really need to change the error to make sense with however you loop the program
        if detail_div == None:
            print('missed html once')
            time.sleep(5)
            self.soup = self.load_website(retries = 0, delay = 0)
            detail_div = self.soup.find('div', {'id' : "detailBulletsWrapper_feature_div"})
        if detail_div == None:
            print ('missed html again')
            time.sleep(5)
            self.soup = self.load_website(retries = 0, delay = 0)
            detail_div = self.soup.find('div', {'id' : "detailBulletsWrapper_feature_div"})
        if detail_div == None:
            print ('missed html a third time')
            time.sleep(10)
            self.soup = self.load_website(retries = 0, delay = 0)
            detail_div = self.soup.find('div', {'id' : "detailBulletsWrapper_feature_div"})
        if detail_div == None:
            print ('missed html a fourth time')
            time.sleep(20)
            self.soup = self.load_website(retries = 0, delay = 0)
            detail_div = self.soup.find('div', {'id' : "detailBulletsWrapper_feature_div"})

        if detail_div == None:

            raise ValueError(f"There is something wrong with the html from {self.url}")

        list_items = detail_div.find_all('span', {'class' : 'a-list-item'} )
        
        return list_items

#helper function to strip numbers out of strings, uses regular expressions
    def digit_find(self, text):
        pattern = '(\d+\,)?(\d+\,)?\d+(\.\d+)?'
        #keep in mind that re.search stops after the first find, it actually seems like that is the standard
        match = re.search(pattern, text) 
        output = match.group() 
        return output



    def get_asin(self):
        items = self.details_list
        
        
        for item in items:
            if 'ASIN' in item.text:
                ASIN_span = item.find_all('span')[-1]
                ASIN = ASIN_span.text.strip()
                
                return ASIN
            
    def get_publication_date(self):
        items = self.details_list

        for item in items:
            if 'Publication date' in item.text:
                pub_date_span = item.find_all('span')[-1]
                pub_date_str = pub_date_span.text.strip()
                pub_date_time = datetime.strptime(pub_date_str, "%B %d, %Y")
                pub_date = datetime.strftime(pub_date_time, "%Y-%m-%d")

        return pub_date

    def get_publisher(self):
        items = self.details_list
        publisher = None
        for item in items:
            if 'Publisher' in item.text:
                span = item.find_all('span')
                publisher_text = span[-1].text
                publisher = re.sub(r'\(.*?\)', '', publisher_text).strip()

        if publisher == None:
            return 'None'
        else:
            return publisher        
                


    def get_print_length(self):
        items = self.details_list
        length = None
        for item in items:
            if 'Print length' in item.text:
                length_set = item.find_all('span')
                length_text = " ".join(tag.text for tag in length_set)

                length = self.digit_find(length_text)
        
        if length == None:
            return 'None'
        else: 
            return length 

    def get_rank(self):
        items = self.details_list
        rank = None
        for item in items:
            if 'Best Sellers' in item.text:
                rank_text = item.text
                rank = self.digit_find(rank_text)
        
        if rank == None:
            return 'None'
        else:
            return rank

    #I'm definitely seeing how using a class is an easy way to make the code less redundant
    #though I think there are methods to make it equally clean with higher order functions
    #If a class actually is a specific type of higher order function?
    #except, no, because the class also has attributes

    def get_rating(self):    
        #if you want the 
        items = self.details_list
        #you need to intialize the variable so that the if statement will return correctly
        #since the rating in the forloop doesn't output outside of it
        rating = None
        for item in items:
            if 'Customer Reviews' in item.text:
                rating_span = item.find_all('span')[1]
                rating = rating_span.find('span', {'class' : 'a-size-base a-color-base'} )
                rating = rating.text.strip()
                return rating
        #this gets nothing from the retting inside the for loop, if the for loop rating doesn't create rating based on it being none
        if rating == None:
            return 'None'
        else:
            return rating
        
    def get_how_many_reviews(self):
        items = self.details_list
        number = None
        for item in items:
            if 'Customer Reviews' in item.text:
                number_text = item.find_all('span')[-1].text
                number = self.digit_find(number_text)
                return number
        
        if number == None:
            return 0
        else:
            return number
        

    def check_KU(self):
        element = self.soup.find('span', {'id': 'tmm-ku-upsell'})
        if element == None:
            KU = 'N'
        else:
            KU = 'Y'
        return KU

    #because Amazon structures the page differently if it is a KU book, we need to first check
    #
    def get_price(self):

        if self.KU == 'N':
            element = self.soup.find('span', {'id' : 'kindle-price'})
            price = element.text.strip()
            return price
        
        #use regular experssion matching, based on the d = digits, the sections bounded by \ and . for decimal
        else:
            element = self.soup.find('a', {'class' : "a-size-mini a-link-normal"})
            text = element.text.strip()
            pattern = r"\d+\.\d+"
            match = re.search(pattern, text)
            price = match.group()
            return price

   

    def get_author_name (self):
        element = self.soup.find('span', {'class' : 'author notFaded'})
        text = element.text.strip()
        name = text.replace("\n(Author)", "")
        translator = str.maketrans("","", string.punctuation)
        name = text.translate(translator)
        return name

    def get_title(self):
        element = self.soup.find('span', {'id' : 'productTitle'})
        title = element.text.strip()
        return title
    
    def get_author_description(self):
        author_description = None
        author_description = self.soup.find('div', {'class' : 'a-cardui-content a-cardui-uninitialized'})
        if author_description == None:
            return 'None'
        return author_description.text

#it is important to run the strip before writing to a csv file to avoid opening with something that csv doesn't like
    def get_blurb(self):
        div = self.soup.find('div', {'id' : 'bookDescription_feature_div'})
        blurb = div.text
        blurb = blurb.strip()
        return blurb

    def get_top_reviews(self):
        outer_div = self.soup.find ('div', {'id' : 'cm-cr-dp-review-list'})
        if outer_div == None:
            return None
        review_divs = outer_div.find_all('div', {'class' :"a-section review aok-relative"})
        reviews = []

#here we are already removing the \n before printing into the text
        for review_div in review_divs:
            div = review_div.find('div', {'data-hook' : 'review-collapsed'})
            review_dirty = div.text
            review = review_dirty.replace('\n', ' ')
            reviews.append(review)
        return reviews

    #Why would I want to have it output the list? It might be a bit more memory efficient, but the dictionary is probably a better approach for writing into the text?

    def get_all_data(self):
        ASIN = self.get_asin()
        title = self.get_title()
        author_name = self.get_author_name()
        publisher = self.get_publisher()
        KU = self.check_KU()
        price = self.get_price()
        rank = self.get_rank()
        pub_date = self.get_publication_date()
        print_length = self.get_print_length()
        review_rating = self.get_rating()
        review_quantity = self.get_how_many_reviews()
        blurb = self.get_blurb()
        reviews = self.get_top_reviews()
        author_description = self.get_author_description()

        return {'ASIN': ASIN,
                'title': title,
                'author_name': author_name,
                'publisher' : publisher,
                'KU': KU,
                'price': price,
                'rank': rank,
                'pub_date': pub_date,
                'print_length': print_length,
                'review_rating': review_rating,
                'review_quantity': review_quantity,
                'blurb': blurb,
                'reviews': reviews,
                'author_description' : author_description}