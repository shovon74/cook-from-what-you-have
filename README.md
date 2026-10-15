# 🍳 Personal Chef

An AI cooking assistant. Tell it what's in your kitchen and it suggests recipes you can make right now, lists what's missing, and offers substitutions.

![Personal Chef demo](docs/demo/demo1.png)

## Features

- Recipe suggestions from the ingredients you already have
- Missing-ingredient list with substitutions
- Remembers allergies and dietary needs across the conversation
- Searches the web when it needs to verify a technique, timing, or cuisine
- Full run tracing with LangSmith (prompts, tool calls, latency, tokens)

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Google Gemini |
| Agent framework | LangChain |
| Web search | Tavily |
| Observability | LangSmith |
| UI | Streamlit |
| Package management | uv |

## Project Structure

```
├── agent.py   # Agent logic: prompt, model, tools, memory (no UI code)
├── app.py     # Streamlit web UI
├── main.py    # Optional terminal UI
└── pyproject.toml
```

The agent is kept separate from the UI, so the same `agent.py` powers both the web app and the CLI.

## Getting Started

**Prerequisites:** Python 3.13+, [uv](https://docs.astral.sh/uv/), and API keys for [Gemini](https://aistudio.google.com/apikey), [Tavily](https://app.tavily.com), and [LangSmith](https://smith.langchain.com).

```bash
git clone https://github.com/<your-username>/personal-chef.git
cd personal-chef
uv sync
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your-gemini-key
TAVILY_API_KEY=your-tavily-key
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=personal-chef
```

Run the web app:

```bash
uv run streamlit run app.py
```

Or the terminal version:

```bash
uv run main.py
```

## Example

> **You:** I have eggs, spinach, feta, and half an onion.
>
> **Chef:** Here's a spinach and feta omelette: ...

## Roadmap

- [ ] Stream responses token by token
- [ ] Structured recipe output (Pydantic) with recipe cards
- [ ] Persistent chat history (SQLite/Postgres checkpointer)
- [ ] LangSmith evals: ingredient adherence and allergy safety