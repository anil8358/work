
                        ### scraping movie reviews from bollywod.com#####

import urllib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify
from datetime import datetime
from utils import *
# import unicodedata
import mechanize
from scrap_interface import ScrapInterface
import gallifrey
import config

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

# format the json of required content from the fetched page or article###
class CrawlMovies(ScrapInterface):

    def make_body(self, page):
        title_content = ''
        rating = ''
        img_src = ''
        review_src = ''
        review_text = ''
        movie_title = ''
        genre = ''
        cast = []

        try:
            if page.find_all('img',class_='imagefield imagefield-field_cover_image'):
                img_src = str(page.find_all('img',class_='imagefield imagefield-field_cover_image')[0].get('src'))
            if page.find_all('span',class_='val'):
                rating = page.find_all('span',class_='val')[0].get_text()
            if page.find('div',class_='contentmain').find_all('div',class_='views-field views-field-title'):
                title_content = page.find('div',class_='contentmain').find_all('div',class_='views-field views-field-title')[0].get_text()
            review_text = page.find('div',class_='contentmain').find('p').get_text()
            if page.find('div',class_='views-field views-field-view-node'):
                review_src = 'www.bollywood.com' + page.find('div',class_='views-field views-field-view-node').find('a').get('href')
            movie_title = ' '.join( page.find('h1',class_='movies').get_text().split(' ')[:-2])
            cast_url = 'http://www.bollywood.com'+page.find('li',class_='menu-id-3').find('a').get('href')
            cast_content = get_content_mechanize(cast_url)
            celeb = cast_content.find_all('div',class_='celeb_name_value')
            for name in celeb:
                cast.append(name.find('a').get_text())
        except Exception, e:
            logger.error("Error in body (make_body_bollywood_review_TOI):  ",  str(e))
            pass
        # except:
        #     print "ERROR in body!!!"
        return {'title':title_content.encode('ascii', 'ignore'),'review_text':review_text.encode('ascii', 'ignore'),'review_src':review_src.encode('ascii', 'ignore'),"img_src":img_src.encode('ascii', 'ignore'),"rating":rating,"movie_title": movie_title.encode('ascii', 'ignore'),"cast":cast,"genre":genre}


    # iterate the list of urls for making body and indexing which were fetched from a page articles of the website.
    # each url in the list s corresponds to a single article/news or post
    def write_pages(self, urls):
        # global no
        try:
            for source in urls:
                to_write = get_content_mechanize(source)
                if to_write:
                    body = self.make_body(to_write)
                    make_index('movies_content','reviews' , body,source)
            return {"succes":True}
        except Exception, e:
            logger.error("Error in Fetching (write_pages):  " , str(e))
            pass


    # scraping pages one by one and gets the posts or article in a list
    def scrap(self):
        url = "http://www.bollywood.com/movies?page="
        for i in range(15):
            movie_reviews = []
            logger.info(url+str(i))
            soup =  get_content_mechanize(url+str(i))
            if soup.find_all('div',class_='contentmain'):
                divs = soup.find_all('div',class_='contentmain')[0].find_all('div',class_='views-field views-field-phpcode-3')
                logger.info(len(divs))
                for div in divs:
                    if div.find('a'):
                        src = 'http://www.bollywood.com'+div.find('a').get('href')
                        # print src
                        movie_reviews.append(src)
                # print len(articles)
                self.write_pages(movie_reviews)
    # scrap_movie_review()
