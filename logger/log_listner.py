from multiprocessing import Process, Queue, Pipe
from logging import getLogger
from .log_configure import main_logger_configure


class LogListenerProcess(Process):

    def __init__(self, queue: Queue, pipe: Pipe, configure: main_logger_configure, verifying_message: str):
        super(LogListenerProcess, self).__init__()
        self.queue = queue
        self.pipe = pipe
        self.verifying_message = verifying_message
        self.configure = configure

    def run(self):
        self.configure()
        if self.pipe.poll(timeout=5):
            assert self.pipe.recv() == self.verifying_message, "MainProcess didn't send message."
            self.pipe.send(self.verifying_message)
        while True:
            try:
                record = self.queue.get()
                if record is None:
                    break
                logger = getLogger(record.name)
                logger.handle(record)
            except Exception as e:
                import sys
                print(e.args, file=sys.stderr)
        print("[End Listener Process]")
