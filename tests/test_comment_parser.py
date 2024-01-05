import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from comments import Comment
from comments import CommentParser

class TestCommentParser(unittest.TestCase):
    def test_no_tags(self):
        """
        Test to ensure a comment with no tags is properly parsed and returns no
        tags.
        """
        comment = Comment('1', 'author', 'This is a test body with NO TAGS', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = []
        self.assertEqual(expected_results, results)

    def test_one_tag(self):
        """
        Test to ensure a comment with one tag is properly parsed and returns
        just the one tag
        """
        comment = Comment('1', 'author', 'This is a test [[odin]] body with one tag', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = ['odin']
        self.assertEqual(expected_results, results)

    def test_two_tags(self):
        """
        Test to ensure a comment with two tags is properly parsed and returns
        both tags
        """
        comment = Comment('1', 'author', 'This is a test [[odin]] body [[loki]] with two tags', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = ['odin', 'loki']
        self.assertEqual(expected_results, results)

    def test_misaligned_tag_closing(self):
        """
        Test to ensure a comment with inproperly aligned tag endings returns
        as expected
        """
        comment = Comment('1', 'author', 'This is a test [[odin] body with one tag', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = []
        self.assertEqual(expected_results, results)

    def test_misaligned_tag_opening(self):
        """
        Test to ensure a comment with inproperly aligned tag beginnings returns
        as expected
        """
        comment = Comment('1', 'author', 'This is a test [odin]] body with one tag', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = []
        self.assertEqual(expected_results, results)

    def test_misaligned_tag_space(self):
        """
        Test to ensure a comment with inproperly aligned tag beginnings returns
        as expected
        """
        comment = Comment('1', 'author', 'This is a test [ [odin]] body with one tag', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = []
        self.assertEqual(expected_results, results)
        
    def test_tag_at_beginning(self):
        """
        Test to ensure a comment with tag at the start returns correctly
        """
        comment = Comment('1', 'author', '[[odin]] This is a test body with one tag', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = ['odin']
        self.assertEqual(expected_results, results)
        
    def test_tag_at_ending(self):
        """
        Test to ensure a comment with tag at the end returns correctly
        """
        comment = Comment('1', 'author', 'This is a test body with one tag [[odin]]', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = ['odin']
        self.assertEqual(expected_results, results)
        
    def test_extra_slashes_from_reddit_editor(self):
        """
        Test to ensure a comment with tag at the end returns correctly
        """
        comment = Comment('1', 'author', r'This is a test \\[\\[odin\\]\\] body with one tag', 'http://example.com')
        parser = CommentParser(comment)
        results = parser.parse()

        expected_results = ['odin']
        self.assertEqual(expected_results, results)


if __name__ == '__main__':
    unittest.main()