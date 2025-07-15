# Deployment Guide

## Local Deployment

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set environment variables:**
   - `MCP_API_KEY`: API key for authentication (default: `change-me-please`)
   - `MCP_RATE_LIMIT`: Requests per minute per IP (default: 60)
   - Optionally, create a `.env` file for local development.
3. **Run the server:**
   ```bash
   python url_injector_mcp.py
   ```

## Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t url-injector-mcp .
   ```
2. **Run the container:**
   ```bash
   docker run -p 8000:8000 \
     -e MCP_API_KEY=your-secure-api-key \
     -e MCP_RATE_LIMIT=60 \
     url-injector-mcp
   ```

## Free Cloud Deployment Options

- **Render (free tier):** Deploy Docker containers with a public URL.
- **Fly.io (free tier):** Deploy Docker containers globally.
- **Railway.app (free tier):** Simple deployments for small projects.

## HTTPS with Nginx and Let’s Encrypt

1. **Set up Nginx as a reverse proxy** (see project docs for sample config).
2. **Get a free SSL certificate** with [Certbot](https://certbot.eff.org/).
3. **Forward HTTPS traffic** to your MCP server on port 8000.

## Environment Variables

- Set `MCP_API_KEY` and `MCP_RATE_LIMIT` securely in your deployment environment.
- Never commit secrets to version control.

## Health Monitoring

- Use `/health` endpoint for uptime checks (e.g., with UptimeRobot free tier).

## Scaling

- Run multiple containers behind a load balancer for high availability.
- The server is stateless and easy to scale horizontally. 