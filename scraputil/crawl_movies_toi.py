
                        ### scraping movie reviews from TOI#####

import urllib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify
from datetime import datetime
from utils import *
from scrap_interface import ScrapInterface
# import unicodedata
import mechanize
import gallifrey
import config

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

# format the json of required content from the fetched page or article###
class CrawlMoviesTOI(ScrapInterface):

    def make_body(self, page):
        title_content = ''
        rating = ''
        img_src = ''
        review_src = ''
        review_text = ''
        movie_title = ''
        cast = ''
        genre = ''

        try:

            if page.find('img',pg='MoviePic'):
                img_src = 'timesofindia.indiatimes.com' + str(page.find('img',pg='MoviePic').get('src'))
            if page.find('span',class_='ratingMovie'):
                rating = page.find('span',class_='ratingMovie').get_text()
            if page.find('h1'):
                title_content = page.find('h1').get_text()
                movie_title = ' '.join(page.find('h1').get_text().split(' ')[:-2])

            # review_text = page.find('div',class_='contentmain').find('p').get_text()
            if page.find('li',mvtab='MR'):
                review_src = 'timesofindia.indiatimes.com' + page.find('li',mvtab='MR').find('a').get('href')
            cast = page.find('span',class_='casting').get_text()
            genre = page.find_all('span',class_='casting')[2].get_text()
        except Exception, e:
            logger.error("Error in body (make_body_bollywood_review):  " , str(e))
            pass
        return {'title':title_content.encode('ascii', 'ignore'),'review_text':review_text.encode('ascii', 'ignore'),'review_src':review_src,"img_src":img_src.encode('ascii', 'ignore'),"rating":rating,"movie_title": movie_title.encode('ascii', 'ignore'),"cast":cast,"genre":genre}



    # iterate the list of urls for making body and indexing   which were fetched from a page articles of the website.
    #each url in the list s corresponds to a single article/news or post

    def write_pages(self, urls):
        # global no
        try:
            for source in urls:
                to_write = get_content(source)
                if to_write:
                    body = self.make_body(to_write)
                    make_index('movies_content','reviews' , body,source)
            return {"succes":True}
        except Exception, e:
            logger.error( "Error in Fetching (write_pages):  " , str(e))
            pass
            # # with open("file_no"+str(post_no)+".html", "w") as file:
            #     file.write(str(to_write))
            #     post_ = post_no+1


    #scraping pages one by one and gets the posts or article in a list


    def scrap(self):
        url = "http://timesofindia.indiatimes.com/entertainment/hindi/movie-reviews?page="
        for i in range(15):
            movie_reviews = []
            logger.info(url+str(i))
            soup =  get_content(url+str(i+1))
            if soup.find('div',class_='mr_listing_right'):
                divs = soup.find_all('div',class_='mr_listing_right')
                logger.info(len(divs))
                for div in divs:
                    if div.find('a'):
                        src = 'http://timesofindia.indiatimes.com'+div.find('a').get('href')
                        # print src
                        movie_reviews.append(src)
                # print len(articles)
                self.write_pages(movie_reviews)
    # scrap_movie_review_toi()
