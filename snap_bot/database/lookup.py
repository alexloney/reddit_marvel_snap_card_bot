import Levenshtein
import re

class Lookup:
    def __init__(self):
        pass

    def normalize(self, data):
        """
        Normalize a string for better searching, this will convert the string to
        lowercase and remove special characters from it.
        """
        return re.sub(r'\W+', '', data.lower())
    
    def how_close(self, str1, str2):
        """
        Determine the levenshtein distance between two strings, this is effectively
        the "edit" distance between them, how many substitutions must be made to
        one string in order for it to become the second string. A value of 0
        indicates that the two strings are identical, larger values indicate
        that they are further apart.
        """
        return Levenshtein.distance(str1, str2)

    def test_close_normalized(self, str1, str2):
        """
        Test two strings, normalizing both before testing, then return the edit
        (e.g. Levenshtein) distance between the two strings.
        """
        return self.how_close(self.normalize(str1), self.normalize(str2))