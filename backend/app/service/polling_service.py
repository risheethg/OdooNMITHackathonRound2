import asyncio
import inspect
from core.logger import logs
from typing import List, Callable, Coroutine

class PollingService:
    """
    Manages a background task that periodically runs a list of registered jobs.
    """
    def __init__(self, interval_seconds: int = 60):
        self._task = None
        self._is_running = False
        self.interval = interval_seconds
        # This will hold all the functions we want to run on each interval
        self.tasks_to_run: List[Callable[[], Coroutine]] = []

    def register_task(self, task: Callable[[], Coroutine]):
        """
        Allows other parts of the application to register a task to be run by the poller.
        A task must be an async function that takes no arguments.
        """
        self.tasks_to_run.append(task)
        logs.define_logger(20, f"Task '{task.__name__}' registered with polling service.", loggName=inspect.stack()[0])

    async def start_polling(self):
        """Starts the background polling task."""
        if not self._is_running:
            self._is_running = True
            self._task = asyncio.create_task(self._poll_runner())
            logs.define_logger(20, "Database polling service started.", loggName=inspect.stack()[0])

    async def stop_polling(self):
        """Stops the background polling task gracefully."""
        if self._is_running and self._task:
            self._is_running = False
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logs.define_logger(20, "Database polling service stopped.", loggName=inspect.stack()[0])

    async def _poll_runner(self):
        """
        The core polling loop. It now iterates through and runs all registered tasks.
        """
        while self._is_running:
            try:
                # Run all registered tasks concurrently
                tasks = [task() for task in self.tasks_to_run]
                await asyncio.gather(*tasks)
                
            except Exception as e:
                logs.define_logger(50, f"An error occurred during polling run: {e}", loggName=inspect.stack()[0])
            
            await asyncio.sleep(self.interval)

# Create a single instance to be used throughout the application
polling_service = PollingService(interval_seconds=30)

