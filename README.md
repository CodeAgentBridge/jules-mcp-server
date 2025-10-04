# Jules MCP Server (jules-mcp)

An MCP (Model Context Protocol) server that exposes Google Jules Agent operations via FastMCP.

This server lets MCP-compatible clients (and Python code) list Jules sources, create and manage
sessions, and inspect activities using the official jules-agent-sdk.

- Server framework: FastMCP
- SDK: jules-agent-sdk
- Python: 3.13+
- License: Apache-2.0

## Features

Tools exposed via the MCP server (grouped by area):

- Sources
  - get_source(source_id)
  - list_sources(filter_str=None, page_size=None, page_token=None)
  - get_all_sources(filter_str=None)
- Sessions
  - create_session(prompt, source, starting_branch=None, title=None, require_plan_approval=False)
  - get_session(session_id)
  - list_sessions(page_size=None, page_token=None)
  - approve_session_plan(session_id)
  - send_session_message(session_id, prompt)
  - wait_for_session_completion(session_id, poll_interval=5, timeout=600)
- Activities
  - get_activity(session_id, activity_id)
  - list_activities(session_id, page_size=None, page_token=None)
  - list_all_activities(session_id)

See jules_mcp/jules_mcp.py for signatures and inline docstrings.

## Installation

Option A — from a local checkout:

```bash
# from the repository root
pip install -e .
```

Option B — using uv (recommended during development):

```bash
# from the repository root
uv sync
```

The project targets Python 3.13+.

## Configuration

Set your Jules API key via environment variable:

- Windows PowerShell
  ```powershell
  $Env:JULES_API_KEY = "<your_api_key_here>"
  ```
- Unix shells (bash/zsh)
  ```bash
  export JULES_API_KEY="<your_api_key_here>"
  ```

If you do not provide an argument to jules(), the SDK reads JULES_API_KEY automatically.

## Running the MCP server

There are two common ways to run the server.

1) Programmatic run (in-process) using FastMCP Client — useful for testing or embedding:

```python
import asyncio
from fastmcp import Client
from jules_mcp import mcp

async def main():
    async with Client(mcp) as client:
        # Example: list all sources (auto-paginated)
        result = await client.call_tool("get_all_sources")
        print(result)

asyncio.run(main())
```

2) As a standalone MCP server executable for external MCP clients:

- Using uv and FastMCP directly
  ```bash
  uv run fastmcp run jules_mcp/jules_mcp.py:mcp
  ```
  This starts the MCP server over stdio.

- Using the provided configuration files
  - MCP.json: a sample command configuration for MCP-aware hosts.
  - fastmcp.json: FastMCP runtime/environment configuration.

Adjust paths in MCP.json if you use a different checkout location.

You can also run via the module entry point:

```bash
python -m jules_mcp
```

This calls start_mcp() which invokes FastMCP.run() using the "mcp" instance defined in the package.

## Usage notes and examples

- Listing and filtering sources
```python
import asyncio
from fastmcp import Client
from jules_mcp import mcp

async def main():
    async with Client(mcp) as client:
        # Filter syntax follows AIP-160 filtering rules supported by Jules
        res = await client.call_tool(
            "list_sources",
            {"filter_str": "name=sources/source1 OR name=sources/source2", "page_size": 10}
        )
        print(res)

asyncio.run(main())
```

- Creating a session and waiting for completion
```python
import asyncio
from fastmcp import Client
from jules_mcp import mcp

async def run_session():
    async with Client(mcp) as client:
        session = await client.call_tool(
            "create_session",
            {
                "prompt": "Analyze the repository and propose improvements",
                "source": "sources/abc123",
                "require_plan_approval": True,
            },
        )

        # Optionally approve plan
        await client.call_tool("approve_session_plan", {"session_id": session["name"]})

        # Wait for completion
        final = await client.call_tool(
            "wait_for_session_completion",
            {"session_id": session["name"], "poll_interval": 5, "timeout": 600}
        )
        print(final)

asyncio.run(run_session())
```

- Inspecting activities
```python
import asyncio
from fastmcp import Client
from jules_mcp import mcp

async def list_acts(session_id: str):
    async with Client(mcp) as client:
        acts = await client.call_tool("list_all_activities", {"session_id": session_id})
        for a in acts:
            print(a)

asyncio.run(list_acts("sessions/abc123"))
```

## Development

- Create a virtual environment and install dev dependencies
  ```bash
  uv sync
  # or: pip install -e .[dev]
  ```

- Run tests (note: some tools may reach the Jules API and require JULES_API_KEY)
  ```bash
  uv run pytest -q
  ```

- Linting/formatting: follow your preferred tools; this repo does not include linters by default.

## Project metadata

- Package name: jules-mcp
- Version: 0.1.0
- Entry points:
  - Python module: python -m jules_mcp
  - FastMCP source: jules_mcp/jules_mcp.py:mcp

## License

Apache License 2.0. See the LICENSE file for details.

## Acknowledgements

- FastMCP — https://gofastmcp.com/
- Model Context Protocol — https://modelcontextprotocol.io/
- jules-agent-sdk — unofficial/official SDK used by this server
