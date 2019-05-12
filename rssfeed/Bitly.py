import requests
import gallifrey
import config
logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)

# Access Token for Single User , does not use OAuth flow as we do not require user specific compression
ACCESS_TOKEN_OF_BITLY = '2e4b646a6261ef2302b441687d353bf454b76f89'

# Bitly Url Compressor
def getTinyUrl(url):

    hitUrl = 'https://api-ssl.bitly.com/v3/shorten?access_token=' + ACCESS_TOKEN_OF_BITLY + '&longUrl=' + url + '&format=txt'
    logger.info("Getting Tiny URL")
    response = requests.get(hitUrl)
    return response.text

