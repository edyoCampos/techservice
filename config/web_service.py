from requests_ratelimiter import LimiterSession
import requests


class WebService:
    def __init__(self, authorization, content_type, per_second=120):
        self.session = LimiterSession(per_second=per_second)
        self.headers = {
            "Authorization": authorization,
            "Content-Type": content_type,
        }

    def request(self, url, method, body="", headers={}):
        all_headers = self.headers.copy()
        all_headers.update(headers)

        response = self.session.request(
            method, url, headers=all_headers, data=body)

        response = self.handle_response(response)

        return response

    def handle_response(self, response):
        if response.status_code >= 400:
            self.handle_error(response)
        return response

    def handle_error(self, response):
        raise NotImplementedError


class MyWebService(WebService):
    def handle_error(self, response):
        # Lógica específica para tratar erros
        print(f"Ocorreu um erro: {response.status_code}")
