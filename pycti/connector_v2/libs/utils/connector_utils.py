import ssl
from typing import List


def create_ssl_context() -> ssl.SSLContext:
    """Set strong SSL defaults: require TLSv1.2+

    `ssl` uses bitwise operations to specify context `<enum 'Options'>`
    """

    ssl_context_options: List[int] = [
        ssl.OP_NO_COMPRESSION,
        ssl.OP_NO_TICKET,  # pylint: disable=no-member
        ssl.OP_NO_RENEGOTIATION,  # pylint: disable=no-member
        ssl.OP_SINGLE_DH_USE,
        ssl.OP_SINGLE_ECDH_USE,
    ]
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_context.options &= ~ssl.OP_ENABLE_MIDDLEBOX_COMPAT  # pylint: disable=no-member
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    for option in ssl_context_options:
        ssl_context.options |= option

    return ssl_context
