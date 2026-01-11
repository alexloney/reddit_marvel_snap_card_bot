import praw
import json

from wells.utils import retry

from comments import Comment

class RedditConnect:
    def __init__(self, subreddit: str):
        self.subreddit_name = subreddit
        self.seen_comments = []

    def get_my_username(self):
        """
        Get the username of the account running that is running. No need for an
        extra query here to Reddit since we know the username from the config
        file, so instead we will just use what we logged in with.
        """
        return self.reddit.user.me().name
    
    def init_reddit_config(self, config_file: str):
        """
        Initialize the Reddit connection, use the details stored in the config
        file to initiate a connection to Reddit
        """
        with open(config_file) as f:
            config = json.load(f)
        
        self.init_reddit_args(
            config['client_id'],
            config['client_secret'],
            config['user_agent'],
            config['username'],
            config['password'])
    
    def init_reddit_args(self, client_id: str, client_secret: str, user_agent: str, username: str, password: str):
        """
        Initialize the Reddit connection using the supplied details
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent)

        self.subreddit = self.reddit.subreddit(self.subreddit_name)
    
    @retry(times=3, interval=[1, 5, 10])
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
                comment_url = 'https://reddit.com' + comment.permalink
                github_issue_link = f"https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new?body=[Original Comment]({comment_url})"
                comments.append(Comment(comment.id, comment.author.name, comment.body, comment_url, github_issue_link))
        
        # To prevent this list from simply growing to an unmanagable size, we
        # will simply remove old entries when it has more than 150, since the
        # query above only returns the past 100, this should be fine.
        while len(self.seen_comments) > 150:
            self.seen_comments.pop(0)

        return comments
    
    def get_comment_reply_author_names(self, id: str):
        """
        Fetch the names of the authors for a given comment.
        """
        comment = self.reddit.comment(id)
        comment.refresh()
        authors = []
        for reply in comment.replies.list():
            authors.append(reply.author.name)

        return authors

    @retry(times=3, interval=[1, 5, 10])
    def add_reply(self, comment_id: str, reply_text: str):
        """
        Load a specific comment by ID and submit a reply to it
        """
        comment = self.reddit.comment(comment_id)
        comment.reply(reply_text)
    
    def enable_readonly(self):
        """
        Enable read-only mode, useful for dry run
        """
        self.reddit.read_only = True
```

Note: The `Comment` class in the `comments.py` file should be updated to accept and store the `github_issue_link` if it is not already doing so.