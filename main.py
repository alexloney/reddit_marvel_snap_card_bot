#!python

import praw
import json

class RedditConnect:
    def __init__(self, config_file):
        self.init_reddit(config_file)
    
    def init_reddit(self, config_file):
        with open(config_file) as f:
            config = json.load(f)
        
        self.reddit = praw.Reddit(
            client_id = config['client_id'],
            client_secret = config['client_secret'],
            username = config['username'],
            password = config['password'],
            user_agent = config['user_agent'])
    
    def get_hot_submissions(self):
        return self.reddit.subreddit('MarvelSnap').hot(limit=10)

reddit_connect = RedditConnect('config.json')

for submission in reddit_connect.get_hot_submissions():
    print(submission.title)




