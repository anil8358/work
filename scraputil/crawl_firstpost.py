
            #### scraping articles from firstpost#####
import urllib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify
from datetime import datetime
import unicodedata
from utils import *
from scrap_interface import ScrapInterface
import gallifrey
import config
logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

class CrawlFirstpost(ScrapInterface):

    def make_body(self, page):
        title_content = ''
        para_content = ''
        published_date =''
        tags_content = ''
        img_src = ''
        try:
            published_date = str(datetime.now())[0:10]

            if page.find_all("h1", class_ = "page-title article-title"):
                title_content = page.find_all("h1", class_ = "page-title article-title")[0].get_text()
            if page.find_all("div", class_="article-tags hidden-md hidden-lg" ):
                tags_content  = str(page.find_all("div", class_="article-tags hidden-md hidden-lg" )[0].get_text()).split('#')[1:]
            if page.find_all('div',itemprop='articleBody'):
                img_src = page.find_all('div',itemprop='articleBody')[0].find('img').get('src')

            divs = page.find_all("div", class_ = "article-full-content")
            for div in divs:
                for para in div.find_all('p'):
                    para_content= para_content+para.get_text()+ '.  '
            try:

                if page.find_all("span", class_="article-date"):
                    dt = str(page.find_all("span", class_="article-date")[0].get_text()).split(' ')
                    published_date = str(
                        datetime.strptime(dt[0].split(',')[0][:3] + " " + dt[1] + " " + dt[2], '%b %d %Y').date())
            except:
                logger.info("Could not fetch original date putting current date")
        except Exception, e:
            logger.info("Error in body (make_body_firstpost):  " , str(e))
            pass
        return {'title':title_content.encode('ascii', 'ignore'),'para':para_content.encode('ascii', 'ignore'),'published_date':published_date,"tags":tags_content,"img_src":img_src.encode('ascii', 'ignore')}



    # iterate the list of urls for making body and indexing   which were fetched from a page articles of the website.
    #each url in the list s corresponds to a single article/news or post

    def write_pages(self,urls):
        # global no
        try:
            for source in urls:
                to_write = get_content(source)
                if to_write:
                    # print source
                    body = self.make_body(to_write)
                    make_index('gossip_bot','blogs' , body,source)
            return {"success":True}
        except Exception, e:
            print "Error in Fetching (write_pages): \n " + str(e)
            pass
            # with open("file_no"+str(post_no)+".html", "w") as file:
            #     file.write(str(to_write))
            #     post_ = post_no+1

    #scraping pages one by one and gets the posts or article in a list

    def scrap(self):
        url = "http://www.firstpost.com/tag/bollywood/page/"
        for i in range(15):
            articles = []
            logger.info( url+str(i+1))
            soup =  get_content(url+str(i+1))
            for x in soup.find_all('a'):
                 if x.get('class') and 'list-item-link' in x.get('class'):
                    articles.append(x.get('href'))
            self.write_pages(articles)
    # scrap_firstpost()
