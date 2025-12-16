"""Taskiq middleware for database state management."""

import logging
from typing import Any
from uuid import UUID

from repository.connection import sync_db_session
from repository.base_model import BaseTableModel
from sqlalchemy import select, update
from taskiq import TaskiqMessage, TaskiqResult
from taskiq.abc.middleware import TaskiqMiddleware


db_types = type[BaseTableModel] # Change to type[TableModel1] | type[TableModel2] | ...

entity_name_to_class_mapping: db_types = {
    
}

class ProgressStateMiddleware(TaskiqMiddleware):
    """
    Middleware to manage *_in_progress flags for database entities.

    Tasks can use labels to specify which entity and field to manage:
    - entity_type: "chapter", "assignment", "course"
    - entity_id_param: name of the parameter containing entity ID (e.g., "chapter_id")
    - progress_field: name of the boolean field (e.g., "content_generation_in_progress")
    - result_fields: dict of fields to update on success (optional)
    """

    def _get_entity_info(
        self, message: TaskiqMessage
    ) -> tuple[UUID, db_types, str, str] | None:
        """
        Extract entity information from task message.

        Returns:
            Tuple of (entity_id, entity_class, entity_id_param, progress_field) or None if invalid
        """
        entity_type = message.labels.get("entity_type")
        if not entity_type:
            logging.info(
                f"Task {message.task_name} has no entity_type, skipping progress state management"
            )
            return None

        entity_id_param = message.labels.get("entity_id_param")
        progress_field = message.labels.get("progress_field")

        if not entity_id_param or not progress_field:
            logging.error(
                f"Task {message.task_name} has entity_type but missing "
                f"entity_id_param or progress_field"
            )
            return None

        # Get entity ID from task arguments
        entity_id_str = (
            message.args[message.labels.get("entity_id_arg_index", 0)]
            if message.args
            else message.kwargs.get(entity_id_param)
        )

        if not entity_id_str:
            logging.error(
                f"Task {message.task_name} could not find entity ID "
                f"in args/kwargs for param {entity_id_param}"
            )
            return None

        try:
            entity_id = UUID(entity_id_str)
        except (ValueError, TypeError):
            logging.error(f"Task {message.task_name} has invalid UUID: {entity_id_str}")
            return None

        # Get entity class
        try:
            entity_class = entity_name_to_class_mapping[entity_type]
        except KeyError:
            logging.error(f"Unknown entity_type: {entity_type}")
            return None

        return entity_id, entity_class, entity_id_param, progress_field

    def _set_in_progress(self, message: TaskiqMessage, in_progress: bool) -> None:
        entity_info = self._get_entity_info(message)
        if not entity_info:
            return

        entity_id, entity_class, _, progress_field = entity_info
        entity_type = message.labels.get("entity_type")

        try:
            with sync_db_session() as db:
                db.execute(
                    update(entity_class)
                    .where(entity_class.id == entity_id)
                    .values({progress_field: in_progress})
                )
            logging.info(
                f"Set {entity_type}.{progress_field} = {in_progress} for {entity_id}"
            )
        except Exception as e:
            logging.error(
                f"Failed to set {entity_type}.{progress_field} = {in_progress} for {entity_id}: {e}"
            )

    def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        """Set *_in_progress = True before task execution."""
        self._set_in_progress(message, True)

        return message

    def post_execute(
        self,
        message: TaskiqMessage,
        result: TaskiqResult[Any],
    ) -> None:
        """Set *_in_progress = False after task execution and update result fields."""
        self._set_in_progress(message, False)

    def on_error(
        self,
        message: TaskiqMessage,
        result: TaskiqResult[Any],
        exception: BaseException,
    ) -> None:
        """Set *_in_progress = False if task fails."""
        self._set_in_progress(message, False)
