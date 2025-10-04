import os

from fastmcp import FastMCP
from jules_agent_sdk import JulesClient, models

_jules_client: JulesClient | None = None


def jules(api_key: str | None = None) -> JulesClient:
    global _jules_client
    if _jules_client is None:
        if api_key is None:
            api_key = os.getenv("JULES_API_KEY")
        _jules_client = JulesClient(api_key)
    return _jules_client


mcp = FastMCP("Jules MCP Server")


@mcp.tool(name="get_source", title="Get source", description="Get a single source by ID",
          tags={"sources"})
def get_source(source_id: str) -> models.Source:
    """Get a single source by ID.

    Args:
        source_id: the ID of the source.
        E.g. a GitHub repository name.
    """
    result = jules().sources.get(source_id)
    return result


@mcp.tool(name="get_all_sources", title="Get all source",
          description="Get all sources with optional filtering.",
          tags={"sources"})
def get_all_sources(filter_str: str | None = None) -> list[models.Source]:
    """Get all sources.

    Args:
        filter_str: The filter expression for listing sources, based on AIP-160.
          If not set, all sources will be returned. Currently only supports filtering by name,
          which can be used to filter by a single source or multiple sources separated by OR.
          Example filters: - 'name=sources/source1 OR name=sources/source2'
    """
    result = jules().sources.list_all(filter_str=filter_str)
    return result


def start_mcp() -> None:
    mcp.run()


if __name__ == '__main__':
    start_mcp()
