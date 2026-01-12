#!python

import datetime
import logging
import argparse
import os
import sys
import time

from database import Database, Card
from reddit_connect import RedditConnect
from comments import CommentParser
import utils

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO)
logging.captureWarnings(True)

class SnapBot:
    def __init__(self, subreddit, config_file, db_update_timeout,
                 max_fuzzy_distance, exact_match_threshold, dry_run, debug,
                 client_id, client_secret, user_agent, reddit_username, reddit_password):
        self.subreddit = subreddit
        self.config_file = config_file
        self.db_update_timeout = db_update_timeout
        self.max_fuzzy_distance = max_fuzzy_distance
        self.exact_match_threshold = exact_match_threshold
        self.dry_run = dry_run
        self.debug = debug
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password

        self.database = Database(config_file)
        self.comment_parser = CommentParser(max_fuzzy_distance, exact_match_threshold)
        self.reddit_connect = RedditConnect(client_id, client_secret, user_agent, reddit_username, reddit_password)

    def run(self):
        logging.info('Starting Reddit bot')
        try:
            for comment in self.reddit_connect.stream_comments(self.subreddit):
                if self.dry_run:
                    logging.info(f'Dry run: Processing comment {comment.id}')
                else:
                    logging.info(f'Processing comment {comment.id}')

                parser = CommentParser(comment)
                results = parser.parse()

                if not results:
                    continue

                # Construct the response message
                response_message = "Here are the cards you requested:\n"
                for result in results:
                    card = self.database.get_card_by_name(result, self.max_fuzzy_distance, self.exact_match_threshold)
                    if card:
                        response_message += f"- {card.name}: {card.description}\n"
                    else:
                        response_message += f"- No card found matching '{result}'\n"

                # Construct the GitHub issue link with pre-filled body
                github_issue_url = "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new"
                if comment.url:
                    github_issue_url += f"?body=[Original Comment]({comment.url})"
                else:
                    logging.warning(f"Comment {comment.id} does not have a URL. Skipping pre-filled body.")

                response_message += f"\nIf you encounter any issues, please [report here]({github_issue_url})."

                # Post the response
                if not self.dry_run:
                    comment.reply(response_message)
                    logging.info(f'Replied to comment {comment.id}')

        except Exception as e:
            logging.error(f'An error occurred: {e}')
            time.sleep(60)  # Wait for a minute before retrying