**Usage of API :**

    http://127.0.0.1:5000/review/<No of Latest Movie Review>
    http://127.0.0.1:5000/latestnews/<No of Latest News to be fetched>
    http://127.0.0.1:5000/runrssfetch
    http://127.0.0.1:5000/gossip_bot/api/scrap
    http://127.0.0.1:5000/gossip_bot/api/movie_review/<movie-name>
    http://127.0.0.1:5000/gossip_bot/api/query/<querystring>
    
    
**run.py** file exposes all the functionalities as REST API using Flask

**app** folder contains all website crawlers and utils.py is for use of common functions for 
site specific scrapping, It also tackcles NLP and Q-A gossip bot along with all time movie reviews.

**RSSfeed** folder contains all files used for scrapping RSS and providing use of Latest News and Latest Movie Review Feature.  

**Logs** folder contains Files Storing RSS logs in files so that latest News and Latest Movie Reviews 
can be returned.
