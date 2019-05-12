                        #### scraping articles from dontcallit bollywood####

import urllib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify
from datetime import datetime
from utils import *
from scrap_interface import ScrapInterface
# format the json of required content from the fetched page or article###
import gallifrey
import config
logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

class CrawlDontcallitbollywood(ScrapInterface):

    def make_body(self, page):
        title_content = ''
        para_content = ''
        published_date =''
        img_src = ''
        try:
            published_date = str(datetime.now())[0:10]
            title_content = page.find_all('header',class_='entry-header')[0].get_text()

            tags  = page.find_all('a',rel='tag')
            tags_content = ''
            for tag in tags:
                tags_content = tags_content + tag.get_text()+"   "
            if page.find_all('div',class_='entry-content'):
                para = page.find_all('div',class_='entry-content')[0].find_all('p')
            for div in para:
                para_content= para_content+div.get_text()+ '.  '
            try:
                dt = str(page.find_all('time', class_='entry-date')[0].get_text()).split(' ')
                published_date = str(datetime.strptime(dt[0][:3] + " " + dt[1].split(',')[0] + " " + dt[2], '%b %d %Y').date())
            except:
                logger.info("could not fetch otginal date putting current date")
        except Exception, e:
            logger.error("Error in body (make_body_dontcallitbollwood):  " , str(e))
            pass
        return {'title':title_content.encode('ascii', 'ignore'),'para':para_content.encode('ascii', 'ignore'),'published_date':published_date,"tags":tags_content.encode('ascii', 'ignore'),"img_src":img_src.encode('ascii', 'ignore')}


    # iterate the list of urls for making body and indexing   which were fetched from a page articles of the website.
    #each url in the list s corresponds to a single article/news or post

    def write_pages(self, urls):

        try:
            for source in urls:
                to_write = get_content(source)
                if to_write:
                    body = self.make_body(to_write)
                    make_index('gossip_bot','blogs' , body,source)
            return {"success":True}
        except Exception, e:
            logger.error("Error in Fetching (write_pages):  " , str(e))
            pass
            # with open("file_no"+str(post_no)+".html", "w") as file:
            #     file.write(str(to_write))
            #     post_ = post_no+1


    #scraping pages one by one and gets the posts or article in a list

    def scrap(self):
        url = "https://dontcallitbollywood.com/page/"
        for i in range(15):
            articles = []
            print url+str(i)
            soup =  get_content(url+str(i+1))
            if soup.find_all('h1',class_='entry-title'):
                divs = soup.find_all('h1',class_='entry-title')
            for hdr in divs:
                src = hdr.find('a').get('href')
                articles.append(src)
            self.write_pages(articles)


    # scrap_dontcallitbollwood()
