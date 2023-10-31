import requests


class OpenCTIApiAuthentication(requests.auth.AuthBase):
    def __init__(
        self,
        bearer_token,
        pycti_version,
        proxies,
        verify,
        cert,
    ):
        super().__init__()
        self.pycti_version = pycti_version
        self.bearer_token = bearer_token
        self.proxies = proxies
        self.verify = verify
        self.cert = cert
        self.headers = {
            "User-Agent": "pycti/" + self.pycti_version,
            "Authorization": "Bearer " + self.bearer_token,
        }

    def __call__(self, r):
        r.headers.update(self.headers)
        r.proxies = self.proxies
        r.verify = self.verify
        r.cert = self.cert

        return r

    def set_custom_header(self, key: str, value: str):
        if key is not None and value is not None:
            self.headers.update({key: value})
        else:
            raise ValueError("Key and/or value parameters are not of string type.")
