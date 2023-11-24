from typing import Dict, Optional, Tuple, Union

import requests


class OpenCTIApiAuthentication(requests.auth.AuthBase):
    """
    Custom authentication class for OpenCTI API requests.

    This class is used to add necessary configuration to the
    requests sent to the OpenCTI API. It extends requests'
    AuthBase to integrate with the requests library.

    Attributes:
        pycti_version (str): Version of the pycti client.
        bearer_token (str): Bearer token for authentication.
        proxies (Optional[Dict[str, str]]): Proxies configuration.
        verify (Union[bool, str]): SSL certificate verification setting.
        cert (Optional[Union[str, Tuple[str, str]]]): Client-side certificates.
        headers (Dict[str, str]): Headers to include in each request.

    Parameters:
        bearer_token (str): Bearer token for OpenCTI API authentication.
        pycti_version (str): The version of the pycti client being used.
        proxies (Optional[Dict[str, str]]): Proxies to use for the requests.
        verify (Union[bool, str]): Whether to verify SSL certificates or a path to CA bundle.
        cert (Optional[Union[str, Tuple[str, str]]]): Client-side certificates.
    """

    def __init__(
        self,
        bearer_token: str,
        pycti_version: str,
        proxies: Optional[Dict[str, str]],
        verify: Union[bool, str],
        cert: Optional[Union[str, Tuple[str, str]]],
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

    def __call__(self, r) -> requests.Request:
        """
        Update the request with authentication headers, proxies, and SSL settings.

        Parameters:
            r (requests.Request): The request object to be modified.

        Returns:
            requests.Request: The modified request object.
        """
        r.headers.update(self.headers)
        r.proxies = self.proxies
        r.verify = self.verify
        r.cert = self.cert

        return r

    def set_custom_header(self, key: str, value: str):
        """
        Set or update a custom header for the requests.

        Parameters:
            key (str): The header name.
            value (str): The header value.

        Raises:
            ValueError: If either key or value is not a string.
        """
        if key is not None and value is not None:
            self.headers.update({key: value})
        else:
            raise ValueError("Key and/or value parameters are not of string type.")
