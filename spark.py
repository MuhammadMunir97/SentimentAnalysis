from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
# from geopy.geocoders import Nominatim
from textblob import TextBlob
from datetime import datetime
from elasticsearch import Elasticsearch
# from elasticsearch import Elasticsearch



TCP_IP = 'localhost'
TCP_PORT = 9001

def get_tweet_sentiment(tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(tweet)
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

def processTweet(tweet):

    # Here, you should implement:
    # (i) Sentiment analysis,
    # (ii) Get data corresponding to place where the tweet was generate (using geopy or googlemaps)
    # (iii) Index the data using Elastic Search 


    tweetData = tweet.split("\t")

    if len(tweetData) > 1:
        
        text = tweetData[1]
        rawLocation = tweetData[0]

        # (i) Apply Sentiment analysis in "text"
        sentiment = get_tweet_sentiment(text)

	# (ii) Get geolocation (state, country, lat, lon, etc...) from rawLocation

        print("\n\n=========================\ntweet: ", tweet)
        print("Raw location from tweet status: ", rawLocation)
        print("sentiment:", sentiment)
        # print("lat: ", lat)
        # print("lon: ", lon)
        # print("state: ", state)
        # print("country: ", country)
        # print("Text: ", text)
        # print("Sentiment: ", sentiment)



        # (iii) Post the index on ElasticSearch or log your data in some other way (you are always free!!) 
        es = Elasticsearch()

        doc = {
            'tweet': tweet,
            'geolocation': rawLocation,
            'sentiment': sentiment,
        }
        res = es.index(index="tweet-index_two", document=doc);



# Pyspark
# create spark configuration
conf = SparkConf()
conf.setAppName('TwitterApp')
conf.setMaster('local[2]')

# create spark context with the above configuration
sc = SparkContext(conf=conf)

# create the Streaming Context from spark context with interval size 4 seconds
ssc = StreamingContext(sc, 4)
#ssc.checkpoint("checkpoint_TwitterApp")

# read data from port 900
dataStream = ssc.socketTextStream(TCP_IP, TCP_PORT)


dataStream.foreachRDD(lambda rdd: rdd.foreach(processTweet))


ssc.start()
ssc.awaitTermination()
