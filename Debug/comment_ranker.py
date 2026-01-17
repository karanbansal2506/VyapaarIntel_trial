import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class CommentRanker:
    """Ranks comments by score only."""

    def __init__(self, top_n: int = 3):
        """
        Initialize ranker.

        Args:
            top_n: Number of top comments to return (default 3)
        """
        self.top_n = top_n

    def is_valid_comment(self, comment: Dict[str, Any]) -> bool:
        """
        Check if comment is valid (not deleted/removed, has content).

        Args:
            comment: Comment dictionary from Reddit API

        Returns:
            True if comment is valid
        """
        body = comment.get("body", "")

        if body == "[deleted]" or body == "[removed]":
            return False

        if not body or not body.strip():
            return False

        return True

    def rank_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank comments by score and return top N.

        Args:
            comments: List of comment dictionaries

        Returns:
            Top N comments sorted by score (descending)
        """
        valid_comments = [c for c in comments if self.is_valid_comment(c)]

        if not valid_comments:
            logger.debug("No valid comments found")
            return []

        # Sort by score (descending)
        valid_comments.sort(key=lambda x: x.get("score", 0), reverse=True)

        top_comments = valid_comments[:self.top_n]

        logger.debug(f"Selected top {len(top_comments)} comments from {len(valid_comments)}")
        return top_comments

    def format_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format comment into structured dictionary.

        Args:
            comment: Comment dictionary from Reddit API

        Returns:
            Dictionary with comment data
        """
        return {
            "body": comment.get("body", ""),
            "score": comment.get("score", 0),
        }
