from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json

es = Elasticsearch()

if __name__ == '__main__':
    print('ElasticSearch consumer listening for messages...')
    topic_name = 'tweets-kafka'

    consumer = KafkaConsumer(topic_name,
                             auto_offset_reset='latest',
                             bootstrap_servers=['localhost:9092'],
                             api_version=(0, 10),
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    for msg in consumer:

        doc = {
            'tweet': msg.value
        }
        res = es.index(index="twitter", doc_type='tweet', body=doc)
        result = es.get(index="twitter", doc_type="tweet",
                        id=res['_id'])['_source']['tweet']
        print(result)
