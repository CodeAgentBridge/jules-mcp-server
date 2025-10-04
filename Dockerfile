# Use an official Python runtime as a parent image
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy the rest of the application code
COPY jules_mcp/ ./jules_mcp

ENV JULES_API_KEY=""

# Set the entrypoint
ENTRYPOINT ["uv", "run", "--with", "fastmcp", "--with", "jules-agent-sdk", "--with", "requests", "fastmcp", "run", "jules_mcp/jules_mcp.py"]
