
          #### this script is for getting celebrity specific news ####

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

# post_no = 1

# def trimoff(str):
#     stop_words = set(stopwords.words('english'))
#     str_token = word_tokenize(str)
#     filtered_words = [word for word in str_token if word not in stop_words]
#     return filtered_words


# format the json of required content from the fetched page or article###
class CrawlBollywoodNews(ScrapInterface):

    def make_body(self, page):
        title_content = ''
        para_content = ''
        img_src = ''
        celeb_name = ''
        published_date = str(datetime.now())[0:10]
        try:
            if page.find('h1',class_='h1-title'):
                title_content = page.find('h1',class_='h1-title').get_text()
            if page.find('div',class_='celeb-name'):
                celeb_name = page.find('div',class_='celeb-name').find('div').get_text()
            if page.find('img',class_='imagefield imagefield-field_inner_image'):
                img_src = page.find('img',class_='imagefield imagefield-field_inner_image').get('src')
            if page.find('div',class_='contentmain'):
                content  = page.find('div',class_='contentmain').find_all('div',class_=None)
            for ct in content:
                para_content = para_content+ct.get_text()+".   "

        except Exception, e:
            logger.error("Error in body (make_body_bollywood):  " , str(e))
            pass
        return {'title':title_content.encode('ascii', 'ignore'),'para':para_content.encode('ascii', 'ignore'),"tags":celeb_name.encode('ascii', 'ignore'),"img_src":img_src.encode('ascii', 'ignore')}




    # iterate the list of urls for making body and indexing   which were fetched from a page articles of the website.
    #each url in the list s corresponds to a single article/news or post
    def write_pages(self, urls):
        # global no
        try:
            for source in urls:
                to_write = get_content_mechanize(source)
                if to_write:
                    body = self.make_body(to_write)
                    make_index('gossip_bot', 'blogs',  body,source)
            return {"success":True}
        except Exception, e:
            logger.error("Error in Fetching (write_pages):  " , str(e))
            pass
            # # with open("file_no"+str(post_no)+".html", "w") as file:
            #     file.write(str(to_write))
            #     post_ = post_no+1

    #scraping pages one by one and gets the posts or article in a list


    def scrap(self):
        url = "http://www.bollywood.com/celebrities/news?page="
        for i in range(5):
            articles = []
            logger.info(url+str(i))
            soup = get_content_mechanize(url+str(i))
            if soup.find_all('div',class_='contentmain'):
                divs = soup.find_all('div',class_='contentmain')[0].find_all('div',class_='hollywood-news-title')
                logger.info(len(divs))
                for div in divs:
                    if div.find('a'):
                        src = 'http://www.bollywood.com'+div.find('a').get('href')
                        articles.append(src)

                self.write_pages(articles)
