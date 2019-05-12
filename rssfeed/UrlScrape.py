#   This file has some variations for scrapping different RSS

import requests
from BeautifulSoup import BeautifulSoup
import re
from urlparse import urlparse
import gallifrey
import config

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

class url_details(object):

  # Used for making Http request to a URL
  def getUrlContent(self, url):
    try:
        response = requests.get(url)
    except Exception as e:
        logger.error( "Error Making Connection to the Requested Website :" + url,  str(e))
    return response

  # Used for getting beautiful soup contents of a HTML page
  def getSoupContent(self, url) :
    html = self.getUrlContent(url)
    html = html.content
    soup = BeautifulSoup(html)
    return soup,soup.prettify()

  # Used to get links if they are within <a href="" > kind of Tag
  def getContainedUrl(self, url):
    soup, preety_soup = self.getSoupContent(url)
    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))
    logger.info( links)
    return links

  # Used to filter proper URLs according to needs with use of REGEX, stray links are removed here
  def getContainedUrl2(self, url):
    soup, preety_soup = self.getSoupContent(url)
    links = []
    soup = soup.text
    urls = re.findall(r'href=[\'"]?([^\'" >]+)', soup) # Used to find Urls using regex
    for j in urls:
      parsed_uri = urlparse(j)
      domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri) # Finding domain of the Url
      if( domain.__contains__('bollywoodhungama') or domain.__contains__("timesofindia")): # Checking no other stray domain Url do not come in our Results
       links.append(j)
    return links

  # Acts as a central caller to All above functions. Can be used to check intermediate result of functions
  def getBollywoodLinks(self, url):
    links = self.getContainedUrl2(url)
    return links
