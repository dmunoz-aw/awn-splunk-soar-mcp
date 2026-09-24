"""Read-only MCP server for Splunk SOAR (awnsoar.soar.splunkcloud.com).

Exposes list/get tools over the classic `/rest/*` SOAR API. No tool in this
server can create, update, run, or delete anything in SOAR.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import SOARError, get_client

mcp = FastMCP("awn-splunk-soar-mcp")


def _wrap(fn, *args, **kwargs) -> dict[str, Any]:
    try:
        return fn(*args, **kwargs)
    except SOARError as exc:
        return {"error": str(exc)}


@mcp.tool()
def soar_system_info() -> dict[str, Any]:
    """Get SOAR instance system info (base URL, timezone, machine id). Use this
    first to confirm connectivity and which instance you're talking to."""
    return _wrap(get_client().system_info)


@mcp.tool()
def soar_list_playbooks(
    page: int = 0,
    page_size: int = 50,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """List playbooks (name, active/scm state, tags, repo). Optional dict of raw
    SOAR REST filter query params, e.g. {"_filter_active": "true"} or
    {"_filter_name__contains": '"phish"'} (string values in SOAR filters must
    be double-quoted inside the value). See SOAR REST API docs for the full
    `_filter_<field>[__<op>]` syntax."""
    return _wrap(get_client().list_playbooks, page=page, page_size=page_size, filters=filters)


@mcp.tool()
def soar_get_playbook(playbook_id: int) -> dict[str, Any]:
    """Get full detail for a single playbook by id, including its canvas/steps."""
    return _wrap(get_client().get_playbook, playbook_id)


@mcp.tool()
def soar_list_playbook_runs(
    page: int = 0,
    page_size: int = 50,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """List playbook execution runs, newest first (status, start/end time,
    container, message). Use filters like {"_filter_playbook": "<id>"} or
    {"_filter_container": "<id>"} to scope to one playbook or case. This is
    the source of truth for "last run" and run-frequency questions."""
    return _wrap(get_client().list_playbook_runs, page=page, page_size=page_size, filters=filters)


@mcp.tool()
def soar_get_playbook_run(run_id: int) -> dict[str, Any]:
    """Get full detail/result for a single playbook run by id."""
    return _wrap(get_client().get_playbook_run, run_id)


@mcp.tool()
def soar_list_containers(
    page: int = 0,
    page_size: int = 50,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """List SOAR containers (cases/incidents) — label, status, tags,
    severity, owner, create/close time."""
    return _wrap(get_client().list_containers, page=page, page_size=page_size, filters=filters)


@mcp.tool()
def soar_get_container(container_id: int) -> dict[str, Any]:
    """Get full detail for a single container (case/incident) by id."""
    return _wrap(get_client().get_container, container_id)


@mcp.tool()
def soar_list_artifacts(
    page: int = 0,
    page_size: int = 50,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """List artifacts. Use filters like {"_filter_container": "<id>"} to scope
    to a single container/case."""
    return _wrap(get_client().list_artifacts, page=page, page_size=page_size, filters=filters)


@mcp.tool()
def soar_list_custom_functions(page: int = 0, page_size: int = 50) -> dict[str, Any]:
    """List custom functions available in SOAR."""
    return _wrap(get_client().list_custom_functions, page=page, page_size=page_size)


@mcp.tool()
def soar_list_assets(page: int = 0, page_size: int = 50) -> dict[str, Any]:
    """List configured SOAR assets (connected apps/integrations)."""
    return _wrap(get_client().list_assets, page=page, page_size=page_size)


@mcp.tool()
def soar_list_app_runs(
    page: int = 0,
    page_size: int = 50,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """List app/action run results, newest first. Use filters like
    {"_filter_playbook_run": "<id>"} to scope to one playbook run."""
    return _wrap(get_client().list_app_runs, page=page, page_size=page_size, filters=filters)


def main() -> None:
    mcp.run()
