[![CI](https://github.com/yourusername/url-injector-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/url-injector-mcp/actions/workflows/ci.yml)
[![Docs](https://github.com/yourusername/url-injector-mcp/actions/workflows/docs.yml/badge.svg)](https://github.com/yourusername/url-injector-mcp/actions/workflows/docs.yml)
[![Docker Image](https://github.com/yourusername/url-injector-mcp/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/yourusername/url-injector-mcp/pkgs/container/url-injector-mcp)
[![codecov](https://codecov.io/gh/yourusername/url-injector-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/url-injector-mcp)

# URL Injector MCP Server

A production-ready Python Model Context Protocol (MCP) server that augments user prompts by injecting relevant URLs based on prompt content. Designed for public deployment and integration with LLM applications (e.g., Cursor, Claude, etc.).

## Features
- **MCP-compliant**: Exposes a single tool, `inject_urls_into_prompt`, for prompt augmentation.
- **Async web search**: Uses DuckDuckGo to find relevant URLs for extracted keywords.
- **URL filtering**: Only reputable, whitelisted domains are included.
- **Streamable HTTP**: Publicly accessible via HTTP (default port 8000).
- **API key authentication**: Bearer token required for all requests.
- **Rate limiting**: Per-IP rate limiting to prevent abuse.
- **Health check**: `/health` endpoint for monitoring and orchestration.
- **Logging**: Structured logging for observability.

## Requirements
- Python 3.9+
- See `requirements.txt` for dependencies

## Setup
1. **Clone the repo and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set environment variables:**
   - `MCP_API_KEY`: API key for authentication (default: `change-me-please`)
   - `MCP_RATE_LIMIT`: Requests per minute per IP (default: 60)

3. **Run the server:**
   ```bash
   python url_injector_mcp.py
   ```
   The server will listen on `0.0.0.0:8000` by default.

## Deployment
- Deploy to any public cloud, PaaS, or VPS that supports Python and exposes HTTP endpoints (e.g., Heroku, Render, Google Cloud Run, AWS EC2, etc.).
- For HTTPS, use a reverse proxy (e.g., Nginx) or a managed platform.
- For Docker, add a simple Dockerfile (not included by default).

## Security
- **API Key**: All requests (except `/health`) require a Bearer token in the `Authorization` header.
- **Rate Limiting**: Prevents abuse by limiting requests per IP.
- **Input Validation**: Only whitelisted domains are included in results.
- **Error Handling**: No sensitive info is leaked in error messages.

## Usage
- **Tool:** `inject_urls_into_prompt(user_prompt: str) -> str`
- **Input:** Any natural language prompt (e.g., "How do I implement a REST API in Python using Flask?")
- **Output:** The original prompt, augmented with up to 10 relevant URLs as a Markdown list.

**Example output:**
```
How do I implement a REST API in Python using Flask?

Here are some relevant resources:
- https://realpython.com/flask-rest-api/
- https://flask.palletsprojects.com/en/2.0.x/tutorial/
- https://stackoverflow.com/questions/12364942/developing-restful-apis-with-python-and-flask
```

## Health Check
- `GET /health` returns `200 OK` with body `OK`.

## Configuration
- Change allowed domains, rate limit, and API key by editing the top of `url_injector_mcp.py` or using environment variables.

## License
MIT 