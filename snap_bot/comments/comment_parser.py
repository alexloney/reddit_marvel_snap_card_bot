import re

from . import Comment

class CommentParser:
    def __init__(self, comment: Comment):
        self.comment = comment
    
    def parse(self):
        """
        Use a simple regex pattern to find all [[xxx]] entries in the comment
        body, returning a list of the entries found. Also, modify any GitHub URLs
        to include a reference back to the original comment.
        """
        matches = re.findall(r'\\?\\?\[\\?\\?\[([^]\\]+)\\?\\?\]\\?\\?\]', self.comment.body)
        
        # Modify GitHub URLs to include a reference back to the original comment
        modified_matches = []
        for match in matches:
            if 'github.com' in match and '?ref=' not in match:
                modified_match = f"{match}?ref={self.comment.url}"
                modified_matches.append(modified_match)
            else:
                modified_matches.append(match)
        
        return modified_matches