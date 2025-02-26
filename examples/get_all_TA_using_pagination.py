# coding: utf-8
from more_itertools.more import first

from pycti import OpenCTIApiClient

# Variables
api_url = "http://localhost:4000"
api_token = "d434ce02-e58e-4cac-8b4c-42bf16748e84"

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

# List all TA
actors = opencti_api_client.threat_actor.list()

# Print

print(actors)
