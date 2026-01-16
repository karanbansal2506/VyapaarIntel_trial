
import base64
import logging
import os
import time
from typing import Dict, List, Any

import requests

logger = logging.getLogger(__name__)


class RedditClient:
    """Client for interacting with Reddit API via HTTP requests."""

    def __init__(self):
        """Initialize Reddit client - uses OAuth if available, otherwise public endpoints."""
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "AIMS Reddit Ingestion Service 1.0")

        self.use_oauth = bool(self.client_id and self.client_secret)
        self.access_token = None
        self.headers = {"User-Agent": self.user_agent}

        if self.use_oauth:
            try:
                self.access_token = self._get_access_token()
                self.headers["Authorization"] = f"bearer {self.access_token}"
                logger.info("Reddit client initialized with OAuth (better rate limits)")
            except Exception as e:
                logger.warning(f"OAuth failed, falling back to public endpoints: {e}")
                self.use_oauth = False
                self.headers = {"User-Agent": self.user_agent}
        else:
            logger.info("Reddit client initialized with public endpoints (no credentials needed)")

    def _get_access_token(self) -> str:
        """Get OAuth access token from Reddit."""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        headers = {
            "Authorization": f"Basic {auth_b64}",
            "User-Agent": self.user_agent,
        }

        data = {"grant_type": "client_credentials"}

        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            headers=headers,
            data=data,
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]

    def search_subreddit(
        self, subreddit_name: str, query: str, limit: int = 5, sort: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search posts in a subreddit using Reddit's search API.

        Args:
            subreddit_name: Name of the subreddit
            query: Search query string
            limit: Maximum number of posts to fetch (default 5)
            sort: Sort method ('relevance', 'hot', 'top', 'new', 'comments')

        Returns:
            List of post dictionaries
        """
        try:
            if self.use_oauth:
                url = f"https://oauth.reddit.com/r/{subreddit_name}/search.json"
            else:
                url = f"https://www.reddit.com/r/{subreddit_name}/search.json"

            params = {
                "q": query,
                "limit": min(limit, 100),
                "sort": sort,
                "restrict_sr": "true",
                "type": "link"
            }

            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            posts = []
            for child in data.get("data", {}).get("children", []):
                if len(posts) >= limit:
                    break
                post_data = child["data"]
                posts.append(post_data)

            time.sleep(3.0 if not self.use_oauth else 1.0)
            logger.info(f"Searched r/{subreddit_name} with query '{query}': found {len(posts)} posts")
            return posts

        except Exception as e:
            logger.error(f"Error searching r/{subreddit_name} with query '{query}': {e}")
            return []

    def fetch_comments(self, post_id: str, subreddit: str) -> List[Dict[str, Any]]:
        """
        Fetch all comments for a submission.

        Args:
            post_id: Reddit post ID
            subreddit: Subreddit name

        Returns:
            List of comment dictionaries
        """
        try:
            if self.use_oauth:
                url = f"https://oauth.reddit.com/r/{subreddit}/comments/{post_id}.json"
            else:
                url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"

            response = requests.get(
                url, headers=self.headers, params={"limit": 500}, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            comments = []
            if len(data) > 1:
                comment_tree = data[1]["data"]["children"]
                comments = self._extract_comments(comment_tree)

            logger.debug(f"Fetched {len(comments)} comments for post {post_id}")
            return comments

        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {e}")
            return []

    def _extract_comments(self, tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recursively extract comments from Reddit's nested structure."""
        comments = []

        for item in tree:
            if item["kind"] == "t1":
                comment_data = item["data"]
                comments.append(comment_data)

                if "replies" in comment_data and comment_data["replies"]:
                    if isinstance(comment_data["replies"], dict):
                        replies_tree = comment_data["replies"]["data"]["children"]
                        comments.extend(self._extract_comments(replies_tree))

        return comments
