#   This file writes the links to the a file inside the Logs folder.
#   It calls necessary methods from RssFetch file to write in proper file
#   It also compresses in form of Tinyurl
#   Run this file periodically to Update the RSS
#   Example Usage - python UpdateRSS.py
#   Author - ayush_awasthi
# fp is file pointer to Full Url files
# fp2 is the pointer to Shortened Url files
# fp3 is for title from the URL
# fp4 is for writing image URL
import RssFetch
import csv
import imageExtractor
import TitleFetcher
import gallifrey
import config
from elasticsearch import Elasticsearch
from aws_es_connection.awses.connection import AWSConnection


# Using gallifrey Logger
logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

tardis_inst = gallifrey.Tardis()
suggestiveBaseURI = tardis_inst.get_resource_url("ElasticSearchAWSInstance")

def updaterss():

    try:
        feeds = RssFetch.Feeds()
        image = imageExtractor.ImageExtractor()

        def fetchRSS(fileName, feedsType):
            fp = open(fileName, 'w+')
            wr = csv.writer(fp)

            try:
                for items in feedsType:
                    link = str(items)

                    # Get Movie Title
                    try:
                        title = TitleFetcher.getLinkTitle2(str(link))

                        # Changing first small letter to Capital
                        if 97 <= ord(title[0]) <= 122:
                            title = chr(ord(title[0]) - 32) + title[1:len(title)]
                    except:
                        logger.info("No Title found")
                        title = None

                    # Get Image Link
                    try:
                        imgsrc = image.getBollywoodImage(link)
                    except:
                        logger.info("No Image found for: " + title)
                        imgsrc = None

                    # For Latest Movie Review, fetch Rating from ES
                    if feedsType == feeds.setBollywoodLatestMovieReviews():
                        try:
                            rating = str(match_keywords(title))
                        except:
                            logger.info("No rating found for: " + title)
                            rating = None

                        wr.writerow([items, title, imgsrc, rating])

                    # Fetching Latest TOI News
                    else:
                        wr.writerow([items, title, imgsrc])

                fp.close()
            except Exception as e:
                logger.info("Error in (updaterss)", str(e))

        # Movie Review
        fetchRSS("Logs/BollywoodLatestMovieReviews.csv", feeds.setBollywoodLatestMovieReviews())

        # TOI News
        fetchRSS("Logs/BollywoodLatestNewsTOI.csv", feeds.setBollywoodLatestNewsTOI())

    except Exception as e:
        logger.error("Error in writing to a file", str(e))


def match_keywords(query):
    es = Elasticsearch(connection_class=AWSConnection,
                       region= config.AWSRegion,
                       host= config.elasticSearchURI)

    res = es.search(index='movies_content', body={"query": {
        "bool": {"should": [{"match": {"movie_title": {"query": query, "operator": "or", "fuzziness": "AUTO"}}}]}}})
    keywords_data = process_result(res)[0]['rating']
    return keywords_data


def process_result(res):
    posts = []
    for hit in res['hits']['hits']:
        post = {"movie": hit['_source']['movie_title'], "rating": hit["_source"]["rating"]}
        posts.append(post)
    return posts

