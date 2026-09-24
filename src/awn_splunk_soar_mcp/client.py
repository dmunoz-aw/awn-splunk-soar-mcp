from typing import Any

import truststore

truststore.inject_into_ssl()

import requests

from .config import config


class SOARError(RuntimeError):
    pass


class SOARClient:
    """Read-only client for the Splunk SOAR REST API.

    Auth is via the classic `ph-auth-token` header (a plain SOAR API token),
    not the JWT-gated `/rest/mcp` endpoint some SOAR Cloud tenants expose.
    """

    def __init__(self) -> None:
        self.base_url = config.soar_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "ph-auth-token": config.require_token(),
                "Content-Type": "application/json",
            }
        )

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/rest{endpoint}"
        try:
            response = self.session.get(
                url, params=params, timeout=config.timeout, verify=config.verify_ssl
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise SOARError(
                f"SOAR API error {exc.response.status_code} on {endpoint}: "
                f"{exc.response.text[:500]}"
            ) from exc
        except requests.RequestException as exc:
            raise SOARError(f"SOAR API request failed for {endpoint}: {exc}") from exc
        return response.json()

    def _list(
        self,
        endpoint: str,
        page: int = 0,
        page_size: int = 50,
        sort: str | None = None,
        order: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "page_size": min(page_size, 500)}
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
        if filters:
            params.update(filters)
        return self._get(endpoint, params=params)

    # -- system --------------------------------------------------------

    def system_info(self) -> dict[str, Any]:
        return self._get("/system_info")

    # -- playbooks -------------------------------------------------------

    def list_playbooks(
        self,
        page: int = 0,
        page_size: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._list("/playbook", page=page, page_size=page_size, filters=filters)

    def get_playbook(self, playbook_id: int) -> dict[str, Any]:
        return self._get(f"/playbook/{playbook_id}")

    # -- playbook runs (execution history) --------------------------------

    def list_playbook_runs(
        self,
        page: int = 0,
        page_size: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._list(
            "/playbook_run", page=page, page_size=page_size, sort="start_time",
            order="desc", filters=filters,
        )

    def get_playbook_run(self, run_id: int) -> dict[str, Any]:
        return self._get(f"/playbook_run/{run_id}")

    # -- containers (cases/incidents) -----------------------------------

    def list_containers(
        self,
        page: int = 0,
        page_size: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._list("/container", page=page, page_size=page_size, filters=filters)

    def get_container(self, container_id: int) -> dict[str, Any]:
        return self._get(f"/container/{container_id}")

    # -- artifacts --------------------------------------------------------

    def list_artifacts(
        self,
        page: int = 0,
        page_size: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._list("/artifact", page=page, page_size=page_size, filters=filters)

    # -- custom functions --------------------------------------------------

    def list_custom_functions(self, page: int = 0, page_size: int = 50) -> dict[str, Any]:
        return self._list("/custom_function", page=page, page_size=page_size)

    # -- assets (connected apps) --------------------------------------------

    def list_assets(self, page: int = 0, page_size: int = 50) -> dict[str, Any]:
        return self._list("/asset", page=page, page_size=page_size)

    # -- app runs / action results ------------------------------------------

    def list_app_runs(
        self,
        page: int = 0,
        page_size: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._list(
            "/app_run", page=page, page_size=page_size, sort="start_time",
            order="desc", filters=filters,
        )


_client: SOARClient | None = None


def get_client() -> SOARClient:
    global _client
    if _client is None:
        _client = SOARClient()
    return _client
