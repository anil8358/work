
            ## script is for scraping articles from missmalini##
import urllib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify
from datetime import datetime
# import unicodedata
import mechanize
from utils import *
from scrap_interface import ScrapInterface
import gallifrey
import config
logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)
# format the json of required content from the fetched page or article###
class CrawlMissmalini(ScrapInterface):
    def make_body(self, page):
        title_content = ''
        para_content = ''
        published_date = ''
        tags_content = ''
        img_src = ''

        try:
            published_date = str(datetime.now())[0:10]
            if page.find_all('div', class_='articleTitle articleTitle-bollywood'):
                title_content = page.find_all('div',class_='articleTitle articleTitle-bollywood')[0].get_text()
            if page.find('div', class_='custom_img_wrapper'):
                img_src = page.find('div',class_='custom_img_wrapper').find('img').get('src')
            if page.find_all('div',class_='tagLinks col-md-11'):
                tags  = page.find_all('div',class_='tagLinks col-md-11')[0].find_all('a')
                for tag in tags:
                    tags_content = tags_content + tag.get_text()+"   "
            if page.find_all('div',class_='articleText'):
                para = page.find_all('div',class_='articleText')[0].find_all('p')
            for div in para:
                para_content= para_content+div.get_text()+ '.  '

            try:

                dt = str(page.find_all('span', class_='articleDate')[0].get_text()).strip().split('.')
                published_date = str(datetime.strptime(dt[0].strip()[:3] + " " + dt[1].strip() + " " + dt[2].strip(), '%b %d %Y').date())
            except:
               logger.info("Could not fetch published date , putting current date")
        except Exception, e:
            logger.error("Error in body (make_body_missmalini):  " , str(e))
            pass
        return {'title':title_content.encode('ascii', 'ignore'),'para':para_content.encode('ascii', 'ignore'),'published_date':published_date.encode('ascii', 'ignore'),"tags":tags_content.encode('ascii', 'ignore'),"img_src":img_src.encode('ascii', 'ignore')}


    # iterate the list of urls for making body and indexing   which were fetched from a page articles of the website.
    #each url in the list s corresponds to a single article/news or post
    def write_pages(self, urls):
        # global no
        # try:
        for source in urls:
            to_write = get_content_mechanize(source)
            if to_write:
                body = self.make_body(to_write)
                make_index('gossip_bot','blogs', body, source)
        return {"success":True}
        # except Exception, e:
        #     print "Error in Fetching (write_pages): \n " + str(e)
        #     pass
            # # with open("file_no"+str(post_no)+".html", "w") as file:
            #     file.write(str(to_write))
            #     post_ = post_no+1


    #scraping pages one by one and gets the posts or article in a list

    def scrap(self):
        url = "https://www.missmalini.com/category/bollywood/page/"
        for i in range(20):
            articles = []
            logger.info(url+str(i))
            soup = get_content_mechanize(url+str(i+1))
            divs = soup.find_all('div',class_='portfolioDetails clearfix')
            logger.info(len(divs))
            for hdr in divs:
                src = hdr.find('a').get('href')
                # print src
                articles.append(src)
            # print len(articles)
            self.write_pages(articles)
    # scrap_missmalini()
