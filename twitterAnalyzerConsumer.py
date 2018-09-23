from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from kafka import KafkaConsumer
from pymongo import MongoClient



client = MongoClient('mongodb://localhost:27017/')

db = client.tweets

collection = db.trump

if __name__ == '__main__':
    print('Consumer listening for messages...')
    topic_name = 'tweets-kafka'

    consumer = KafkaConsumer(topic_name,
                            auto_offset_reset='earliest',
                            bootstrap_servers=['localhost:9092'],
                            api_version=(0, 10))#, consumer_timeout_ms=1000)

    for msg in consumer:
        print(msg.value.decode('utf-8'))
