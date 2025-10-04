import pytest
from fastmcp import Client

from jules_mcp import mcp


@pytest.mark.asyncio
async def test_tool_execution():
    client: Client
    async with Client(mcp) as client:
        results = await client.call_tool("get_all_sources")
        assert results is not None
