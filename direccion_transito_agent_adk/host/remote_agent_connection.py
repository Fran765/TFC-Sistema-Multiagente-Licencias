import logging
from typing import Callable

import httpx
from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    SendMessageResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)

logger = logging.getLogger(__name__)

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]


class RemoteAgentConnections:
    """Manages connections to remote A2A agents."""

    def __init__(self, agent_card: AgentCard, agent_url: str):
        logger.debug(
            f"Initializing connection to agent: {agent_card.name} at {agent_url}"
        )
        self._httpx_client = httpx.AsyncClient(timeout=30)
        self.agent_client = A2AClient(self._httpx_client, agent_card, url=agent_url)
        self.card = agent_card
        self.conversation_name = None
        self.conversation = None
        self.pending_tasks = set()

    def get_agent(self) -> AgentCard:
        """Returns the agent card for this connection."""
        return self.card

    async def send_message(
        self, message_request: SendMessageRequest
    ) -> SendMessageResponse:
        """Sends a message to the remote agent."""
        return await self.agent_client.send_message(message_request)
