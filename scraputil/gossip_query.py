

                ##### This script is for handeling user query######


from flask import jsonify
# from app import app
from elasticsearch import Elasticsearch
#from nltk.corpus import stopwords
#from nltk.tokenize import RegexpTokenizer
from itertools import izip
from utils import *
import gallifrey
import config
from aws_es_connection.awses.connection import AWSConnection

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

aws_env = gallifrey.AWSEnvironment()
fleet = aws_env.get_fleet()

class GossipQuery:

    def __init__(self):
        self.phrase_data = []
        self.keywords_all_data = []
        self.keywords_data = []
        # movie_review = {}


    # show_results function prints the result  on terminal as well as returns the result as list of dict
    def show_results(self):
        count = 0
        result = []
        phrase_url = []
        all_url = []
        # first we try to match the exact phrase if possible
        for article in self.phrase_data:

            logger.info("result :: "+str(count+1)+"\n")
            logger.info( "title :: "+article['title']+".........\n")
            logger.info("read more :: "+article['src'])
            logger.info("image-source :: "+article['img_src']+"\n")
            logger.info("........................................")
            phrase_url.append(article['src'])
            count += 1;
            result.append(article)
            if count >= 8:
                return jsonify({"result":result})

        # Then we try to match all the keywords in the phrase i.e every keyword must match
        for article in self.keywords_all_data:
            if article['src'] not in phrase_url:

                logger.info("result :: "+str(count+1)+"\n")
                logger.info("title :: "+article['title']+".........\n")
                logger.info("read more :: "+article['src'])
                logger.info("image-source :: "+article['img_src']+"\n")
                logger.info("........................................")
                count += 1;
                all_url.append(article['src'])
                result.append(article)
                if count >= 8:
                    return jsonify({"result":result})

        # Then we try to match 75 % of the keywords in the phrase
        if len(result)==0:
            for article in self.keywords_data:
                if article['src'] not in phrase_url and article['src'] not in all_url:

                    logger.info("result :: "+str(count+1)+"\n")
                    logger.info("title :: "+article['title']+"..........\n")
                    logger.info("read more :: "+article['src'])
                    logger.info("image-source :: "+article['img_src']+"\n")

                    logger.info("............................................")
                    count += 1;
                    result.append(article)
                    if count >= 8:
                        return jsonify({"result":result})

        return jsonify({"result":result})

    # process_result function process result which came out from elastic-server and put it into a json format
    def process_result(self, res):
        posts = []
        for hit in res['hits']['hits']:
            post = {'src': hit['_id'], 'title': hit['_source']['title'], 'img_src': hit['_source']['img_src']}
            posts.append(post)
        return posts

    # match the whole phrase with doc's title and tags
    def match_phrase(self, query):
        # global phrase_data
        es = Elasticsearch(connection_class=AWSConnection,
                           region= config.AWSRegion,
                           host= config.elasticSearchURI)
        # Exact Match is a Must
        res = es.search(index = 'gossip_bot', body = {"query":{"bool":{"must":[{"match_phrase":{'tags':{"query":query}}}
        ,{"match_phrase":{"title":{"query":query}}}],"should":{"range": { "published_date": {"gte" : "now-2d/d","lte":"now/d","boost":2}}}}}})
        self.phrase_data = self.process_result(res)


    # match_all_keywords matches all keywords present in the query with the documents title and tags yhen return
    # corresponding results

    def match_all_keywords(self,query):
        #global keywords_all_data
        es = Elasticsearch(connection_class=AWSConnection,
                           region= config.AWSRegion,
                           host= config.elasticSearchURI)
        # Whole query trimmed to extract keywords and query only on keywords
        res = es.search(index = 'gossip_bot', body = {"query":{"bool":{"must":[{"match":{'tags':{"query":query,
        "operator":"and","fuzziness":1}}},{"match":{"title":{"query":query,"operator":"and","fuzziness":1}}}],
        "should":{"range": { "published_date": {"gte" : "now-2d/d","lte":"now/d","boost":2}}}}}})
        self.keywords_all_data = self.process_result(res)


    # match_keywords function macthes minimum of 75% keywords with docs in title and tags from te query and return the corresponding result
    def match_keywords(self, query):
        #global keywords_data
        es = Elasticsearch(connection_class=AWSConnection,
                           region= config.AWSRegion,
                           host= config.elasticSearchURI)

        res = es.search(index = 'gossip_bot', body = {"query":{"bool":{"must":[{"match":{'tags':{"query":query,
        "operator": "or","fuzziness":"AUTO"}}},{"match":{"title":{"query":query,"operator": "or","fuzziness":"AUTO"}}}],
        "should":[{"range": { "published_date": {"gte" : "now-2d/d","lte":"now/d","boost":3}}},
        {"match":{"title":{"query":query,"operator": "and","fuzziness":"AUTO","boost":3}}},
        {"match":{"title":{"query":query,"minimum_should_match": "75%","fuzziness":"AUTO","boost":2}}}]}}})
        self.keywords_data = self.process_result(res)



    # handle_query handels the user input and sends query after trimming off to searchin in elastic server

    def handle_query(self, query):
        logger.info("Running Query")
        #trim_query,tokens = trimoff(query)
        #r_str = ''
        # tokens are received so we need to reconstruct the string, they do not have punctuations
        # Note: trim_query does not even contains stopwords
        #for s in tokens:
         #   r_str = r_str+s+" "

        # exact phrase is matched (In the query)
        self.match_phrase(query)
        # trimmed query after removing all the stopwords.
        self.match_all_keywords(query)

        # get_POS matches all the Nouns and Adjectives in the query and discards any other part of speech
        # and there get_stars() returns the query even after substituting the pet name for actor and actress
        self.match_keywords(get_stars(query))
        logger.info("Showing Results : ")
        # receives the json object after processing and returns
        res = self.show_results()
        return res

    # handle_query()
