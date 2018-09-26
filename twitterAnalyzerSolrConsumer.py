from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from kafka import KafkaConsumer
import pysolr

solr = pysolr.Solr('http://localhost:8983/solr/test', timeout=10)

if __name__ == '__main__':
    print('Consumer listening for messages...')
    topic_name = 'tweets-kafka'
    consumer = KafkaConsumer(topic_name,
                            auto_offset_reset='earliest',
                            bootstrap_servers=['localhost:9092'],
                            api_version=(0, 10),
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    for msg in consumer:
        result = solr.add([msg.value])
        print(result);
