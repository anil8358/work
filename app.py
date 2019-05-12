#!/usr/bin/env python
##  RESTful Service Used to Expose all functionalities
#   Flask used for creating Restful services
#   Usage - http://127.0.0.1:5000/review/100 (GET request gives top 100 movie reviews )
#   Usage - http://127.0.0.1:5000/latestnews/3 (Get request gives top 3 latest news from movies)
# Extracts URL first then find their shortened URLS and Images by keeping a count anf mathcing the count

from scraputil.crawl_firstpost import CrawlFirstpost
from scraputil.crawl_bollywoodlife import CrawlBollywoodlife
from scraputil.crawl_bollywood_news import CrawlBollywoodNews
from scraputil.crawl_dontcallitbollywood import CrawlDontcallitbollywood
from scraputil.crawl_masala import CrawlMasala
from scraputil.crawl_missmalini import CrawlMissmalini
from scraputil.crawl_movies import CrawlMovies
from scraputil.get_movie_review import GetMovieReview
from scraputil.crawl_movies_toi import CrawlMoviesTOI
from flask import Flask, jsonify
import gallifrey
from scraputil.utils import api_latest
from rssfeed import UpdateRSS
from scraputil import gossip_query
import config

# Using gallifrey Logger
logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

app = Flask(__name__)

aws_env = gallifrey.AWSEnvironment()
fleet = aws_env.get_fleet()


@app.route('/gossip_bot/api/query/<string:querystring>', methods=['GET'])
def queryString(querystring):
    logger.info("Gossip Query")
    query_obj = gossip_query.GossipQuery()
    logger.info("Gossip Query for: " + str(querystring))
    result = query_obj.handle_query(querystring)
    return result


@app.route('/gossip_bot/api/movie_review/<string:querystring>', methods=['GET'])
def reviewString(querystring):
    logger.info("Fetching Specific Movie Review")
    movie_review_obj = GetMovieReview()
    logger.info("Movie Review for: " + str(querystring))
    result = movie_review_obj.get_review(querystring)
    return result


# Scraping Content
@app.route('/gossip_bot/api/scrap', methods=['GET'])
def call_scraper():
    try:
        logger.info("Scrapping Web Content")
        websiteList = [CrawlMissmalini(), CrawlMovies(), CrawlBollywoodNews(), CrawlBollywoodlife(),
                       CrawlMasala(), CrawlMoviesTOI(), CrawlFirstpost(), CrawlDontcallitbollywood()]

        for website in websiteList:
            website.scrap()
            logger.info("Scrapping Normal Web Content Complete")
        return jsonify({"success": True})
    except Exception, e:
        logger.error("Error in Scrapper (call_scrapper)", str(e))
        pass
    return jsonify({"success": False})


# FETCH All Latest Movie Reviews
@app.route('/review/<int:noOfReviews>', methods=['GET'])
def getMovieReview(noOfReviews):
    logger.info("Getting Latest Movie Review")
    filename = '../Logs/BollywoodLatestMovieReviews.csv'
    logger.info("Showing Latest Movie Reviews, noOfReviews: " + str(noOfReviews))
    result = api_latest(filename, noOfReviews, "review")
    return result


# FETCH Latest News from Bollywood
@app.route('/latestnews/<int:noOfReviews>', methods=['GET'])
def getLatestMovieNews(noOfReviews):
    logger.info("Getting Latest Movie News")
    filename = '../Logs/BollywoodLatestNewsTOI.csv'
    logger.info("Showing Latest News, noOfReviews: " + str(noOfReviews))
    result = api_latest(filename, noOfReviews, "news")
    return result


@app.route('/runrssfetch', methods=['GET'])
def fetchRSS():
    try:
        logger.info("Fetching RSS feeds")
        UpdateRSS.updaterss()
    except Exception, e:
        logger.error("Could not Fetch RSS Feed", str(e))
    return jsonify({"success": True})


@app.route('/health', methods=['GET'])
def health():
    return "App is working"


if __name__ == '__main__':
    logger.info("Running Movie Gossip Bot")
    if fleet not in ['prod', 'hdfc']:
        app.run(host='0.0.0.0',threaded=True, debug=True, port=7080)
    else:
        app.run(host='0.0.0.0',threaded=True, debug=False, port=7080)
