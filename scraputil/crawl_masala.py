                            ####scraping articles from masala #####

import urllib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify
from datetime import datetime
from utils import *
from scrap_interface import ScrapInterface
import gallifrey
import config

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

# format the json of required content from the fetched page or article###
class CrawlMasala(ScrapInterface):

    def make_body(self, page):
        title_content = ''
        para_content = ''
        published_date =''
        tags_content = ''
        img_src = ''
        try:
            published_date = str(datetime.now())[0:10]


            if page.find_all("span", property = "dc:title"):
                title_content = page.find_all("span", property= "dc:title")[0].get('content')

            if page.find_all('ul', class_= 'tags-list'):
                tags  = page.find_all('ul', class_= 'tags-list')[0].find_all('li')
                for tag in tags:
                    tags_content = tags_content + tag.get_text()+"   "
            if page.find('div',class_='article-image'):
                img_src = page.find('div',class_='article-image').find('img').get('src')
            if page.find_all('div',class_ = 'body-content')[0]:
                para = page.find_all('div',class_ = 'body-content')[0].find_all('p')
            for div in para:
                para_content= para_content+div.get_text()+ '.  '

            try:
                dt = str(str(page.find_all('span', class_='time')[0].get_text()).split(',')[-1:][0])[1:].split(' ')
                published_date = str(datetime.strptime(dt[1][:3] + " " + dt[0] + " " + dt[2], '%b %d %Y').date())
            except:
                logger.info("Could not fetch original date putting current date")
        except Exception, e:
            logger.info("Error in body (make_body_masala):  " , str(e))
            pass
        return {'title':title_content.encode('ascii', 'ignore'),'para':para_content.encode('ascii', 'ignore'),'published_date':published_date,"tags":tags_content.encode('ascii', 'ignore'),"img_src":img_src.encode('ascii', 'ignore')}


    # iterate the list of urls for making body and indexing   which were fetched from a page articles of the website.
    #each url in the list s corresponds to a single article/news or post

    def write_pages(self, urls):
        # global no
        try:
            for source in urls:
                to_write = get_content(source)
                if to_write:
                    body = self.make_body(to_write)
                    make_index('gossip_bot', 'blogs' ,body,source)
            return {"succes":True}
        except Exception, e:
            logger.error("Error in Fetching (write_pages):  " , str(e))
            pass
        #     # with open("file_no"+str(post_no)+".html", "w") as file:
            #     file.write(str(to_write))
            #     post_ = post_no+1



    #scraping pages one by one and gets the posts or article in a list

    def scrap(self):
        url = "http://www.masala.com/celebrities/news?page="
        for i in range(25):
            articles = []
            logger.info( url+str(i))
            soup = get_content(url+str(i+1))
            if soup.find_all('div',class_='item-list clearfix'):
                divs = soup.find_all('div',class_='item-list clearfix')[0].find_all('div',class_='field-item even',property = 'dc:title')
            for x in divs:
                 src = 'http://www.masala.com'+x.find('h3').find('a').get('href')
                 articles.append(src)
            self.write_pages(articles)
