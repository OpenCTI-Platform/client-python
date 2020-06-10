import os

import pytest
import json

from utils.splix_splitter import StixSplitter

def test_split_bundle():

    stix_splitter = StixSplitter()
    with open('../../tests/data/enterprise-attack.json') as file:
        content = file.read()
        bundles = stix_splitter.split_bundle(content)
    assert len(bundles) == 7031
