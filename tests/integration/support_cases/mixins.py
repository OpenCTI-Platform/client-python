from typing import List

from pytest_httpserver import HTTPServer

from pycti.connector_v2.libs.mixins.http import HttpMixin


class SuccessMixinTests:
    @staticmethod
    def case_success_http_mixin():
        return HttpMixinTest()


class FailMixinTests:
    @staticmethod
    def case_fail_404_http_mixin():
        return HttpMixin404Test()


class HttpMixinTest:
    @staticmethod
    def result_values() -> List:
        return ["https://twitter.com/LuatixHQ"]

    @staticmethod
    def run(httpserver: HTTPServer):
        http_mixin = HttpMixin()

        body = "href='https://twitter.com/LuatixHQ' target="
        endpoint = "/en"
        httpserver.expect_request(endpoint).respond_with_data(body)

        return http_mixin.get(httpserver.url_for(endpoint))


class HttpMixin404Test:
    @staticmethod
    def error_value() -> int:
        return 404

    @staticmethod
    def run(httpserver):
        http_mixin = HttpMixin()

        endpoint = "/en"
        httpserver.expect_request(endpoint).respond_with_data(
            "Not found", status=404, content_type="text/plain"
        )

        return http_mixin.get(httpserver.url_for(endpoint))
