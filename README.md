# research-agent

A conversational research agent built with the [Mistral Agents SDK](https://docs.mistral.ai/studio/agents/overview) (`mistralai-agents`).

The agent (`main.py`) chats with the user about a topic, searches the web through Mistral's hosted
`web_search` tool (called via the Conversations API from a custom `@agents.tool`), cross-checks
sources, and answers with Markdown citations. Sessions are durable once deployed, so the
conversation keeps its memory.

## Run locally

```bash
uv sync
export MISTRAL_API_KEY=<your-key>
uv run agents chat          # chat in the terminal, in this process
uv run agents chat -m "What happened in AI this week?"
```

## Deploy (Mistral-managed)

Commit and push this project to a GitHub repository, then:

```bash
git remote add origin <repository-url>
git push -u origin HEAD
uv run --env-file .env agents deploy
```

`agents deploy` builds the pushed commit with the Dockerfile in this repo and runs it as a
managed deployment. It prints a link to chat with the agent in Vibe Code Web
(`https://chat.mistral.ai/managed-agents/research-agent`) and you can also call it by name:

```bash
uv run --env-file .env agents chat research-agent
```

```python
from mistralai import agents

agent = agents.Agent.load_from(agent_name="research-agent")
session = await agent.start_session()
result = await session.run("Summarize the latest fusion energy news.")
print(result.text)
```
