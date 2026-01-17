import json
import logging
import os
import sys
from typing import Dict, List, Any

from dotenv import load_dotenv

from comment_ranker import CommentRanker
from reddit_client import RedditClient

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RedditIngestionService:
    """Main service orchestrating Reddit data ingestion."""

    def __init__(self):
        """Initialize service with Reddit client."""
        self.reddit_client = RedditClient()

    def process_post(self, post: Dict[str, Any], comment_limit: int = 3) -> Dict[str, Any]:
        """
        Process a single post: extract data and fetch top comments.

        Args:
            post: Post dictionary from Reddit API
            comment_limit: Number of top comments to return (default 3)

        Returns:
            Dictionary with post data and top comments
        """
        post_id = post.get("id", "")
        subreddit = post.get("subreddit", "")

        # Fetch comments
        comments = self.reddit_client.fetch_comments(post_id, subreddit)
        
        # Rank comments by score
        ranker = CommentRanker(top_n=comment_limit)
        top_comments = ranker.rank_comments(comments)

        # Format comments
        formatted_comments = [ranker.format_comment(c) for c in top_comments]

        return {
            "title": post.get("title", ""),
            "url": f"https://reddit.com{post.get('permalink', '')}",
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "top_comments": formatted_comments,
        }

    def process_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete ingestion request.

        Args:
            input_data: Input JSON dictionary

        Returns:
            Output JSON dictionary with results
        """
        # Extract query from keywords array (combine into single query string)
        keywords = input_data.get("keywords", [])
        # query = " ".join(keywords) if keywords else input_data.get("query", "")
        
        target_subreddits = input_data.get("target_subreddits", [])
        posts_limit = input_data.get("posts_limit_per_subreddit", 5)
        comment_limit = input_data.get("comments_limit_per_post", 3)

        # Default to 5 posts if not specified or too high
        posts_limit = min(posts_limit, 5) if posts_limit else 5

        logger.info(
    f"Processing request: {len(keywords)} keywords, "
    f"{len(target_subreddits)} subreddits, "
    f"{posts_limit} posts per subreddit, "
    f"{comment_limit} comments per post"
)




        results = []

        # for subreddit_name in target_subreddits:
        #     try:
        #         # Search subreddit with query
        #         posts = self.reddit_client.search_subreddit(
        #             subreddit_name, query=query, limit=posts_limit, sort="relevance"
        #         )

        #         if not posts:
        #             logger.warning(f"No posts found in r/{subreddit_name} for query '{query}'")
        #             continue

        #         # Process each post
        #         processed_posts = []
        #         for post in posts:
        #             try:
        #                 processed_post = self.process_post(post, comment_limit=comment_limit)
        #                 processed_posts.append(processed_post)
        #             except Exception as e:
        #                 logger.error(f"Error processing post {post.get('id', 'unknown')}: {e}")
        #                 continue

        #         if processed_posts:
        #             results.append({
        #                 "subreddit": subreddit_name,
        #                 "posts": processed_posts
        #             })

        #     except Exception as e:
        #         logger.error(f"Error processing subreddit {subreddit_name}: {e}")
        #         continue

        # output = {
        #     "query": query,
        #     "results": results,
        # }

        # return output

        results = []

        keywords = input_data.get("keywords", [])
        if not keywords:
            keywords = [input_data.get("query", "")]

        for keyword in keywords:
            if not keyword:
                continue

            logger.info(f"Processing keyword: '{keyword}'")

            for subreddit_name in target_subreddits:
                try:
                    posts = self.reddit_client.search_subreddit(
                        subreddit_name,
                        query=keyword,
                        limit=posts_limit,
                        sort="relevance"
                    )

                    if not posts:
                        continue

                    processed_posts = []
                    for post in posts:
                        try:
                            processed_post = self.process_post(
                                post,
                                comment_limit=comment_limit
                            )
                            processed_posts.append(processed_post)
                        except Exception as e:
                            logger.error(
                                f"Error processing post {post.get('id', 'unknown')}: {e}"
                            )

                    if processed_posts:
                        results.append({
                            "keyword": keyword,
                            "subreddit": subreddit_name,
                            "posts": processed_posts
                        })

                except Exception as e:
                    logger.error(
                        f"Error processing keyword '{keyword}' in subreddit {subreddit_name}: {e}"
                    )
        output = {
            "query": keywords,
            "results": results,
        }

        return output            



def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)

    service = RedditIngestionService()
    output = service.process_request(input_data)

    # print(json.dumps(output, indent=2, ensure_ascii=False))
    with open("ingestion_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Saved ingestion_output.json")




if __name__ == "__main__":
    main()
