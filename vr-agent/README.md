

# VR Agent Backend

Python/FastAPI backend service for AI-driven conversational agents in Va.Si.Li-Lab VR environment. Handles LLM communication, tool registration, and agent lifecycle management.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/createAgent` | Initialize a new agent with system prompt |
| `POST` | `/chat` | Process user message and return agent response |
| `POST` | `/addTool` | Register tool for specific agent instance |
| `POST` | `/removeTool` | Remove tool from agent instance |
| `POST` | `/toolDescriptions` | Sync tools from Unity to backend registry |


## LLM Integration

The backend communicates with external LLM server via `/chat/completions` endpoint.
The environment variables are set in the dockerfile:

```shell script
API_BASE=http://host.docker.internal:11434/v1
API_KEY=ollama
MODEL_NAME=gpt-oss:20b
```

## Deployment

Build and run the docker container, which runs the app.py file as the entry point.