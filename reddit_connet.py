import praw
import json

from comment import Comment

class RedditConnect:
    def __init__(self, subreddit, config_file):
        self.subreddit_name = subreddit
        self.username = ''
        self.init_reddit(config_file)

        self.seen_comments = []

    def get_my_username(self):
        """
        Get the username of the account running that is running. No need for an
        extra query here to Reddit since we know the username from the config
        file, so instead we will just use what we logged in with.
        """
        return self.username
    
    def init_reddit(self, config_file):
        """
        Initialize the Reddit connection, use the details stored in the config
        file to initiate a connection to Reddit
        """
        with open(config_file) as f:
            config = json.load(f)
        
        self.reddit = praw.Reddit(
            client_id = config['client_id'],
            client_secret = config['client_secret'],
            username = config['username'],
            password = config['password'],
            user_agent = config['user_agent'])

        self.subreddit = self.reddit.subreddit(self.subreddit_name)

        self.username = config['username']
    
    def get_comments_shallow(self):
        """
        Get a list of comments, these may repeat as it pulls the last 100 comments
        each time it runs, so when we query again, we may get comments we've
        already seen. Because of that, we are using a `seen_comments` variable
        to keep track of comments we have already seen to prevent sending those
        back up to the caller
        """
        comments = []
        count = 0
        for comment in self.subreddit.comments():
            count += 1
            if comment.id not in self.seen_comments:
                self.seen_comments.append(comment.id)
                comments.append(Comment(comment.id, comment.body, 'https://reddit.com' + comment.permalink))
        
        # To prevent this list from simply growing to an unmanagable size, we
        # will simply remove old entries when it has more than 150, since the
        # query above only returns the past 100, this should be fine.
        while len(self.seen_comments) > 150:
            self.seen_comments.pop(0)

        return comments
    
    def get_comment_reply_author_names(self, id):
        """
        Fetch the names of the authors for a given comment.
        """
        comment = self.reddit.comment(id)
        comment.refresh()
        authors = []
        for reply in comment.replies.list():
            authors.append(reply.author.name)

        return authors

    def add_reply(self, comment_id, reply_text):
        comment = self.reddit.comment(comment_id)
        comment.reply(reply_text)
