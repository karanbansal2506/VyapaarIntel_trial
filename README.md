# VyapaarIntel
An AI agent that analyzes real customer conversations from public forums to extract recurring questions, pain points, and demand signals, and converts them into clear, actionable business recommendations for small businesses and MSMEs.
# VyapaarIntel

VyapaarIntel is an AI-powered research engine that converts real, live customer discussions into structured, actionable business insights.  
Instead of guessing what users want, businesses can directly learn from what people are already saying online.

---

## The Problem It Solves

- Businesses struggle to understand real customer pain points
- Surveys are slow, biased, and expensive
- Social media feedback is noisy and unstructured
- Generic LLMs don’t know what users are actually saying right now

The most honest customer feedback already exists — but it’s scattered across thousands of posts and comments.

---

## The Solution

VyapaarIntel acts as a listening engine:

1. User enters a natural language query
2. System converts it into a structured research plan
3. Live Reddit discussions are fetched automatically
4. High-signal comments are extracted and ranked
5. Gemini analyzes patterns and produces:
   - Key themes
   - Repeated pain points
   - Actionable business recommendations

The output is structured insights, not a chat response.

---

## Key Features

- Natural language → automated research planning
- Live Reddit data ingestion (no static datasets)
- Comment ranking to reduce noise
- Theme and pain-point extraction
- Actionable, business-ready recommendations
- Repeatable agentic workflow (not one-off prompting)

---

## Why Not Just Use an LLM?

| Generic LLM | VyapaarIntel |
|------------|-------------|
| Trained on past data | Uses live discussions |
| Generic advice | Evidence-backed insights |
| Hallucinations | Accurate responses |
| No source grounding | Structured signal extraction |
| Manual effort required | Fully automated pipeline |


---

## Architecture Overview

User Query  
↓  
Query Planner Agent (Gemini)  
↓  
Research Plan (ex.json)  
↓  
Reddit Ingestion Engine  
↓  
Signal Extraction + Ranking  
↓  
Insight Analysis Agent (Gemini)  
↓  
Structured Business Insights

---

## Tech Stack

- Backend: Python, FastAPI
- AI: Gemini API (google.genai), local clustering + embedding
- Data Source: Reddit (live discussions)
- Frontend: React (Vite)
- Architecture: Agent-based automation pipeline

---

## Features

- Low compute and token-efficient prompts
- Works on low bandwidth (text-first)
- Simple UX: one input → structured output
- Useful for MSMEs, founders, students, and researchers
- Easily extensible to SMS / WhatsApp / local-language interfaces

---

## Example Use Cases

- Product-market fit research
- Feature prioritization
- Market demand validation
- Student and career trend analysis
- Customer pain-point discovery

---

## Future Improvements

- WhatsApp / SMS input
- Regional language support
- More data sources (forums, reviews)
- Trend tracking and alerts
- Offline and low-connectivity support

---

## Project Status

This repository contains a working end-to-end prototype built for hackathon demonstration and future expansion.

