from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


SECRET_KEYS = {"api_key", "secret", "token", "password"}


@dataclass(frozen=True)
class RedashExportConfig:
    base_url: str
    api_key: str
    dashboard_ids: list[str]
    output_dir: Path


def export_redash_assets(config: RedashExportConfig) -> dict[str, list[str]]:
    if not config.dashboard_ids:
        raise ValueError("At least one Redash dashboard id is required")

    dashboards_dir = config.output_dir / "dashboards"
    queries_dir = config.output_dir / "queries"
    dashboards_dir.mkdir(parents=True, exist_ok=True)
    queries_dir.mkdir(parents=True, exist_ok=True)

    exported_queries: set[str] = set()
    for dashboard_id in sorted(config.dashboard_ids):
        dashboard = _get_json(config, f"/api/dashboards/{dashboard_id}")
        _write_json(dashboards_dir / f"{dashboard_id}.json", _strip_secrets(dashboard))

        for query_id in sorted(_query_ids_from_dashboard(dashboard), key=int):
            if query_id in exported_queries:
                continue
            query = _get_json(config, f"/api/queries/{query_id}")
            _write_json(queries_dir / f"{query_id}.json", _strip_secrets(query))
            exported_queries.add(query_id)

    manifest = {
        "dashboards": sorted(config.dashboard_ids),
        "queries": sorted(exported_queries, key=int),
    }
    _write_json(config.output_dir / "manifest.json", manifest)
    return manifest


def config_from_env() -> RedashExportConfig:
    base_url = os.environ.get("REDASH_URL")
    api_key = os.environ.get("REDASH_API_KEY")
    dashboard_ids = _split_csv(os.environ.get("REDASH_DASHBOARD_IDS", ""))
    output_dir = Path(os.environ.get("REDASH_EXPORT_DIR", "redash/exports"))

    missing = [
        name
        for name, value in {
            "REDASH_URL": base_url,
            "REDASH_API_KEY": api_key,
            "REDASH_DASHBOARD_IDS": dashboard_ids,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required Redash export configuration: {', '.join(missing)}")

    return RedashExportConfig(
        base_url=base_url or "",
        api_key=api_key or "",
        dashboard_ids=dashboard_ids,
        output_dir=output_dir,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export Redash dashboards and queries")
    parser.add_argument("--redash-url", default=os.environ.get("REDASH_URL"))
    parser.add_argument("--api-key", default=os.environ.get("REDASH_API_KEY"))
    parser.add_argument("--dashboard-ids", default=os.environ.get("REDASH_DASHBOARD_IDS", ""))
    parser.add_argument("--output-dir", default=os.environ.get("REDASH_EXPORT_DIR", "redash/exports"))
    args = parser.parse_args(argv)

    missing = [
        option
        for option, value in {
            "--redash-url": args.redash_url,
            "--api-key": args.api_key,
            "--dashboard-ids": args.dashboard_ids,
        }.items()
        if not value
    ]
    if missing:
        parser.error(f"missing required configuration: {', '.join(missing)}")

    manifest = export_redash_assets(
        RedashExportConfig(
            base_url=args.redash_url,
            api_key=args.api_key,
            dashboard_ids=_split_csv(args.dashboard_ids),
            output_dir=Path(args.output_dir),
        )
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _get_json(config: RedashExportConfig, path: str) -> Any:
    request = Request(
        urljoin(config.base_url.rstrip("/") + "/", path.lstrip("/")),
        headers={"Authorization": f"Key {config.api_key}"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Redash API request failed: {exc.code} {path}: {detail}") from exc


def _query_ids_from_dashboard(dashboard: dict[str, Any]) -> set[str]:
    query_ids: set[str] = set()
    for widget in dashboard.get("widgets", []):
        visualization = widget.get("visualization") or {}
        query = visualization.get("query") or {}
        query_id = query.get("id")
        if query_id is not None:
            query_ids.add(str(query_id))
    return query_ids


def _strip_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_secrets(item)
            for key, item in sorted(value.items())
            if key.lower() not in SECRET_KEYS
        }
    if isinstance(value, list):
        return [_strip_secrets(item) for item in value]
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
