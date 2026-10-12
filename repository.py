
import os

import psycopg
from psycopg.rows import dict_row


class PostgresTaskRepository:
    """Handles database operations for tasks."""

    def __init__(self, database_url=None):
        self.database_url = database_url or os.environ["DATABASE_URL"]

    def _connect(self):
        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    def get_all(self):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_by_id(self, task_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,),
            ).fetchone()
        return dict(row) if row else None

    def create(self, title):
        with self._connect() as connection:
            row = connection.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title, False),
            ).fetchone()
        return dict(row)

    def update(self, task_id, title=None, done=None):
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id FROM tasks WHERE id = %s",
                (task_id,),
            ).fetchone()

            if existing is None:
                return None

            if title is not None:
                connection.execute(
                    "UPDATE tasks SET title = %s WHERE id = %s",
                    (title, task_id),
                )

            if done is not None:
                connection.execute(
                    "UPDATE tasks SET done = %s WHERE id = %s",
                    (done, task_id),
                )

            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,),
            ).fetchone()

        return dict(row)

    def delete(self, task_id):
        with self._connect() as connection:
            result = connection.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id",
                (task_id,),
            ).fetchone()
        return result is not None
