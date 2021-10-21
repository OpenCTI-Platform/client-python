class ListenStream(threading.Thread):
    def __init__(
        self, helper, callback, url, token, verify_ssl, start_timestamp, live_stream_id
    ) -> None:
        threading.Thread.__init__(self)
        self.helper = helper
        self.callback = callback
        self.url = url
        self.token = token
        self.verify_ssl = verify_ssl
        self.start_timestamp = start_timestamp
        self.live_stream_id = live_stream_id
        self.exit = False

    def run(self) -> None:  # pylint: disable=too-many-branches
        current_state = self.helper.get_state()
        if current_state is None:
            current_state = {
                "connectorLastEventId": f"{self.start_timestamp}-0"
                if self.start_timestamp is not None and len(self.start_timestamp) > 0
                else "-"
            }
            self.helper.set_state(current_state)

        # If URL and token are provided, likely consuming a remote stream
        if self.url is not None and self.token is not None:
            # If a live stream ID, appending the URL
            if self.live_stream_id is not None:
                live_stream_uri = f"/{self.live_stream_id}"
            elif self.helper.connect_live_stream_id is not None:
                live_stream_uri = f"/{self.helper.connect_live_stream_id}"
            else:
                live_stream_uri = ""
            # Live stream "from" should be empty if start from the beginning
            if (
                self.live_stream_id is not None
                or self.helper.connect_live_stream_id is not None
            ):
                live_stream_from = (
                    f"?from={current_state['connectorLastEventId']}"
                    if current_state["connectorLastEventId"] != "-"
                    else ""
                )
            # Global stream "from" should be 0 if starting from the beginning
            else:
                live_stream_from = "?from=" + (
                    current_state["connectorLastEventId"]
                    if current_state["connectorLastEventId"] != "-"
                    else "0"
                )
            live_stream_url = f"{self.url}/stream{live_stream_uri}{live_stream_from}"
            opencti_ssl_verify = (
                self.verify_ssl if self.verify_ssl is not None else True
            )
            logging.info(
                "%s",
                (
                    "Starting listening stream events (URL: "
                    f"{live_stream_url}, SSL verify: {opencti_ssl_verify})"
                ),
            )
            messages = SSEClient(
                live_stream_url,
                headers={"authorization": "Bearer " + self.token},
                verify=opencti_ssl_verify,
            )
        else:
            live_stream_uri = (
                f"/{self.helper.connect_live_stream_id}"
                if self.helper.connect_live_stream_id is not None
                else ""
            )
            if self.helper.connect_live_stream_id is not None:
                live_stream_from = (
                    f"?from={current_state['connectorLastEventId']}"
                    if current_state["connectorLastEventId"] != "-"
                    else ""
                )
            # Global stream "from" should be 0 if starting from the beginning
            else:
                live_stream_from = "?from=" + (
                    current_state["connectorLastEventId"]
                    if current_state["connectorLastEventId"] != "-"
                    else "0"
                )
            live_stream_url = (
                f"{self.helper.opencti_url}/stream{live_stream_uri}{live_stream_from}"
            )
            logging.info(
                "%s",
                (
                    f"Starting listening stream events (URL: {live_stream_url}"
                    f", SSL verify: {self.helper.opencti_ssl_verify})"
                ),
            )
            messages = SSEClient(
                live_stream_url,
                headers={"authorization": "Bearer " + self.helper.opencti_token},
                verify=self.helper.opencti_ssl_verify,
            )
        # Iter on stream messages
        for msg in messages:
            if self.exit:
                break
            if msg.event == "heartbeat" or msg.event == "connected":
                continue
            if msg.event == "sync":
                if msg.id is not None:
                    state = self.helper.get_state()
                    state["connectorLastEventId"] = str(msg.id)
                    self.helper.set_state(state)
            else:
                self.callback(msg)
                if msg.id is not None:
                    state = self.helper.get_state()
                    state["connectorLastEventId"] = str(msg.id)
                    self.helper.set_state(state)

    def stop(self):
        self.exit = True
