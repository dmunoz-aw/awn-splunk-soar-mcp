# awn-splunk-soar-mcp

Read-only MCP server for Splunk SOAR (AWS Managed Cloud). Exposes playbooks,
playbook runs, containers (cases), artifacts, assets, custom functions, and
app runs as MCP tools so an agent can audit and investigate SOAR without
being able to create, update, run, or delete anything.

## Why this exists

The SOAR instance's own `/rest/mcp` endpoint requires a JWT bearer token,
which isn't what a standard SOAR "API Token" is. This server instead talks to
the classic, stable `/rest/*` SOAR REST API using the plain API token via the
`ph-auth-token` header — the same auth pattern used by `esrm-soar-playbooks`'
`soar_cli`.

## Setup

```bash
uv sync
cp .env.example .env
# edit .env: set SOAR_MCP_TOKEN to a SOAR API token (SOAR admin -> Users ->
# your user -> API Token). SOAR_URL defaults to the AWN prod instance.
```

Test it standalone:

```bash
uv run awn-splunk-soar-mcp
```

## Wiring into Claude Code

Add to your MCP config (e.g. `~/.claude.json`), pointing at this checkout:

```json
"soar-mcp-server": {
  "command": "uv",
  "args": [
    "--directory",
    "/absolute/path/to/awn-splunk-soar-mcp",
    "run",
    "awn-splunk-soar-mcp"
  ],
  "env": {
    "SOAR_MCP_TOKEN": "${SOAR_MCP_TOKEN}"
  }
}
```

`SOAR_MCP_TOKEN` should already be set in your shell environment (e.g.
`~/.zshrc`) — it's referenced here, not hardcoded.

## Tools

- `soar_system_info`
- `soar_list_playbooks` / `soar_get_playbook`
- `soar_list_playbook_runs` / `soar_get_playbook_run`
- `soar_list_containers` / `soar_get_container`
- `soar_list_artifacts`
- `soar_list_custom_functions`
- `soar_list_assets`
- `soar_list_app_runs`

All list tools accept `page`, `page_size`, and an optional `filters` dict of
raw SOAR REST `_filter_<field>[__<op>]` query params.

## Scope

Read-only by design — no `create_*`, `update_*`, `run_*`, or `delete_*`
tools. If write/action capability is ever needed, it should be added as
clearly-separate, individually-permissioned tools, not folded into this
server's default surface.
