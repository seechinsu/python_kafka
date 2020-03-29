from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import KafkaProducer
import json
import yaml

settings = yaml.safe_load(open("settings.yaml"))

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         api_version=(0, 10),
                         key_serializer=lambda k: json.dumps(
                             k).encode('utf-8'),
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
topic_name = 'tweets-kafka'


class StdOutListener(StreamListener):
    def on_data(self, data):
        dictData = json.loads(data)
        if dictData.get('id'):
            value = {'tweet_id': dictData['id'], 'tweet': dictData['text']}
            key = 'raw'
            producer.send(topic_name, key=key, value=value)
            print(value)
            return True
        else:
            print(dictData)

    def on_error(self, status):
        print(status)


if __name__ == "__main__":
    listener = StdOutListener()
    auth = OAuthHandler(settings['CONSUMER_KEY'], settings['CONSUMER_SECRET'])
    auth.set_access_token(settings['ACCESS_TOKEN'],
                          settings['ACCESS_TOKEN_SECRET'])

    stream = Stream(auth, listener)

    stream.filter(track=['Trump'])
