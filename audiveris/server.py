"""Minimal HTTP server that wraps Audiveris CLI for headless OMR processing."""

import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def _find_musicxml_member(mxl_path: Path) -> str:
    """Return the MusicXML member path inside an MXL archive."""
    with zipfile.ZipFile(mxl_path) as archive:
        names = archive.namelist()

        if "META-INF/container.xml" in names:
            container = archive.read("META-INF/container.xml")
            root = ET.fromstring(container)
            namespace = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
            rootfile = root.find(".//c:rootfile", namespace)
            if rootfile is not None:
                full_path = rootfile.attrib.get("full-path", "")
                if full_path and full_path in names:
                    return full_path

        fallback = [name for name in names if not name.startswith("META-INF/") and name.lower().endswith((".xml", ".musicxml"))]
        if fallback:
            return fallback[0]

    raise ValueError(f"No MusicXML member found in archive: {mxl_path}")


def _extract_musicxml(mxl_path: Path, dest_path: Path) -> None:
    """Extract MusicXML payload from .mxl archive into an uncompressed file."""
    member_path = _find_musicxml_member(mxl_path)
    with zipfile.ZipFile(mxl_path) as archive:
        xml_data = archive.read(member_path)
    dest_path.write_bytes(xml_data)


class AudiverisHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            if self.path != "/process":
                self.send_error(404)
                return

            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_error(400, "Empty request body")
                return

            body = json.loads(self.rfile.read(content_length))
            input_path = body.get("input_path")
            output_dir = body.get("output_dir")

            if not input_path or not output_dir:
                self._json_response(400, {"error": "input_path and output_dir are required"})
                return

            input_file = Path(input_path)
            if not input_file.exists():
                self._json_response(400, {"error": f"Input file not found: {input_path}"})
                return

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Audiveris outputs to a book-named subfolder, so use a temp dir then move.
            with tempfile.TemporaryDirectory() as tmp_dir:
                cmd = [
                    "Audiveris",
                    "-batch",
                    "-transcribe",
                    "-export",
                    "-output",
                    tmp_dir,
                    "--",
                    str(input_file),
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                if result.stdout:
                    print(f"Audiveris stdout:\n{result.stdout[-4000:]}")
                if result.stderr:
                    print(f"Audiveris stderr:\n{result.stderr[-4000:]}")

                if result.returncode != 0:
                    self._json_response(
                        500,
                        {
                            "error": "Audiveris processing failed",
                            "stderr": result.stderr[-2000:] if result.stderr else "",
                            "stdout": result.stdout[-2000:] if result.stdout else "",
                        },
                    )
                    return

                # Find the generated .mxl file.
                mxl_files = list(Path(tmp_dir).rglob("*.mxl"))
                if not mxl_files:
                    self._json_response(
                        500,
                        {
                            "error": "No MusicXML output generated",
                            "stderr": result.stderr[-2000:] if result.stderr else "",
                        },
                    )
                    return

                # Extract uncompressed MusicXML for browser-side Verovio rendering.
                src_mxl = mxl_files[0]
                dest_name = f"{input_file.stem}.musicxml"
                dest_path = output_path / dest_name
                _extract_musicxml(src_mxl, dest_path)

            self._json_response(200, {"output_path": str(dest_path)})
        except Exception as exc:
            print(f"Unhandled server error: {exc}")
            self._json_response(500, {"error": f"Internal Audiveris server error: {exc}"})

    def do_GET(self):
        if self.path == "/health":
            self._json_response(200, {"status": "ok"})
            return
        self.send_error(404)

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 7070), AudiverisHandler)
    print("Audiveris server listening on port 7070")
    server.serve_forever()
