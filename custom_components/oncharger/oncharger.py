"""Oncharger integration."""
from __future__ import annotations

import logging
from typing import Any

from urllib.parse import urlparse, ParseResult
import requests

from .const import (
    HTTP_TIMEOUT,
    IP_ADDRESS,
    USERNAME,
    PASSWORD,
)


_LOGGER = logging.getLogger(__name__)
API_BASE = "https://my.oncharger.com/api"


class Oncharger:
    """Oncharger instance."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Init oncharger."""
        self._ip_address = data.get(IP_ADDRESS)
        self._username = data[USERNAME]
        self._password = data[PASSWORD]

    def get_config(self) -> dict[str, Any]:
        """Get config data for Oncharger component."""
        return self._get_request(path="config")

    def get_status(self) -> dict[str, Any]:
        """Get status data for Oncharger component."""
        data = self._get_request(path="status")

        if data.get("isOnline") is False:
            raise ConnectionError("Device is offline")

        return data

    def set_max_charging_current(self, charging_current: float) -> None:
        """Set Oncharger max charging current."""
        if self._ip_address:
            self._get_request(path="api", query=f"param=pilot&value={charging_current}")
        else:
            self._get_request(
                path="update", query=f"param=maxCurrent&value={charging_current}"
            )

    def set_lock_unlock(self, lock: bool) -> None:
        """Set Oncharger lock/unlock."""
        if self._ip_address:
            self._get_request(path="api", query=f"param=lock&value={str(lock).lower()}")
        else:
            self._get_request(
                path="update", query=f"param=loc&value={str(lock).lower()}"
            )

    def set_boost_config(
        self, conn: int, amp: int, is_total_limit: int, ip: string
    ) -> None:
        """Set Oncharger boost config."""
        if self._ip_address:
            self._get_request(
                path="save-pm",
                query=f"conn={conn}&amp={amp}&isTotalLimit={is_total_limit}&ip={ip}",
            )
        else:
            config = f"{conn}|{amp}|{is_total_limit}|{ip}"
            self._get_request(path="update", query=f"param=cb_config&value={config}")

    @property
    def _api_url(self) -> ParseResult:
        """Get base Oncharger API URL."""
        if self._ip_address:
            return urlparse(f"http://{self._ip_address}")._replace(
                query=f"login={self._username}&pass={self._password}"
            )

        return urlparse(API_BASE)

    def _get_request(self, path: str, query: str | None = None) -> dict[str, Any]:
        """Make GET request to the Oncharger API."""
        url = self._api_url._replace(path="/".join([self._api_url.path, path]))
        if query:
            url = url._replace(query="&".join([self._api_url.query, query]))

        headers = {
            "x-ocid": self._username,
            "x-password": self._password,
        }
        _LOGGER.debug(f"Oncharger request: GET {url.geturl()}")
        try:
            r = requests.get(url.geturl(), headers=headers, timeout=HTTP_TIMEOUT)
            r.raise_for_status()
            _LOGGER.debug(f"Oncharger status: {r.status_code}")
            _LOGGER.debug(f"Oncharger response: {r.text}")
            json = r.json()

            if json.get("err.auth.msg"):
                raise Forbidden(response=r)

            return json
        except TimeoutError as timeout_error:
            raise ConnectionError from timeout_error
        except requests.exceptions.ConnectionError as connection_error:
            raise ConnectionError from connection_error
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code == 403:
                raise Forbidden from http_error
            raise ConnectionError from http_error


class Forbidden(requests.exceptions.RequestException):
    """Error to indicate there is forbidden response."""
