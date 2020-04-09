from threading import Thread


class CommonThread(Thread):
    def __init__(self):
        super().__init__()
        self._run_trigger = None

    def run(self):
        if self._run_trigger is None:
            raise ValueError('Run trigger cannot be None')
        self._run()

    def add_run_trigger(self, run_trigger):
        self._run_trigger = run_trigger

    def _run(self):
        raise NotImplementedError
