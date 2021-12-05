import tweepy
import socket
import re
import logging
import sys
import configparser
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
# import preprocessor
log = logging.getLogger(__name__)

cfg = configparser.ConfigParser()
cfg.read(sys.argv[1])

# Enter your Twitter keys here!!!
ACCESS_TOKEN = cfg["KEYS"].get("access_token")#,"1457477332768370694-mtaQBaULyYQ6VgAFjEbiGk6fOluBQ9")
ACCESS_SECRET = cfg["KEYS"].get("access_secret")#,"QvN8VcaKQ8ARPblamY0o3mrWCZjBCWSktx5k1pblYT5aO")

#API key
CONSUMER_KEY = cfg["KEYS"].get("api_key")#,"O4LTSNdy1nLm2OPHekaUvnZEw")
CONSUMER_SECRET = cfg["KEYS"].get("api_secret")#,"Vhw6Q5BM0M8eVD5lndYsJn0WaRGRXzcWkbvCxdM2PWMtWhSOvu")

if len(sys.argv) < 3:
    sys.exit(2)
hashtags = set(sys.argv[2:])

TCP_IP = 'localhost'
TCP_PORT = 9001

geolocator = Nominatim(user_agent="CS4371Project")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def tags(t):
    return ['#' + tag for tag in t]

class Translator:
    def __getitem__(self, char):
        if 32 <= char and char <= 126:
            return char
        else:
            return None
translator = Translator()

def preprocessing(tweet):
    # Add here your code to preprocess the tweets and  
    # remove Emoji patterns, emoticons, symbols & pictographs, transport & map symbols, flags (iOS), etc
    return tweet.translate(translator)

def getTweet(status):
    
    # You can explore fields/data other than location and the tweet itself. 
    # Check what else you could explore in terms of data inside Status object

    tweet = ""
    location = ""
    """
    try:
        location = status.coordinates.coordinates[0] + "," + status.coordinates.coordinates[0]
    except AttributeError:
        location = None#status.user.location
    """
    #location = status.user.location
    if hasattr(status, "retweeted_status"):  # Check if Retweet
        try:
            tweet = status.retweeted_status.extended_tweet["full_text"]
        except AttributeError:
            tweet = status.retweeted_status.text
    else:
        try:
            tweet = status.extended_tweet["full_text"]
        except AttributeError:
            tweet = status.text

    loc = geocode(status.user.location)
    if loc is None: return None, None
    location = str(loc.latitude)+","+str(loc.longitude)
    
    return location, preprocessing(tweet)





# create sockets
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()

class MyStream(tweepy.Stream):
    """
    def __init__(self, *args):
        self.body = None
        super().__init__(*args)
    """
    def on_status(self, status):
        location, tweet = getTweet(status)
        if (location != None and tweet != None):
            tweetLocation = location + "\t" + tweet+"\n"
            #print(status.text)
            conn.send(tweetLocation.encode('utf-8'))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            return False
        else:
            print(status_code)
            
    def on_request_error(self, resp):
        log.error("Stream encountered HTTP error: %d", resp.status_code)
        log.error(resp.text)
    """
    def _connect(self, *args, body=None, **kwargs):
        self.body = body
        super()._connect(*args,body=body,**kwargs)
    """

myStream = MyStream(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_SECRET)
t = myStream.filter(track=tags(hashtags), languages=["en"], threaded=True)
while True:
    i = input()
    if i[0] == '!':
        if i[1:] in hashtags:
            hashtags.remove(i[1:])
            myStream.disconnect()
            t.join()
            t = myStream.filter(track=tags(hashtags), languages=["en"], threaded=True)
    elif i[0] == '/':
        if i == '/exit':
            myStream.disconnect()
            break
        if i == '/list':
            print(hashtags)
    else:
        hashtags.add(i)
        myStream.disconnect()
        t.join()
        t = myStream.filter(track=tags(hashtags), languages=["en"], threaded=True)
t.join()
