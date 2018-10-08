from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import pika
from pymongo import MongoClient
import settings


client = MongoClient('mongodb://localhost:27017/')
db = client.tweets
collection = db.test

if __name__ == '__main__':
    credentials = pika.PlainCredentials('user','bitnami')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange='twitter', exchange_type='fanout', durable=True)
    channel.queue_declare(queue='twitter-mongo-pika', durable=True)
    channel.queue_bind(exchange='twitter', queue='twitter-mongo-pika')

    print('Listening for messages...')

    def callback(ch, method, properties, body):
        result = collection.insert_one(json.loads(body))
        print(collection.find_one({'_id': result.inserted_id}))

    channel.basic_consume(callback, queue='twitter-mongo-pika', no_ack=True)
    channel.start_consuming()
