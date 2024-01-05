import re

class CommentParser:
    def __init__(self, comment):
        self.comment = comment
    
    def parse(self):
        """
        Use a simple regex pattern to find all [[xxx]] entries in the comment
        body, returning a list of the entries found
        """
        match = re.findall(r'\[\[([^]]+)\]\]', self.comment.body)
        return match