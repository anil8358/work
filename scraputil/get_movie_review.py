

                    ### this script  is for geting movie reviews macthing with user query######

from flask import jsonify
# from app import app
from elasticsearch import Elasticsearch
from itertools import izip
from utils import *
from aws_es_connection.awses.connection import AWSConnection
import gallifrey
import config
#es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#es = Elasticsearch([{'host': 'https://search-zarbi-3zcgsth5c3i747ut7kzesrkt2a.us-west-2.es.amazonaws.com/', 'port': 443}])

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

# def stem_query(str):

#show_results function prints the result  on terminal as well as returns the result as list of dict
class GetMovieReview:

    def show_results(self, movies):
        count = 0
        result = []
        for movie in movies:
            count = count+1
            result.append(movie)
            logger.info("Movie Review "+str(count)+ ":\n" + str(movie))
        return jsonify({"result": result})

    #process_result function process result which came out from elastic-server and put it into a json format
    def process_result(self, res):
        posts = []
        for hit in res['hits']['hits']:
            post = {}

            if hit["_source"]['movie_title'] == "":
                post["movie"] = None
            else:
                post["movie"] = hit['_source']['movie_title']

            if hit["_source"]["title"] == "":
                post["title"] = None
            else:
                post["title"] = hit['_source']['title']

            if hit["_source"]["rating"] == "":
                post["rating"] = None
            else:
                post["rating"] = hit["_source"]["rating"]

            if hit["_source"]['review_text'] == "":
                post["review"] = None
            else:
                post["review"] = hit['_source']['review_text']

            if hit["_source"]["review_src"] == "":
                post["src"] = None
            else:
                post["src"] = hit['_source']["review_src"]

            if hit["_source"]["img_src"] == "":
                post["img_src"] = None
            else:
                post["img_src"] = hit["_source"]['img_src']

            if hit["_source"]['genre'] == "":
                post['genre'] = None
            else:
                post['genre'] = hit['_source']['genre']

            posts.append(post)
        return posts

    #get_review function queries elastic-server according to the user query and return corresponding results
    def get_review(self, query):
        global keywords_all_data

        es = Elasticsearch(connection_class=AWSConnection,
                           region= config.AWSRegion,
                           host= config.elasticSearchURI)

        res = es.search(index='movies_content', body={"query":{"bool":{"should":[{"match":{"movie_title":{"query":query,"operator":"or","fuzziness":"AUTO"}}}]}}})
        keywords_all_data = self.process_result(res)
        # print "-----------------------------------------"
        return self.show_results(keywords_all_data)


    # this portion is for running script outside the frame work

    # celeb_name = (raw_input("enter the name of movie>>>"))
    # trim_query,tokens = trimoff(celeb_name)
    # r_str = ''
    # print tokens
    # for s in tokens:
    #     r_str = r_str+s+" "
    # match_phrase(r_str)
    # print tokens
    # if len(tokens)>2:
    #     match_keywords(trim_query)
    # res = show_results()
    # get_review(celeb_name)
