"""Export the OpenAPI schema to a static file.

Usage::

    python scripts/export_openapi.py

Writes `openapi.json` to the project root. Useful for shipping the schema
to external teams or for generating client SDKs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure the project root is importable when run as `python scripts/export_openapi.py`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


def main() -> None:
    schema = app.openapi()
    out = Path(__file__).resolve().parents[1] / "openapi.json"
    out.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OpenAPI schema written to {out}")


if __name__ == "__main__":
    main()
