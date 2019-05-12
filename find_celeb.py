
### this script is for celebrity profile but currently not in use


from flask import jsonify
import scraputil
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from itertools import izip
from aws_es_connection.awses.connection import AWSConnection
import gallifrey
import config

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

class find_celeb:

    def show_results(self, dic):
        phrase_keys = dic.keys()
        phrase_values = dic.values()
        count = 0
        for out_key,out_value in izip(phrase_keys,phrase_values):
            count = count+1
            logger.info(out_key+" :: "+out_value)
        if count==0:
            logger.info("NOTHING found")


    def process_result(self, res):
        posts = {}
        for hit in res['hits']['hits']:
            posts["celebrity"] = hit['_source']['celebrity']
            posts["news"] = hit['_source']['para']
            posts["read-more"] = hit['_id']
            posts["news_title"] = hit['_source']['title']
            posts["img_src"] = hit["_source"]['img_src']
        # print posts
        return posts


    def match_all_keywords(self, query):
        global keywords_all_data

        es = Elasticsearch(connection_class=AWSConnection,
                           region= config.AWSRegion,
                           host= config.elasticSearchURI)

        res = es.search(index = 'gossip_bot_celeb', body = {"query":{"match":{"celebrity":{"query":query,"operator":"and","fuzziness":"AUTO"}}}})
        keywords_all_data = self.process_result(res)
        self.show_results(keywords_all_data)


    celeb_name = (raw_input("enter the name of celeb>>>"))
    match_all_keywords(celeb_name)
