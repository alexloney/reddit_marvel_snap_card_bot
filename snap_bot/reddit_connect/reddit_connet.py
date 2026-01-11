import praw
import json

from wells.utils import retry

from comments import Comment

class RedditConnect:
    def __init__(self, subreddit: str):
        self.subreddit_name = subreddit
        self.seen_comments = []

    def get_my_username(self):
        return self.reddit.user.me().name
    
    def init_reddit_config(self, config_file: str):
        with open(config_file) as f:
            config = json.load(f)
        
        self.init_reddit_args(
            config['client_id'],
            config['client_secret'],
            config['user_agent'],
            config['username'],
            config['password'])
    
    def init_reddit_args(self, client_id: str, client_secret: str, user_agent: str, username: str, password: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent)

        self.subreddit = self.reddit.subreddit(self.subreddit_name)
    
    @retry(times=3, interval=[1, 5, 10])
    def get_comments_shallow(self):
        comments = []
        count = 0
        for comment in self.subreddit.comments():
            count += 1
            if comment.id not in self.seen_comments:
                self.seen_comments.append(comment.id)
                comment_url = 'https://reddit.com' + comment.permalink
                github_issue_url = f"https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new?body=[Original Comment]({comment_url})"
                comments.append(Comment(comment.id, comment.author.name, comment.body, github_issue_url))
        
        while len(self.seen_comments) > 150:
            self.seen_comments.pop(0)

        return comments
    
    def get_comment_reply_author_names(self, id: str):
        comment = self.reddit.comment(id)
        comment.refresh()
        authors = []
        for reply in comment.replies.list():
            authors.append(reply.author.name)

        return authors

    @retry(times=3, interval=[1, 5, 10])
    def add_reply(self, comment_id: str, reply_text: str):
        comment = self.reddit.comment(comment_id)
        comment.reply(reply_text)
    
    def enable_readonly(self):
        self.reddit.read_only = True