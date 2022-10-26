from typing import Dict, Tuple

import requests

# example: https://github.com/certtools/intelmq/blob/d4adbd57ed8bb7e7fa14e7d2132db2ac1fd97658/intelmq/bots/collectors/http/collector_http_stream.py
from requests import HTTPError


class HttpMixin(object):
    _session: requests.Session = None

    def __init__(self):
        self._session = requests.Session()
        super().__init__()

    def _setup(self):
        self._session = requests.Session()

    def get(
        self, url: str, params: Dict = None, headers: Dict = None, auth: Tuple = None
    ):
        if self._session is None:
            self._setup()

        try:
            response = self._session.get(
                url, timeout=10, params=params, headers=headers, auth=auth
            )

            response.raise_for_status()
        except HTTPError as http_err:
            raise HTTPError(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise HTTPError(f"Another HTTP error occurred: {err}")

        return response.content
