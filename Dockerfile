# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy the rest of the application code
COPY jules_mcp/ ./jules_mcp

# Set the entrypoint
ENTRYPOINT ["python", "-m", "jules_mcp"]