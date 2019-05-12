                ### scraping articles from bollywoodlife####

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
class CrawlBollywoodlife(ScrapInterface):

    def make_body(self, page):
        title_content = ''
        para_content = ''
        published_date =''
        tags_content = ''
        img_src = ''
        try:
            published_date = str(datetime.now())[0:10]
            if page.find_all('div',class_="articleTtl"):
                div = page.find_all('div',class_="articleTtl")
                title_content = div[0].find("h1").get_text()+".   "+div[0].find("h2").get_text()
            if page.find('img',class_='articleImg'):
                img_src = page.find('img',class_='articleImg').get('src')

            content  = page.find_all('span',itemprop="keywords")
            for x in content:
                tags_content = tags_content+x.get_text()+"   "

            divs = page.find_all("div", class_ = "articleBody")
            for div in divs:
                for para in div.find_all('p'):
                    para_content= para_content+para.get_text()+ '.  '
            try:
                dt = str(page.find_all("span", class_="posted")[1].get_text()).strip().split(' ')
                published_date = str(
                    datetime.strptime(dt[1][:3] + " " + dt[2].split(',')[0] + " " + dt[3], '%b %d %Y').date())
            except:
                logger.info( "could not fectch original date putting current date")
        except Exception, e:
            logger.error("Error in body (make_body_bollywoodlife):  " , str(e))
            pass
        return {'title':title_content.encode('ascii', 'ignore'),'para':para_content.encode('ascii', 'ignore'),'published_date':published_date,"tags":tags_content.encode('ascii', 'ignore'),"img_src" : img_src.encode('ascii', 'ignore')}

    # make index in elastic server by makin id as src url and body as formatted above json ###

    # iterate the list of urls for making body and indexing   which were fetched from a page articles of the website.
    #each url in the list s corresponds to a single article/news or post


    def write_pages(self, urls):
        # global no
        try:
            for source in urls:
                to_write = get_content(source)
                if to_write:
                    body = self.make_body(to_write)
                    make_index('gossip_bot','blogs', body,source)
            return {"success":True}
        except Exception, e:
            logger.error("Error in Fetching (write_pages):  ", str(e))
            pass
        #     # with open("file_no"+str(post_no)+".html", "w") as file:
            #     file.write(str(to_write))
            #     post_ = post_no+1


    #scraping pages one by one and gets the posts or article in a list

    def scrap(self):
        url = "http://www.bollywoodlife.com/page/"
        for i in range(20):
            articles = []
            print url+str(i+1)
            soup = get_content(url+str(i+1))
            for x in soup.find_all('a'):
                if x.get('class') and 'hl-hp-link' in x.get('class'):
                    articles.append(x.get('href'))
            # print articles
            self.write_pages(articles)
    # scrap_bollywoodlife()
