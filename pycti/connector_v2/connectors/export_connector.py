from pycti.connector_v2.connector import Connector


class ExportConnector(Connector):
    def __init__(self):
        super().__init__()

    def listen(self, messaging_queue, message_callback: Callable[[Dict], str]) -> None:
        """listen for messages and register callback function

        :param message_callback: callback function to process messages
        :type message_callback: Callable[[Dict], str]
        """

        self.listen_queue = ListenQueue(self, self.config, message_callback)
        self.listen_queue.start()