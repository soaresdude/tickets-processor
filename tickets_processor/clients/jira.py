import json
from dataclasses import dataclass
from logging import Logger, getLogger

import backoff
import httpx
from httpx import Response, Request

from core.config import settings


@dataclass
class JiraClient:
    base_url: str = settings.JIRA_BASE_URL
    user: str = settings.JIRA_USER
    token: str = settings.JIRA_API_TOKEN
    logger: Logger = getLogger(__name__)

    def _get_headers(self) -> dict:
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _extract_request_as_dict(request: Request):
        return {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "payload": json.loads(request.read()),
        }

    @staticmethod
    def _extract_response_as_dict(response: Response):
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "payload": response.json(),
        }

    def logging_response_hook_wrapper(self):
        async def logging_response_hook(response: Response, *args, **kwargs) -> None:
            await response.aread()

            extra = {
                "extra": {
                    "request": self._extract_request_as_dict(response.request),
                    "response": self._extract_response_as_dict(response),
                }
            }

            if response.is_success:
                self.logger.info(
                    "http.response",
                    extra=extra,
                )
            elif response.is_error:
                self.logger.error(
                    "http.response",
                    extra=extra,
                )

        return logging_response_hook

    @backoff.on_exception(backoff.expo, httpx.HTTPError, max_tries=8)
    def _get_session(self) -> httpx.AsyncClient:
        client_session = httpx.AsyncClient(headers=self._get_headers())
        client_session.event_hooks["response"] = [self.logging_response_hook_wrapper()]

        return client_session

    @backoff.on_exception(backoff.expo, httpx.HTTPError, max_tries=8)
    async def post(self, data: dict, path: str):
        async with self._get_session() as session:
            response = await session.post(self.base_url + path,
                                          json=data,
                                          auth=(settings.JIRA_USER, settings.JIRA_API_TOKEN))
            if response.status_code >= 400:
                response.raise_for_status()
            return response.json()
