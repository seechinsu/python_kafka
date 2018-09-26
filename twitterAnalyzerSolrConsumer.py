from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from kafka import KafkaConsumer
import pysolr

solr = pysolr.Solr('http://localhost:8983/solr/test', timeout=10)

solr.add([
    {
        "id": "doc_1",
        "title": "A test document",
    }]);
