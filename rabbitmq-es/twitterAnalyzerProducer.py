from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import pika
import settings

credentials = pika.PlainCredentials('user','bitnami')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='twitter', exchange_type='fanout', durable=True)
channel.queue_declare(queue='twitter-mongo-pika', durable=True)

class StdOutListener(StreamListener):
    def on_data(self, data):
        dictData = json.loads(data)
        try:
            value = {'tweet': dictData['text']}
        except KeyError:
            value = {'tweet': 'blank tweet'}
        channel.basic_publish(exchange='twitter', routing_key='', body=json.dumps(value))
        print(value)
        return True

    def on_error(self, status):
        print(status)

if __name__ == "__main__":
    listener = StdOutListener()
    auth = OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)

    stream = Stream(auth, listener)

    stream.filter(track=['marvel', 'trump', 'facebook'])
