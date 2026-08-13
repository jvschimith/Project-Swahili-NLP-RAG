"""Path-safe JSON document storage and a compact JSONL corpus manifest."""

from __future__ import annotations

import json
from pathlib import Path

from .models import IngestionResult, WebDocument


class CorpusStore:
    """Store immutable content-addressed documents with exact deduplication."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.documents_dir = self.root / "documents"
        self.manifest_path = self.root / "manifest.jsonl"

    def save(self, document: WebDocument) -> IngestionResult:
        records = self.list_manifest()
        if any(record["canonical_url"] == document.canonical_url for record in records):
            return IngestionResult("duplicate", document, "canonical_url")
        if any(record["content_hash"] == document.content_hash for record in records):
            return IngestionResult("duplicate", document, "content_hash")

        self.documents_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{document.document_id}.json"
        path = (self.documents_dir / filename).resolve()
        if self.documents_dir.resolve() not in path.parents:
            raise ValueError("Document storage path escaped corpus root")
        path.write_text(
            json.dumps(document.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        record = {
            "document_id": document.document_id,
            "canonical_url": document.canonical_url,
            "domain": document.source_domain,
            "title": document.title,
            "published_at": document.published_at,
            "retrieved_at": document.retrieved_at,
            "language": document.language,
            "content_hash": document.content_hash,
            "extraction_method": document.extraction_method,
            "storage_path": f"documents/{filename}",
        }
        with self.manifest_path.open("a", encoding="utf-8") as manifest:
            manifest.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        return IngestionResult("stored", document, storage_path=str(path))

    def list_manifest(self) -> list[dict[str, object]]:
        if not self.manifest_path.exists():
            return []
        records = []
        for line in self.manifest_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return records
