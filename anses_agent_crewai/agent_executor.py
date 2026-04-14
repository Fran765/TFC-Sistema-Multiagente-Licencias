import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    Part,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from agent import ANSESAgent

logger = logging.getLogger(__name__)


class ANSESAgentExecutor(AgentExecutor):
    """AgentExecutor for the ANSES agent."""

    def __init__(self):
        """Initializes the ANSESAgentExecutor."""
        self.agent = ANSESAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Executes the ANSES agent to handle CUIL requests."""
        if not context.task_id or not context.context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not context.message:
            raise ValueError("RequestContext must have a message")

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            await updater.submit()
        await updater.start_work()

        query = context.get_user_input()
        try:
            result = self.agent.invoke(query)
            logger.info("CUIL request processed successfully")
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            raise ServerError(error=InternalError()) from e

        parts = [Part(root=TextPart(text=result))]

        await updater.add_artifact(parts)
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handles task cancellation."""
        raise ServerError(error=UnsupportedOperationError())
