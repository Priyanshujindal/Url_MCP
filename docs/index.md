# URL Injector MCP Server

A production-ready, open source Model Context Protocol (MCP) server that augments user prompts by injecting relevant URLs. Designed for public deployment and integration with LLM applications (Cursor, Claude, etc.).

## Features
- MCP-compliant: Exposes a single tool, `inject_urls_into_prompt`, for prompt augmentation.
- Async web search (DuckDuckGo) for relevant URLs.
- URL filtering for reputable, whitelisted domains.
- Streamable HTTP for public access.
- API key authentication and per-IP rate limiting.
- Health check endpoint for monitoring.
- Structured logging and robust error handling.

## Quick Start

1. **Install dependencies:**
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
4. **Test health check:**
   ```bash
   curl http://localhost:8000/health
   ```

See the [Usage](usage.md) and [Deployment](deployment.md) pages for more details. 