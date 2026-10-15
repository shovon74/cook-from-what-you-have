# Cook From What You Have

An AI cooking assistant that suggests recipes from your ingredients, with substitutions and dietary preferences in mind.

## Run locally

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

1. Get API keys from [Google AI Studio](https://aistudio.google.com/app/apikey) and [Tavily](https://tavily.com/). Their free-tier availability and limits may change.
2. Install dependencies and create your environment file:

	```sh
	uv sync
	cp .env.example .env
	```

3. Add your `GOOGLE_API_KEY` and `TAVILY_API_KEY` to `.env`. For optional [LangSmith](https://smith.langchain.com/) tracing, add your `LANGSMITH_API_KEY` and set `LANGSMITH_TRACING=true`; otherwise, set it to `false`.
4. Start the app:

	```sh
	uv run streamlit run app.py
	```
