
###### for use of common functions######
import os

from flask.json import jsonify
#from nltk.corpus import stopwords
#from nltk.tokenize import RegexpTokenizer
from textblob import TextBlob
import urllib
from bs4 import BeautifulSoup
import mechanize
from itertools import izip
from elasticsearch import Elasticsearch, RequestsHttpConnection
import mechanicalsoup
from aws_es_connection.awses.connection import AWSConnection
import pandas as pd
import gallifrey
import config

# Using gallifrey Logger
logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

# Mapper for Names to thir pet name used to refine search
stars = {"Salman khan":["sallu bhai","sallu","bhai"]
,"Shah rukh khan":["king khan","SRK"],
"Sahid kapoor":["chocolate boy"],
"Kareena kapoor":["bebo"],"Hrithik roshan":["dance icon"],"Amitabh bachchan":["Big B"]}


# trimoff function is for removing stopwords from query and finding keywords
'''
def trimoff(string):
    stop_words = set(stopwords.words('english'))
    str_token = remove_punctuation(string)
    filtered_words = [word for word in str_token if word not in stop_words]
    keywords = ''
    for word in filtered_words:
        keywords = keywords + word + " "
    return keywords, str_token


# remove_punctuation function removes the punctuation from query
def remove_punctuation(string):
    tokenizer = RegexpTokenizer(r'\w+')
    str_token = tokenizer.tokenize(string)
    return str_token

'''
# get_content_mechanize function is for getting data from the webpage
# which does not have access through scripts to scrap data so it behaves as a Browser
# and fetch the content from thi given url
def get_content_mechanize(to_scrap):
    try:
        # br = mechanize.Browser()
        # br.set_handle_robots(False)
        # br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        # resp = br.open(to_scrap)
        # data = resp.read()  # content

        br = mechanicalsoup.Browser();
        data = br.get(to_scrap).content

        try:
            l_soup = BeautifulSoup(data, "lxml")
        except Exception, e:
            print "Exception Caught: \n " + str(e)

        return l_soup
    except Exception, e:
        print "ERROR in Fetching (get_content_mechanize): \n " + str(e)
        pass


# get_content is for fetching web page simply through request which has permission to scrap data
def get_content(to_scrap):
    try:
        data =urllib.urlopen(to_scrap).read()
        l_soup = BeautifulSoup(data, 'lxml')
        return l_soup
    except Exception, e:
        print "Error in Fetching (get_content): \n " + str(e)
        pass


# this function is for getting pos tags of query
'''
def get_POS(query):
    try:
        pos = TextBlob(query)
        res = []
        for word in pos.tags:
            if word[1] in ['NNP', 'NN', 'JJ']:
                res.append(word[0])
        return ' '.join(res)

    except Exception, e:
        print "Error in Fetching (get_POS): \n " + str(e)
        pass
'''

# this function is for getting names through nick names of stars from the above mapped dictionary
def get_stars(query):
    # print query
    try:
        for key, value in izip(stars.keys(),stars.values()):
            for val in value:
                if val in query:
                    query = query.replace(val,key)
                    break
        return query
    except Exception, e:
        print "Error in Fetching (get_stars): \n " + str(e)
        pass


def make_index(idx, doc, index_body,source_url):
    es = Elasticsearch(connection_class=AWSConnection,
                       region= config.AWSRegion,
                       host= config.elasticSearchURI)

    # es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    es.index(index=idx, doc_type=doc, id=source_url, body=index_body)
    print "index_created for----->>" + str(source_url)


def api_latest(filename, noOfReviews, type):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    fp = pd.read_csv(filepath, delimiter=",", header=None)
    obj = []
    views = 0

    for line in fp[0]:
        line = str(line)
        line = line.replace('\n', '')
        line = line.replace('\r', '')

        if line.count('http'):  # Remove any line that may not be a valid URL
            views = views + 1
            temp = {}
            views2 = 0

            for line2 in fp[1]:
                line2 = line2.replace('\n', '')
                line2 = line2.replace('\r', '')
                if views2 == (views - 1):
                    temp['title'] = line2
                    break

                views2 = views2 + 1;

            views3 = 0
            for line3 in fp[2]:
                line3 = str(line3)
                line3 = line3.replace('\n', '')
                line3 = line3.replace('\r', '')
                line3.replace('[', '')
                line3.replace(']', '')

                if views3 == (views - 1):
                    if line3 == "nan":
                        temp['img_src'] = None
                    else:
                        temp['img_src'] = line3
                    break

                views3 = views3 + 1;

            if type == "review":
                views4 = 0
                for line4 in fp[3]:
                    line4 = str(line4)
                    line4 = line4.replace('\n', '')
                    line4 = line4.replace('\r', '')

                    if views4 == (views - 1):
                        if line4 == "nan":
                            temp['rating'] = None
                        else:
                            temp['rating'] = line4
                        break

                    views4 = views4 + 1;

            temp['src'] = line
            obj.append(temp)

            if views == noOfReviews:  # Keeps track of no of reviews to be given to User
                break

    logger.info("Latest " + type.title() + " Result: \n" + str(obj))
    # Packs all URLs into a single json object
    return jsonify({"result": obj})
