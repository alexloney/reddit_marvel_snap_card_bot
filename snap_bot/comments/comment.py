class Comment:
    def __init__(self, id: str, author: str, body: str, url: str):
        self.id = id
        self.author = author
        self.body = body
        self.url = url

    def generate_new_issue_link(self) -> str:
        """
        Generate a new GitHub issue link with the Reddit comment URL pre-populated in the issue body.
        
        Returns:
            str: The formatted GitHub issue creation URL.
        """
        github_base_url = "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new"
        if self.url:
            # Ensure the Reddit URL is properly encoded
            import urllib.parse
            encoded_url = urllib.parse.quote(self.url, safe='')
            return f"{github_base_url}?body=[Original Comment]({encoded_url})"
        else:
            return github_base_url

    def update_body_with_new_issue_link(self) -> None:
        """
        Update the comment body to include a link to create a new GitHub issue with the Reddit comment URL pre-populated.
        """
        new_issue_link = self.generate_new_issue_link()
        self.body += f"\n\n[Create New Issue]({new_issue_link})"