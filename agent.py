"""Personal Chef agent. No UI code here, so any front end can import it."""

import os

from dotenv import load_dotenv

# Load .env BEFORE importing langchain so LangSmith tracing env vars are picked up.
load_dotenv()

from langchain.agents import create_agent  # noqa: E402
from langchain.chat_models import init_chat_model  # noqa: E402
from langchain_tavily import TavilySearch  # noqa: E402
from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402

SYSTEM_PROMPT = """You are Personal Chef, a friendly home-cooking assistant.

The user tells you which ingredients they have at home. Your job:
1. Suggest 1-3 recipes that mainly use those ingredients. Assume basic pantry
   staples (salt, pepper, oil, water) unless told otherwise.
2. For the best match, give: name, time, servings, ingredients with quantities,
   and numbered steps.
3. Clearly list any missing ingredients and offer a substitution for each.
4. If you are unsure about a technique, cooking time, or the user asks for a
   specific cuisine/diet, use the web search tool to check before answering.
5. Respect allergies and dietary restrictions the user mentions, for the whole
   conversation. If the ingredient list is too thin, ask one short question.
"""


def build_agent():
    model = init_chat_model(
        os.getenv("CHEF_MODEL", "google_genai:gemini-2.5-flash"),
        temperature=0.7,
    )
    return create_agent(
        model,
        tools=[TavilySearch(max_results=4)],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),  # chat history is stored per thread_id
    )


def message_text(message) -> str:
    """Gemini sometimes returns content as a list of blocks; normalise to str."""
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in content
    )


def ask(agent, user_input: str, thread_id: str) -> str:
    """Send one user message and return the chef's reply as plain text."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        {"configurable": {"thread_id": thread_id}, "tags": ["personal-chef"]},
    )
    return message_text(result["messages"][-1])