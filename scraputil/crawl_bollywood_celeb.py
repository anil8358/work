
##### this script is for scraping celebrities profiles but currently not in use ########

import urllib
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify
from datetime import datetime
# import unicodedata
from utils import *
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
class CrawlBollywoodCeleb(ScrapInterface):

    def make_body(self, page):
        bio_text = ''
        read_more = ''
        recent_movies = ''
        celeb_name = ''
        img_src = ''

        try:
            celeb_name = str(page.find('h1' ,class_='celebrities').get_text())
            bio_text = page.find_all('div' ,class_='field-content')[0].find('p').get_text()
            read_more = 'www.bollywood.com'+ page.find_all('div', class_='views-field views-field-phpcode')[1].find(
                'a').get('href')
            movies = page.find_all('td')
            for mv in movies:
                if len(mv.get_text()) > 1:
                    recent_movies = recent_movies + mv.get_text() + ',   '

        except Exception, e:
            logger.error("ERROR in body - ", str(e))
        return {'title': celeb_name, 'bio_content': bio_text, 'biography_src': read_more, "movies": recent_movies}

    def write_pages(self, urls):
        for source in urls:
            to_write = get_content_mechanize(source)
            if to_write:
                body = self.make_body(to_write)
                make_index('gossip_bot_celeb', 'profiles', body, source)
        return {"success": True}
        # except:
        #     pass
        # # with open("file_no"+str(post_no)+".html", "w") as file:
        #     file.write(str(to_write))
        #     post_ = post_no+1

    def scrap(self):
        url = "http://www.bollywood.com/celebrities?page="
        for i in range(15):
            articles = []
            logger.info( url + str(i))
            soup = get_content_mechanize(url + str(i))
            divs = soup.find_all('div', class_='contentmain')[0].find_all('div', class_='views-field views-field-title')
            logger.info( len(divs))
            for div in divs:
                if div.find('a'):
                    src = 'http://www.bollywood.com' + div.find('a').get('href')
                    articles.append(src)
            self.write_pages(articles)
