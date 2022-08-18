"""OpenCTI entity operations"""

import uuid
from typing import Any, Dict
from warnings import warn

from stix2.canonicalization.Canonicalize import canonicalize


def _generate_uuid5(prefix: str, data: Dict[str, Any]) -> str:
    """
    Generate an OpenCTI uuid5 identifier.

    :param prefix: Identifier prefix
    :param data: Namespace data
    :return: A uuid5 identifier
    """
    stix_cyber_object_namespace = "00abedb4-aa42-466c-9c01-fed23315a9b7"
    data = canonicalize(data, utf8=False)
    id = str(uuid.uuid5(uuid.UUID(stix_cyber_object_namespace), data))
    return f"{prefix}--{id}"


def _check_for_deprecated_parameter(
    old_name: str,
    new_name: str,
    existing_value: Any,
    kwargs: Dict[str, Any],
) -> Any:
    """
    Check if a deprecated function parameter is in use and warn if so.

    :param old_name: The old name of the parameter
    :param new_name: The new name of the parameter
    :param existing_value: The current parameter value
    :param kwargs: Keyword arguments from the method
    :return: The value from the old name, or the existing value
    """
    if old_name in kwargs:
        warn(
            f"The parameter {old_name} has been superseded by {new_name}",
            DeprecationWarning,
            stacklevel=2,
        )
        return kwargs.pop(old_name)

    return existing_value


def _check_for_excess_parameters(
    kwargs: Dict[str, Any],
) -> None:
    """
    Check for extra parameters and warn if any are present.

    :param kwargs: Keyword arguments from the method
    :return: None
    """
    if kwargs:
        for key in kwargs:
            warn(f"Excess parameter {key}", SyntaxWarning, stacklevel=2)
