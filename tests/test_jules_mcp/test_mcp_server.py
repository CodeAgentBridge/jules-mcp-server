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
from fastmcp import Client
from jules_agent_sdk import models


@pytest.mark.asyncio
class TestSources:
    async def test_get_source(self, client: Client, mock_jules_client: MagicMock):
        mock_jules_client.sources.get.return_value = models.Source(
            id="test-source", name="sources/test-source"
        )

        result = await client.call_tool("get_source", {"source_id": "test-source"})

        assert result.structured_content["name"] == "sources/test-source"
        mock_jules_client.sources.get.assert_called_once_with("test-source")

    async def test_list_sources(self, client: Client, mock_jules_client: MagicMock):
        mock_jules_client.sources.list.return_value = {
            "sources": [models.Source(id="test-source", name="sources/test-source")],
            "nextPageToken": "next-page-token",
        }

        result = await client.call_tool(
            "list_sources",
            {"filter_str": "name=sources/test-source", "page_size": 1},
        )

        assert len(result.structured_content["sources"]) == 1
        assert result.structured_content["sources"][0]["name"] == "sources/test-source"
        assert result.structured_content["nextPageToken"] == "next-page-token"
        mock_jules_client.sources.list.assert_called_once_with(
            filter_str="name=sources/test-source", page_size=1, page_token=None
        )

    async def test_get_all_sources(self, client: Client, mock_jules_client: MagicMock):
        mock_jules_client.sources.list_all.return_value = [
            models.Source(id="test-source-1", name="sources/test-source-1"),
            models.Source(id="test-source-2", name="sources/test-source-2"),
        ]

        result = await client.call_tool(
            "get_all_sources", {"filter_str": "name=sources/test-source-1"}
        )

        assert len(result.structured_content["result"]) == 2
        assert result.structured_content["result"][0]["name"] == "sources/test-source-1"
        assert result.structured_content["result"][1]["name"] == "sources/test-source-2"
        mock_jules_client.sources.list_all.assert_called_once_with(
            filter_str="name=sources/test-source-1"
        )


@pytest.mark.asyncio
class TestSessions:
    @pytest.fixture
    def mock_session_dict(self) -> dict:
        """Provides a mock session as a dictionary."""
        return {
            "name": "sessions/test-session",
            "title": "Test Session",
            "prompt": "Test prompt",
            "source": "sources/test-source",
            "source_context": {"source_name": "sources/test-source"},
            "state": "IN_PROGRESS",
        }

    async def test_create_session(
        self, client: Client, mock_jules_client: MagicMock, mock_session_dict: dict
    ):
        mock_jules_client.sessions.create.return_value = mock_session_dict

        result = await client.call_tool(
            "create_session",
            {
                "prompt": "Test prompt",
                "source": "sources/test-source",
                "title": "Test Session",
            },
        )

        assert result.structured_content["name"] == "sessions/test-session"
        assert result.structured_content["title"] == "Test Session"
        mock_jules_client.sessions.create.assert_called_once_with(
            prompt="Test prompt",
            source="sources/test-source",
            starting_branch=None,
            title="Test Session",
            require_plan_approval=False,
        )

    async def test_get_session(
        self, client: Client, mock_jules_client: MagicMock, mock_session_dict: dict
    ):
        mock_jules_client.sessions.get.return_value = mock_session_dict

        result = await client.call_tool("get_session", {"session_id": "test-session"})

        assert result.structured_content["name"] == "sessions/test-session"
        mock_jules_client.sessions.get.assert_called_once_with("test-session")

    async def test_list_sessions(
        self, client: Client, mock_jules_client: MagicMock, mock_session_dict: dict
    ):
        mock_jules_client.sessions.list.return_value = {
            "sessions": [mock_session_dict],
            "nextPageToken": "next-page-token",
        }

        result = await client.call_tool("list_sessions", {"page_size": 1})

        assert len(result.structured_content["sessions"]) == 1
        assert (
            result.structured_content["sessions"][0]["name"] == "sessions/test-session"
        )
        assert result.structured_content["nextPageToken"] == "next-page-token"
        mock_jules_client.sessions.list.assert_called_once_with(
            page_size=1, page_token=None
        )

    async def test_approve_session_plan(
        self, client: Client, mock_jules_client: MagicMock
    ):
        result = await client.call_tool(
            "approve_session_plan", {"session_id": "test-session"}
        )

        assert result.structured_content["status"] == "approved"
        mock_jules_client.sessions.approve_plan.assert_called_once_with("test-session")

    async def test_send_session_message(
        self, client: Client, mock_jules_client: MagicMock
    ):
        result = await client.call_tool(
            "send_session_message",
            {"session_id": "test-session", "prompt": "Test message"},
        )

        assert result.structured_content["status"] == "sent"
        mock_jules_client.sessions.send_message.assert_called_once_with(
            "test-session", "Test message"
        )

    async def test_wait_for_session_completion(
        self, client: Client, mock_jules_client: MagicMock, mock_session_dict: dict
    ):
        mock_session_dict["state"] = "COMPLETED"
        mock_jules_client.sessions.wait_for_completion.return_value = mock_session_dict

        result = await client.call_tool(
            "wait_for_session_completion",
            {"session_id": "test-session", "poll_interval": 1, "timeout": 10},
        )

        assert result.structured_content["state"] == "COMPLETED"
        mock_jules_client.sessions.wait_for_completion.assert_called_once_with(
            "test-session", poll_interval=1, timeout=10
        )


@pytest.mark.asyncio
class TestActivities:
    async def test_get_activity(self, client: Client, mock_jules_client: MagicMock):
        mock_jules_client.activities.get.return_value = models.Activity(
            name="sessions/test-session/activities/test-activity"
        )

        result = await client.call_tool(
            "get_activity",
            {"session_id": "test-session", "activity_id": "test-activity"},
        )

        assert (
            result.structured_content["name"]
            == "sessions/test-session/activities/test-activity"
        )
        mock_jules_client.activities.get.assert_called_once_with(
            "test-session", "test-activity"
        )

    async def test_list_activities(self, client: Client, mock_jules_client: MagicMock):
        mock_jules_client.activities.list.return_value = {
            "activities": [
                models.Activity(name="sessions/test-session/activities/test-activity")
            ],
            "nextPageToken": "next-page-token",
        }

        result = await client.call_tool(
            "list_activities", {"session_id": "test-session", "page_size": 1}
        )

        assert len(result.structured_content["activities"]) == 1
        assert (
            result.structured_content["activities"][0]["name"]
            == "sessions/test-session/activities/test-activity"
        )
        assert result.structured_content["nextPageToken"] == "next-page-token"
        mock_jules_client.activities.list.assert_called_once_with(
            "test-session", page_size=1, page_token=None
        )

    async def test_list_all_activities(
        self, client: Client, mock_jules_client: MagicMock
    ):
        mock_jules_client.activities.list_all.return_value = [
            models.Activity(name="sessions/test-session/activities/test-activity-1"),
            models.Activity(name="sessions/test-session/activities/test-activity-2"),
        ]

        result = await client.call_tool(
            "list_all_activities", {"session_id": "test-session"}
        )

        assert len(result.structured_content["result"]) == 2
        assert (
            result.structured_content["result"][0]["name"]
            == "sessions/test-session/activities/test-activity-1"
        )
        assert (
            result.structured_content["result"][1]["name"]
            == "sessions/test-session/activities/test-activity-2"
        )
        mock_jules_client.activities.list_all.assert_called_once_with("test-session")
