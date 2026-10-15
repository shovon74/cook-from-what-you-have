# Pantry Chef

An AI cooking assistant that suggests recipes from the ingredients you have, notes missing ingredients and substitutions, and accounts for dietary restrictions.

## Run locally

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env` and add your `GOOGLE_API_KEY` and `TAVILY_API_KEY`.
3. Start the app with `uv run streamlit run app.py`.

LangSmith tracing is optional; configure its variables in `.env` if you use it.
