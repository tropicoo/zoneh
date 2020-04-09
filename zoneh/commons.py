"""Common things module."""

from threading import Thread


class CommonThread(Thread):
    """Common (base) thread class with run trigger."""

    def __init__(self):
        """Class constructor."""
        super().__init__()
        self._run_trigger = None

    def run(self):
        """Run thread."""
        if self._run_trigger is None:
            raise ValueError('Run trigger cannot be None')
        self._run()

    def add_run_trigger(self, run_trigger):
        """Add thread run trigger for execution control from thread manager."""
        self._run_trigger = run_trigger

    def _run(self):
        """Real thread run method."""
        raise NotImplementedError
