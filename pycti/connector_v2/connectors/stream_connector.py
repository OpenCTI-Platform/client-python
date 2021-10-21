from pycti.connector_v2.connector import Connector


class StreamConnector(Connector):
    def __init__(self):
        super().__init__()

    def listen_stream(
        self,
        message_callback,
        url=None,
        token=None,
        verify_ssl=None,
        start_timestamp=None,
        live_stream_id=None,
    ) -> ListenStream:
        """listen for messages and register callback function

        :param message_callback: callback function to process messages
        """

        self.listen_stream = ListenStream(
            self,
            message_callback,
            url,
            token,
            verify_ssl,
            start_timestamp,
            live_stream_id,
        )
        self.listen_stream.start()
        return self.listen_stream
