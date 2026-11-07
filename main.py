import os
from collections.abc import Sequence

from mistralai import agents
from mistralai.client import Mistral
from mistralai.client import models as api_models

AGENT_MODEL = "mistral-large-4"
SEARCH_MODEL = "mistral-medium-latest"


def _mistral_client() -> Mistral:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if api_key:
        return Mistral(api_key=api_key)
    from mistralai.workflows.client import get_mistral_client

    return get_mistral_client()


def _render_content(content: str | Sequence[object]) -> str:
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for chunk in content:
        if isinstance(chunk, api_models.TextChunk):
            parts.append(chunk.text)
        elif isinstance(chunk, api_models.ToolReferenceChunk):
            parts.append(f"\nSource: {chunk.title} ({chunk.url})")
    return "".join(parts)


@agents.tool
async def web_search(query: str) -> str:
    """Search the public web for up-to-date information on a topic. Returns a short answer with its sources listed at the end."""
    client = _mistral_client()
    response = await client.beta.conversations.start_async(
        model=SEARCH_MODEL,
        inputs=query,
        tools=[{"type": "web_search"}],
        store=False,
    )
    replies = [entry for entry in response.outputs if isinstance(entry, api_models.MessageOutputEntry)]
    if not replies:
        raise agents.ToolError("The web search returned no answer. Rephrase the query and try again.")
    return _render_content(replies[-1].content)


agent = agents.Agent(
    model=AGENT_MODEL,
    name="research-agent",
    instructions=(
        "You are a conversational research assistant. The user talks with you to explore a topic in depth.\n"
        "Use the web_search tool for anything current, uncertain, or that needs sources: recent events, "
        "statistics, claims to verify, or anything past your knowledge cutoff. Search several angles of the "
        "question and cross-check important claims against more than one source before stating them.\n"
        "Cite every factual claim with a Markdown link to its source, [title](url), using the sources the "
        "search returns. Say clearly when sources disagree or when you are unsure.\n"
        "Answer conversationally: a short direct answer first, then the useful detail, then open questions or "
        "angles the user may want to explore next. Do not dump a report; offer to go deeper.\n"
        "Remember earlier messages in this conversation and refer back to them. When the request is ambiguous, "
        "ask one clarifying question before searching. Do not search for things you can answer reliably from "
        "knowledge, and say when information may be outdated."
    ),
    tools=[web_search],
    temperature=0.3,
)


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        result = await agent.run("What should I research first?")
        print(result.text)

    asyncio.run(main())
