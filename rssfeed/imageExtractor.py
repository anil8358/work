#Logic for Image Extraction from a web page , uses meta with og:image property
import UrlScrape
import gallifrey
import config

logger = gallifrey.Logger(
    application_name='{}.{}'.format(config.APPLICATION_NAME, __name__),
    filename=config.LOG_FILE_NAME
)


class ImageExtractor:
    def getBollywoodImage(self, url):
        obj = UrlScrape.url_details()
        soup, preety = obj.getSoupContent(url)
        ret = []
        metadata = soup.findAll('meta', {'property' : 'og:image'})
        for img in metadata:
            urlstr = img['content']
            ret.append(urlstr)
        return str(ret[0])
