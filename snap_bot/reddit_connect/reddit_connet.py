import praw
import json

from wells.utils import retry

from snap_bot.comments.comment import Comment  # Corrected import path

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
        Initialize the Reddit connection with provided arguments.
        
        Args:
            client_id (str): The client ID for the Reddit API.
            client_secret (str): The client secret for the Reddit API.
            user_agent (str): The user agent string to identify the application.
            username (str): The Reddit username.
            password (str): The Reddit password.
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )
    
    def get_subreddit(self):
        """
        Get the subreddit instance based on the subreddit name.
        
        Returns:
            praw.models.Subreddit: The subreddit object.
        """
        return self.reddit.subreddit(self.subreddit_name)

    @retry(Exception, tries=3, delay=2)
    def get_comments(self, limit=None):
        """
        Fetch comments from the subreddit.
        
        Args:
            limit (int, optional): The maximum number of comments to fetch. Defaults to None.
        
        Returns:
            list: A list of Comment objects.
        """
        subreddit = self.get_subreddit()
        comments = []
        for submission in subreddit.new(limit=limit):
            for comment in submission.comments.list():
                if isinstance(comment, praw.models.Comment):
                    # Ensure the comment has a valid URL
                    comment_url = f"https://www.reddit.com{comment.permalink}"
                    new_comment = Comment(
                        id=comment.id,
                        author=comment.author.name if comment.author else 'unknown',
                        body=comment.body,
                        url=comment_url
                    )
                    new_comment.update_body_with_new_issue_link()
                    comments.append(new_comment)
        return comments

    def add_comment(self, submission_id: str, comment_text: str):
        """
        Add a comment to a specific Reddit submission.
        
        Args:
            submission_id (str): The ID of the submission to comment on.
            comment_text (str): The text of the comment to post.
        """
        submission = self.reddit.submission(id=submission_id)
        submission.reply(comment_text)

    def update_comment(self, comment_id: str, new_body: str):
        """
        Update an existing Reddit comment with new content.
        
        Args:
            comment_id (str): The ID of the comment to update.
            new_body (str): The new text for the comment.
        """
        comment = self.reddit.comment(id=comment_id)
        comment.edit(new_body)

    def delete_comment(self, comment_id: str):
        """
        Delete a specific Reddit comment.
        
        Args:
            comment_id (str): The ID of the comment to delete.
        """
        comment = self.reddit.comment(id=comment_id)
        comment.delete()