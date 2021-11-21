import threading
from typing import List, Callable


class MessagingQueue(threading.Thread):
    def __init__(self):
        pass

    def listen(self, callback_function: Callable):
        pass

    def stop(self):
        pass

    def send(self, msg: str, connector_id: str, work_id: str, bundles: List):
        pass
