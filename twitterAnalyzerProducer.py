from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from kafka import KafkaProducer
import settings

producer = KafkaProducer(bootstrap_servers='localhost:9092', api_version=(0, 10))
topic_name = 'tweets-kafka'

class StdOutListener(StreamListener):
    def on_data(self, data):
        dictData = json.loads(data)
        msg = 'tweet_id: {tweet_id}, tweet: {tweet}'.format(tweet_id=dictData['id'], tweet=dictData['text'])
        value = bytes(msg, encoding='utf-8')
        key = bytes('raw', encoding='utf-8')
        producer.send(topic_name, key=key, value=value)
        print('sent msg: ' + msg)
        return True

    def on_error(self, status):
        print(status)

if __name__ == "__main__":
    listener = StdOutListener()
    auth = OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)

    stream = Stream(auth, listener)

    stream.filter(track=['trump'])
