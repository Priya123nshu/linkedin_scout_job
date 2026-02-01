FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install system dependencies required for Playwright and Git
# uvx needs git to pull from github
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to cache dependencies
COPY requirements.txt .

# Install python dependencies from requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

# Install Playwright browsers/dependencies
# Run directly with python module to avoid uv venv issues
RUN python -m playwright install-deps
RUN python -m playwright install chromium

# Copy application code
COPY . .

# Install dependencies for the local MCP server (so uv run works instantly)
WORKDIR /app/linkedin_mcp_server_local
ENV UV_HTTP_TIMEOUT=300
RUN uv sync
WORKDIR /app

# Ensure temp directory exists and has permissions (for cookie file)
RUN chmod 777 /tmp

# Expose port (Render sets PORT env var, but we defualt to 8000/8001)
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
