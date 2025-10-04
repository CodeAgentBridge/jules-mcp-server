#  Copyright (C) 2025 Yurii Serhiichuk
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
from typing import Any, Final

from fastmcp import FastMCP
from jules_agent_sdk import JulesClient, models
from mcp.types import ToolAnnotations

version: Final[str] = "0.1.2"

_jules_client: JulesClient | None = None


def jules(api_key: str | None = None) -> JulesClient:
    """Get a singleton JulesClient instance.

    The API key is read from the JULES_API_KEY environment variable if not provided.
    """
    global _jules_client
    if _jules_client is None:
        if api_key is None:
            api_key = os.getenv("JULES_API_KEY")
        _jules_client = JulesClient(api_key)
    return _jules_client


mcp = FastMCP("Jules MCP Server", version=version)


# -------------------- Sources --------------------
@mcp.tool(
    name="get_source",
    title="Get source",
    description="Get a single source by ID (e.g., sources/abc123 or abc123)",
    tags={"sources"},
    annotations=ToolAnnotations(
        title="Get Jules source by ID",
        readOnlyHint=True,
        idempotentHint=True,
        destructiveHint=False,
        openWorldHint=True,
    ),
)
def get_source(source_id: str) -> models.Source:
    """Get a single source by ID.

    Args:
        source_id: The ID or full name of the source. For GitHub sources, this is the Jules source ID, e.g. 'sources/abc123'.
    """
    result = jules().sources.get(source_id)
    return result


@mcp.tool(
    name="list_sources",
    title="List sources (paginated)",
    description="List sources with optional filter and pagination; returns items and nextPageToken.",
    tags={"sources"},
)
def list_sources(
    filter_str: str | None = None,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
    """List sources (paginated).

    Args:
        filter_str: Filter expression per AIP-160. Currently supports filtering by name, e.g. "name=sources/source1 OR name=sources/source2".
        page_size: Max number of sources to return.
        page_token: Token from a previous call to retrieve the next page.

    Returns:
        Dict with keys:
            - sources: list[Source]
            - nextPageToken: Optional[str]
    """
    result = jules().sources.list(
        filter_str=filter_str, page_size=page_size, page_token=page_token
    )
    return result


@mcp.tool(
    name="get_all_sources",
    title="Get all sources",
    description="Get all sources with optional filtering (auto-pagination).",
    tags={"sources"},
)
def get_all_sources(filter_str: str | None = None) -> list[models.Source]:
    """Get all sources (auto-pagination).

    Args:
        filter_str: The filter expression for listing sources, based on AIP-160.
            If not set, all sources will be returned. Currently only supports filtering by name,
            which can be used to filter by a single source or multiple sources separated by OR.
            Example: 'name=sources/source1 OR name=sources/source2'
    """
    result = jules().sources.list_all(filter_str=filter_str)
    return result


# -------------------- Sessions --------------------
@mcp.tool(
    name="create_session",
    title="Create session",
    description="Create a new Jules session for a given source and prompt.",
    tags={"sessions"},
)
def create_session(
    prompt: str,
    source: str,
    starting_branch: str | None = None,
    title: str | None = None,
    require_plan_approval: bool = False,
) -> models.Session:
    """Create a new session.

    Args:
        prompt: The prompt to start the session with.
        source: The source to use (e.g., 'sources/abc123').
        starting_branch: Optional starting branch for GitHub repos.
        title: Optional human-friendly title for the session.
        require_plan_approval: If True, the plan requires explicit approval before execution.
    """
    session = jules().sessions.create(
        prompt=prompt,
        source=source,
        starting_branch=starting_branch,
        title=title,
        require_plan_approval=require_plan_approval,
    )
    return session


@mcp.tool(
    name="get_session",
    title="Get session",
    description="Get a single session by ID.",
    tags={"sessions"},
)
def get_session(session_id: str) -> models.Session:
    """Get a session by ID.

    Args:
        session_id: The session ID or full name (e.g., 'sessions/abc123' or 'abc123').
    """
    return jules().sessions.get(session_id)


@mcp.tool(
    name="list_sessions",
    title="List sessions (paginated)",
    description="List sessions with pagination; returns items and nextPageToken.",
    tags={"sessions"},
)
def list_sessions(
    page_size: int | None = None, page_token: str | None = None
) -> dict[str, Any]:
    """List sessions (paginated).

    Args:
        page_size: Max number of sessions to return.
        page_token: Token from a previous call to retrieve the next page.

    Returns:
        Dict with keys:
            - sessions: list[Session]
            - nextPageToken: Optional[str]
    """
    return jules().sessions.list(page_size=page_size, page_token=page_token)


@mcp.tool(
    name="approve_session_plan",
    title="Approve session plan",
    description="Approve the pending plan for a session that requires approval.",
    tags={"sessions"},
)
def approve_session_plan(session_id: str) -> dict[str, str]:
    """Approve a plan in a session.

    Args:
        session_id: The session ID or full name.

    Returns:
        Simple status confirmation.
    """
    jules().sessions.approve_plan(session_id)
    return {"status": "approved"}


@mcp.tool(
    name="send_session_message",
    title="Send user message to session",
    description="Send a user message (prompt) to an existing session.",
    tags={"sessions"},
)
def send_session_message(session_id: str, prompt: str) -> dict[str, str]:
    """Send a message to a session.

    Args:
        session_id: The session ID or full name.
        prompt: The message/prompt from the user.

    Returns:
        Simple status confirmation.
    """
    jules().sessions.send_message(session_id, prompt)
    return {"status": "sent"}


@mcp.tool(
    name="wait_for_session_completion",
    title="Wait for session completion",
    description="Poll the session until completion or failure, with optional timeout.",
    tags={"sessions"},
)
def wait_for_session_completion(
    session_id: str,
    poll_interval: int = 5,
    timeout: int | None = 600,
) -> models.Session:
    """Wait for a session to reach a terminal state.

    Args:
        session_id: The session ID or full name.
        poll_interval: Seconds between polling requests (default: 5).
        timeout: Optional timeout in seconds (default: 600). Set None for no timeout.
    """
    return jules().sessions.wait_for_completion(
        session_id, poll_interval=poll_interval, timeout=timeout
    )


# -------------------- Activities --------------------
@mcp.tool(
    name="get_activity",
    title="Get activity",
    description="Get a single activity by ID within a session.",
    tags={"activities"},
)
def get_activity(session_id: str, activity_id: str) -> models.Activity:
    """Get an activity by ID.

    Args:
        session_id: The session ID or full name.
        activity_id: The activity ID.
    """
    return jules().activities.get(session_id, activity_id)


@mcp.tool(
    name="list_activities",
    title="List activities (paginated)",
    description="List activities for a session with pagination; returns items and nextPageToken.",
    tags={"activities"},
)
def list_activities(
    session_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
    """List activities for a session (paginated).

    Args:
        session_id: The session ID or full name.
        page_size: Max number of activities to return.
        page_token: Token from a previous call to retrieve the next page.

    Returns:
        Dict with keys:
            - activities: list[Activity]
            - nextPageToken: Optional[str]
    """
    return jules().activities.list(
        session_id, page_size=page_size, page_token=page_token
    )


@mcp.tool(
    name="list_all_activities",
    title="List all activities",
    description="List all activities for a session (auto-pagination).",
    tags={"activities"},
)
def list_all_activities(session_id: str) -> list[models.Activity]:
    """List all activities for a session (auto-pagination)."""
    return jules().activities.list_all(session_id)


def start_mcp() -> None:
    mcp.run()


if __name__ == "__main__":
    start_mcp()
