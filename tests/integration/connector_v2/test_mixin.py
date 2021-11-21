import pytest
from requests import HTTPError

from tests.integration.support_cases.mixins import SuccessMixinTests, FailMixinTests
from pytest_cases import parametrize_with_cases


@parametrize_with_cases("mixin", cases=SuccessMixinTests)
def test_mixin(mixin, httpserver):
    content = mixin.run(httpserver)
    for elem in mixin.result_values():
        assert elem in str(content)


@parametrize_with_cases("mixin", cases=FailMixinTests)
def test_mixin_fail(mixin, httpserver):
    with pytest.raises(HTTPError, match=rf".* {mixin.error_value()} .*"):
        mixin.run(httpserver)
