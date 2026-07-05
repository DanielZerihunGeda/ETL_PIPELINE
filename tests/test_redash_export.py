import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from etl_pipeline.redash_export import RedashExportConfig, export_redash_assets


def test_exports_dashboard_and_related_queries_without_secrets(tmp_path) -> None:
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            requests.append((self.path, self.headers.get("Authorization")))
            if self.path == "/api/dashboards/42":
                body = {
                    "id": 42,
                    "name": "Traffic",
                    "api_key": "dashboard-secret",
                    "widgets": [
                        {"visualization": {"query": {"id": 7}}},
                    ],
                }
            elif self.path == "/api/queries/7":
                body = {
                    "id": 7,
                    "name": "Runs",
                    "query": "select * from mart.fct_trajectory_runs",
                    "api_key": "query-secret",
                }
            else:
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))

        def log_message(self, format, *args):  # noqa: A002
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        export_redash_assets(
            RedashExportConfig(
                base_url=f"http://127.0.0.1:{server.server_port}",
                api_key="token",
                dashboard_ids=["42"],
                output_dir=tmp_path,
            )
        )
    finally:
        server.shutdown()
        thread.join()

    dashboard = (tmp_path / "dashboards/42.json").read_text()
    query = (tmp_path / "queries/7.json").read_text()
    manifest = json.loads((tmp_path / "manifest.json").read_text())

    assert ("Key token") in {authorization for _, authorization in requests}
    assert "dashboard-secret" not in dashboard
    assert "query-secret" not in query
    assert manifest == {"dashboards": ["42"], "queries": ["7"]}
