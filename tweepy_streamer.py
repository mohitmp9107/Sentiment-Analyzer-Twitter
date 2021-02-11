from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob 
import twitter_credentials

# # # # TWITTER CLIENT # # #
class TwitterClient():
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
    
    def get_user_timeline_tweets(self,num_tweets):
        tweets=[]
        for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
    def get_friend_list(self,num_friends):
        friend_list=[]
        for tweet in Cursor(self.twitter_user.friends,id=self.twitter_user).items(num_friends):
            friend_list.append(tweet)
        return friend_list
    
    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets=[]
        for tweet in Cursor(self.twitter_client.home_timeline,id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append((tweet))
        return home_timeline_tweets

# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.consumer_key,twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_key,twitter_credentials.access_secret)
        return auth
    

# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
        #This handles twitter authentication and connection to Twitter Streaming API.
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth,listener)
        stream.filter(track=hash_tag_list)

class TwitterListener(StreamListener):
    """
    It's a basic class that just prints received tweets to stdout
    """

    def __init__(self,fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename


    def on_data(self,data):
        try:
            print(data)
            with open(self.fetched_tweets_filename,'a') as file:
                file.write(data)
            return True
        except BaseException as e:
            print("Error on_data:%s" %str(e))
        return True
    
    def on_error(self,status):
        if status==420:
            # returning false on_data method in case of rate limits occurs
            return False
        print(status)
    
class TweetAnalyzer():
    """
    class for analyzing and categorizing contents of tweets
    """

    def clean_tweet(self,tweet):
        # removes special characters fron tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def analyze_sentiment(self,tweet):
        analysis = TextBlob(self.clean_tweet((tweet)))
        
        if analysis.sentiment.polarity >0:
            return 1
        elif analysis.sentiment.polarity ==0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self,tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets],columns=['tweets'])
        df['len']=np.array([len(tweet.text) for tweet in tweets])
        df['id']=np.array([tweet.id for tweet in tweets])
        df['date']=np.array([tweet.created_at for tweet in tweets])
        df['source']=np.array([tweet.source for tweet in tweets])
        df['likes']=np.array([tweet.favorite_count for tweet in tweets])
        df['retweets']=np.array([tweet.retweet_count for tweet in tweets])
        return df

if __name__=='__main__':
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name='elonmusk',count=50)
    
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

    # print(dir(tweets[0]))
    print(df.head(10))
    # # avg length of all tweets
    # print(np.mean(df['len']))

    # # likes for tweet with max likes 
    # print(np.max(df['likes']))

    # # retweets for tweet with max retweets
    # print(np.max(df['retweets']))

    # # time series
    # time_likes =  pd.Series(data=df['likes'].values,index=df['date'])
    # time_likes.plot(figsize=(16,4),label='likes',legend=True)

    # time_retweets = pd.Series(data=df['retweets'].values,index=df['date'])
    # time_retweets.plot(figsize=(16,4),label='retweets',legend=True)

    # plt.show()
