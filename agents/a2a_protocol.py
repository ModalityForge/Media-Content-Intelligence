"""Typed in-process task boundary between the two public MCI agents.

Messages, task state, and results are represented explicitly so orchestration
decisions remain serializable and traceable. The helper accepts synchronous or
asynchronous validator handlers and converts failures into structured results.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import inspect
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class A2AMessage:
    """Serializable envelope sent from one named agent to another."""

    message_id: str
    from_agent: str
    to_agent: str
    payload: dict[str, Any]
    timestamp: datetime
    message_type: str = "task"

    def to_dict(self) -> dict[str, Any]:
        """Convert the message to JSON-compatible primitives for tracing."""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
        }


@dataclass
class A2ATask:
    """Execution record derived from an incoming agent-to-agent message."""

    task_id: str
    agent_name: str
    input_data: dict[str, Any]
    created_at: datetime
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        """Convert the task state to JSON-compatible primitives."""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "input_data": self.input_data,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


@dataclass
class A2AResult:
    """Completed or failed outcome returned across the agent boundary."""

    task_id: str
    status: str
    output: dict[str, Any]
    completed_at: datetime
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the result and optional error to serializable values."""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "output": self.output,
            "completed_at": self.completed_at.isoformat(),
            "error": self.error,
        }


def create_task(
    from_agent: str,
    to_agent: str,
    task_payload: dict[str, Any],
) -> A2AMessage:
    """Create an A2A task message."""
    return A2AMessage(
        message_id=f"msg-{uuid.uuid4().hex[:8]}",
        from_agent=from_agent,
        to_agent=to_agent,
        payload=task_payload,
        timestamp=datetime.now(timezone.utc),
        message_type="task",
    )


async def send_task(
    from_agent: str,
    to_agent: str,
    task_payload: dict[str, Any],
    handler: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """Send a task to another agent and get the result."""
    message = create_task(from_agent, to_agent, task_payload)

    task = A2ATask(
        task_id=message.message_id,
        agent_name=to_agent,
        input_data=task_payload,
        created_at=message.timestamp,
        status="running",
    )

    try:
        result = handler(task_payload)
        if inspect.isawaitable(result):
            result = await result
        return A2AResult(
            task_id=task.task_id,
            status="completed",
            output=result,
            completed_at=datetime.now(timezone.utc),
        ).to_dict()
    except Exception as e:
        return A2AResult(
            task_id=task.task_id,
            status="failed",
            output={},
            completed_at=datetime.now(timezone.utc),
            error=str(e),
        ).to_dict()
