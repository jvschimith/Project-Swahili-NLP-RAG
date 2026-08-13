"""Small static-first corpus ingestion CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.application.services.url_analyzer import URLNewsAnalyzer

from .pipeline import AcquisitionPipeline
from .storage import CorpusStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire one public Swahili HTML document")
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("data/corpus"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    html = URLNewsAnalyzer().fetch_url(args.url)
    if html is None:
        parser.error("page could not be fetched under the public URL policy")
    pipeline = AcquisitionPipeline(CorpusStore(args.output))
    result = pipeline.process_html(args.url, html, persist=not args.dry_run)
    print(
        json.dumps(
            {
                "status": result.status,
                "duplicate_reason": result.duplicate_reason,
                "storage_path": result.storage_path,
                "document": result.document.to_dict() if result.document else None,
                "metrics": dict(pipeline.metrics),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if result.document else 2


if __name__ == "__main__":
    raise SystemExit(main())
