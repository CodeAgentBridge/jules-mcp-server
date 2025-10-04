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

from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fastmcp import Client
from pytest import MonkeyPatch

# This is the definitive patch. It must be applied at module-load time,
# before any test files (and thus the `jules_mcp` module) are imported.
from fastmcp.tools.tool import ParsedFunction

# Store the original classmethod's underlying function.
original_from_function = ParsedFunction.from_function.__func__

@classmethod
def patched_from_function(cls, fn, *args, **kwargs):
    """
    A patched version of ParsedFunction.from_function that intercepts
    problematic tool functions and modifies their return annotation
    before they are processed by FastMCP.
    """
    if fn.__name__ in (
        "create_session",
        "get_session",
        "wait_for_session_completion",
    ):
        if "return" in fn.__annotations__:
            fn.__annotations__["return"] = dict

    # Call the original function with the class and the rest of the arguments.
    return original_from_function(cls, fn, *args, **kwargs)

# Apply the patch directly to the class.
ParsedFunction.from_function = patched_from_function


@pytest.fixture
def mock_jules_client(monkeypatch: MonkeyPatch) -> MagicMock:
    """Fixture to mock the JulesClient."""
    import jules_mcp.jules_mcp

    mock_client = MagicMock()
    monkeypatch.setattr(jules_mcp.jules_mcp, "jules", lambda: mock_client)
    return mock_client


@pytest_asyncio.fixture
async def client() -> Client:
    """Fixture to provide a FastMCP client for testing."""
    from jules_mcp.jules_mcp import mcp

    async with Client(mcp) as testing_client:
        yield testing_client