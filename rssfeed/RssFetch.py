# Used to get Links from different RSS and copy the contents to an array
# Function Names and Variables names descriptive enough to get Usage
import UrlScrape
import gallifrey
import config

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

#List of RSS Feeds to be put here

class Feeds:
    #List of RSS begins

    bollywoodLatestMovieReviews = ['http://www.bollywoodhungama.com/rss/movie-review.xml']
    bollywoodLatestNewsTOI = ['http://timesofindia.indiatimes.com/rssfeeds/1081479906.cms']
    #List of RSS ends

    # Lists used to store the links
    bollywoodLatestMovieReviewsList = []
    bollywoodLatestNewsTOIList = []


    def setBollywoodLatestMovieReviews(self):
        logger.info("Getting Movie Review")
        for itr in self.bollywoodLatestMovieReviews:
            obj = UrlScrape.url_details()
            self.bollywoodLatestMovieReviewsList = obj.getBollywoodLinks(itr)
        return self.bollywoodLatestMovieReviewsList


    def setBollywoodLatestNewsTOI(self):
        logger.info("Getting Bollywood Latest News")
        for itr in self.bollywoodLatestNewsTOI:
            obj = UrlScrape.url_details()
            self.bollywoodLatestNewsTOIList = obj.getBollywoodLinks(itr);
        return self.bollywoodLatestNewsTOIList
