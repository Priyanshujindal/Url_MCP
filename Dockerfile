# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements if exists, else install manually
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy the rest of the code
COPY . .

# Set environment variables (change MCP_API_KEY in Railway dashboard for security)
ENV MCP_API_KEY=change-me-please
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run the MCP server
CMD ["python", "url_injector_mcp.py"] 