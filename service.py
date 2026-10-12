
from repository import PostgresTaskRepository


class TaskService:
    """Provides the task operations used by the API."""

    def __init__(self, repository=None):
        self.repository = repository or PostgresTaskRepository()

    def get_all_tasks(self):
        return self.repository.get_all()

    def get_task(self, task_id):
        return self.repository.get_by_id(task_id)

    def create_task(self, title):
        return self.repository.create(title)

    def update_task(self, task_id, title=None, done=None):
        return self.repository.update(
            task_id,
            title=title,
            done=done,
        )

    def delete_task(self, task_id):
        return self.repository.delete(task_id)
