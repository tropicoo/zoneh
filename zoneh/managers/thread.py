"""Thread managers module."""

from threading import Event


class ThreadManager:
    """Thread manager.

    Manage passed threads.
    """

    def __init__(self, threads):
        """Class constructor."""
        self._threads = threads
        self._running_threads = []

        self._should_run = Event()
        self._should_run.set()

    def start_threads(self):
        """Start threads."""
        for thread in self._threads:
            thread.add_run_trigger(run_trigger=self._should_run)
            thread.start()
            self._running_threads.append(thread)

    def stop_threads(self):
        """Stop threads."""
        self._should_run.clear()
