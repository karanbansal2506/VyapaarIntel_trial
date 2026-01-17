import json
import os
import sys
from typing import Dict, Any

from google import genai


# ---------------- CONFIG ---------------- #

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

GEMINI_MODEL = "gemini-2.5-flash"

OUTPUT_FILE = "ex.json"


# ---------------- PROMPT BUILDER ---------------- #

def build_prompt(user_query: str) -> str:
    return f"""
You are an AI research planner.

A user has described what they want to analyze. Your job is to convert this
into a structured research plan for analyzing real user discussions on Reddit.

USER QUERY:
{user_query}

TASK:
1. Rewrite the query into a clear, neutral business description.
2. Generate 4–6 high-signal search keywords.
3. Select up to 3 relevant subreddits (MAX 3).
4. Set posts_limit_per_subreddit to 20.

RULES:
- Keywords should reflect real user phrasing.
- Subreddits must be realistic and relevant.
- Do NOT invent obscure subreddits.
- Output STRICT JSON ONLY. No explanations.

OUTPUT FORMAT:
{{
  "business_description": "",
  "target_subreddits": [],
  "keywords": [],
  "posts_limit_per_subreddit": 20
}}
"""


# ---------------- CORE LOGIC ---------------- #

def generate_research_plan(user_query: str) -> Dict[str, Any]:
    prompt = build_prompt(user_query)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    raw_text = response.text.strip()

    # Remove markdown fences if Gemini adds them
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    return json.loads(raw_text)


# ---------------- CLI ENTRY ---------------- #

def main():
    if len(sys.argv) < 2:
        print("Usage: python query_planner_agent.py \"<user query>\"")
        sys.exit(1)

    user_query = sys.argv[1]

    try:
        plan = generate_research_plan(user_query)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        print(f"Saved research plan to {OUTPUT_FILE}")

    except Exception as e:
        print("Error generating research plan:")
        print(e)


if __name__ == "__main__":
    main()
