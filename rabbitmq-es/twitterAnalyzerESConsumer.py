from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import pika
from elasticsearch import Elasticsearch
import settings

es = Elasticsearch()

if __name__ == '__main__':
    credentials = pika.PlainCredentials('user','bitnami')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange='twitter', exchange_type='fanout', durable=True)
    channel.queue_declare(queue='twitter-es-pika', durable=True)
    channel.queue_bind(exchange='twitter', queue='twitter-es-pika')

    print('Listening for messages...')

    def callback(ch, method, properties, body):
        doc = {
            'tweet': json.loads(body)
        }
        res = es.index(index="twitter", doc_type='tweet', body=doc)
        result = es.get(index="twitter", doc_type="tweet", id=res['_id'])['_source']['tweet']
        print(result)

    channel.basic_consume(callback, queue='twitter-es-pika', no_ack=True)
    channel.start_consuming()
