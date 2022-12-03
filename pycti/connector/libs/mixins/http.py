import time
from typing import Dict

import requests
from requests import HTTPError

RETRY_ERROR_CODES = [408, 500, 501, 502, 503, 504]


class HttpMixin(object):
    _session: requests.Session = None

    def __init__(self) -> None:
        self._setup()
        super().__init__()

    def _setup(self) -> None:
        self._session = requests.Session()

    def _retrieve(self, url: str, cmd: str, args: Dict = None, retry_cnt: int = 3):
        if self._session is None:
            self._setup()

        if args is None:
            args = {}

        try:
            request_function = getattr(self._session, cmd)
            response = request_function(url, **args)

            response.raise_for_status()
        except HTTPError as http_err:
            if retry_cnt > 0:
                if (
                    http_err.response.status_code in RETRY_ERROR_CODES
                ):  # request timeout
                    time.sleep(3)
                    return self._retrieve(url, cmd, args, retry_cnt - 1)

            raise HTTPError(f"HTTP error occurred: {http_err}")
        except AttributeError as e:
            raise NotImplementedError(
                f"Error requests function '{cmd}' is not supported: {e}"
            )
        except Exception as err:
            raise HTTPError(f"Another HTTP error occurred: {err}")

        return response.content

    def http_get(self, url: str, args: Dict = None, retry_cnt: int = 3):
        return self._retrieve(url, "get", args, retry_cnt)

    def http_post(self, url: str, args: Dict = None, retry_cnt: int = 3):
        return self._retrieve(url, "post", args, retry_cnt)
