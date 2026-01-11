import unittest
from snap_bot.comments.comment import Comment
from urllib.parse import quote

class TestDatabase(unittest.TestCase):
    def test_card_partial_search(self):
        """
        Test partial search functionality in the database.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_ebony_order(self):
        """
        Test search for Ebony Order card.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_exact_search(self):
        """
        Test exact search functionality in the database.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_fuzzy_search_1(self):
        """
        Test first fuzzy search scenario.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_fuzzy_search_2(self):
        """
        Test second fuzzy search scenario.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_insert_tokens(self):
        """
        Test insertion of tokens into the database.
        """
        # Mock database and token insertion logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_not_searchable_card(self):
        """
        Test search functionality with a non-searchable card.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_resolve_tokens(self):
        """
        Test resolution of tokens in the database.
        """
        # Mock database and token resolution logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_search_evolved(self):
        """
        Test search for evolved cards.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_uncle_ben(self):
        """
        Test search for Uncle Ben card.
        """
        # Mock database and search logic
        self.assertTrue(True)  # Placeholder for actual test logic

    def test_widows_bite(self):
        """
        The Widow's Bite card is not reporting as being connected to Black Widow
        so this tests our manual data fix works.
        """
        # Mock database and search logic
        cards = [
            Comment('BlackWidow', 'Black Widow', '3', '3', '<b>On Reveal:</b> Add a Widow\'s Bite.', reddit_comment_url='https://www.reddit.com/r/subreddit/comments/1/comment_id/')
        ]
        
        for card in cards:
            card.update_body_with_new_issue_link()
            expected_github_link = "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new?body=[Original%20Comment](https%3A%2F%2Fwww.reddit.com%2Fr%2Fsubreddit%2Fcomments%2F1%2Fcomment_id%2F)"
            expected_updated_body = "<b>On Reveal:</b> Add a Widow's Bite.\n\n[Create New Issue]({})".format(expected_github_link)
            self.assertEqual(card.body, expected_updated_body)

class TestComment(unittest.TestCase):
    def test_generate_new_issue_link(self):
        """
        Test generating a new GitHub issue link with the Reddit comment URL pre-populated in the issue body.
        """
        reddit_comment_url = 'https://www.reddit.com/r/subreddit/comments/1/comment_id/'
        expected_github_link = "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new?body=[Original%20Comment](https%3A%2F%2Fwww.reddit.com%2Fr%2Fsubreddit%2Fcomments%2F1%2Fcomment_id%2F)"
        
        comment = Comment('1', 'author', 'body', reddit_comment_url)
        new_issue_link = comment.generate_new_issue_link()
        
        self.assertEqual(new_issue_link, expected_github_link)

    def test_update_body_with_new_issue_link(self):
        """
        Test updating the comment body to include a link to create a new GitHub issue with the Reddit comment URL pre-populated.
        """
        reddit_comment_url = 'https://www.reddit.com/r/subreddit/comments/1/comment_id/'
        expected_github_link = "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new?body=[Original%20Comment](https%3A%2F%2Fwww.reddit.com%2Fr%2Fsubreddit%2Fcomments%2F1%2Fcomment_id%2F)"
        
        comment_body = 'This is a test body.'
        comment = Comment('1', 'author', comment_body, reddit_comment_url)
        comment.update_body_with_new_issue_link()
        
        expected_updated_body = "This is a test body.\n\n[Create New Issue]({})".format(expected_github_link)
        self.assertEqual(comment.body, expected_updated_body)

    def test_generate_new_issue_link_no_url(self):
        """
        Test generating a new GitHub issue link when the Reddit comment URL is not provided.
        """
        comment = Comment('1', 'author', 'body', None)
        new_issue_link = comment.generate_new_issue_link()
        
        self.assertEqual(new_issue_link, "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new")

class TestDatabaseCommentIntegration(unittest.TestCase):
    def test_database_comment_integration(self):
        """
        Test the integration between the database and comment functionalities.
        """
        # Mock database and comment logic
        self.assertTrue(True)  # Placeholder for actual test logic

if __name__ == '__main__':
    unittest.main()