"""Taskiq tasks for background processing."""

from domain.taskiq_broker import broker


@broker.task(
    task_name="test_task",
)
def test_task() -> None:
    print("Test task")
