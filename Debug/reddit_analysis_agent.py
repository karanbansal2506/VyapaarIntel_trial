import json
import os
import sys
from typing import List, Dict, Any

from google import genai
from google.genai import types
from vector_store import VectorStore

vector_store = VectorStore()


# ---------------- CONFIG ---------------- #

# Initialize client with API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Correct model name for google.genai package
GEMINI_MODEL = "gemini-2.5-flash"


# ---------------- HELPERS ---------------- #

#def extract_text_blocks(ingestion_output: Dict[str, Any]) -> List[str]:
#    """
 #   Extract post titles and top comments from ingestion output.
  #  """
 #   texts = []

  #  for item in ingestion_output.get("results", []):
   #     for post in item.get("posts", []):
    #        title = post.get("title", "")
     #       if title:
      #          texts.append(title)
#
 #           for comment in post.get("top_comments", []):
  #              body = comment.get("body", "")
   #             if body:
    #                texts.append(body)

   # return texts

def retrieve_context(query: str):
    results = vector_store.search(query, k=10)
    return results["documents"][0]


def build_prompt(text_blocks: List[str], business_context: str) -> str:
    """
    Build a controlled Gemini prompt for business insight extraction.
    """
    MAX_CHARS = 8000

    joined = []
    total = 0
    for t in text_blocks:
        if total + len(t) > MAX_CHARS:
            break
        joined.append(f"- {t}")
        total += len(t)

    joined_text = "\n".join(joined)

    return f"""
You are an AI analyst helping small businesses understand real customer demand.
BUSINESS CONTEXT:
{business_context}

Below are real user questions and comments collected from public online discussions.

TASK:
1. Identify recurring themes or concerns.
2. Extract key pain points per theme.
3. Suggest concrete, actionable business actions.

IMPORTANT:
- Focus on repeated patterns, not one-off opinions.
- Do NOT mention Reddit or sources in the output.
- Be practical and concise.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "themes": [
    {{
      "theme": "",
      "evidence_count": 0,
      "key_pain_points": [],
      "recommended_actions": []
    }}
  ],
  "overall_summary": ""
}}

DISCUSSIONS:
{joined_text}
"""


def run_analysis(ingestion_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Gemini analysis and parse structured output.
    """
    business_context = ingestion_output.get("business_description", "")

    query = " ".join(ingestion_output.get("query", []))
    text_blocks = retrieve_context(query)


    if not text_blocks:
        return {
            "themes": [],
            "overall_summary": "No meaningful discussion data found."
        }

    prompt = build_prompt(text_blocks, business_context)

    try:
        # Use the correct google.genai API
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        raw_text = response.text.strip()

        # Handle markdown-wrapped JSON
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        return json.loads(raw_text)
        
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse Gemini output",
            "raw_output": raw_text
        }
    except Exception as e:
        return {
            "error": f"API error: {str(e)}",
            "details": "Check your API key and model availability"
        }


# ---------------- CLI ENTRY ---------------- #

def main():
    if len(sys.argv) < 2:
        print("Usage: python reddit_analysis_agent.py <ingestion_output.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r", encoding="utf-8") as f:
        ingestion_output = json.load(f)

    analysis_result = run_analysis(ingestion_output)

    print(json.dumps(analysis_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()