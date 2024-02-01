# coding: utf-8

from pycti import OpenCTIApiClient

from python_scripts.testing.test import CTIclient

# Variables
api_url = "http://opencti:4000"
api_token = "bfa014e0-e02e-4aa6-a42b-603b19dcf159"

# OpenCTI initialization
cticlient = OpenCTIApiClient(api_url, api_token)

def search_observable(key, values):
    """
    Search for an observable in OpenCTI based on a key-value pair.

    Args:
        key (str): The key to search for in this case the value.
        values (list): A list of values to match against(could be Ip address or hash).

    Returns:
        dict or None: The matching observable if found, None otherwise.
    """
    observable = cticlient.stix_cyber_observable.read(
        filters=[
            {
                "key": key,
                "values": values,
            }
        ]
    )
    if observable is None:
        print("Value not found")
    else:
        return observable

# Exact IP match
ip_observable = search_observable("value", ["110.172.180.180"])
print(ip_observable)

# Exact File name match
file_name_observable = search_observable("value", ["activeds.dll"])
print(file_name_observable)

# Exact File hash match
file_hash_observable = search_observable("value", ["3aad33e025303dbae12c12b4ec5258c1"])
print(file_hash_observable)