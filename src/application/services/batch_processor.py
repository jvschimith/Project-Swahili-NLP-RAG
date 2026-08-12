"""
Application Layer - Batch Processing

Process multiple URLs in batch with progress tracking.
"""

import json
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from src.application.services.export_formats import (
    AnnotatedDocument,
    AnnotatedSentence,
    AnnotatedToken,
    DatasetSplitter,
)
from src.application.services.url_analyzer import URLNewsAnalyzer


@dataclass
class BatchJob:
    """Batch processing job."""

    job_id: str
    urls: list[str]
    status: str = "pending"  # pending, running, completed, failed
    progress: int = 0  # 0-100
    total_urls: int = field(init=False)
    completed_urls: int = 0
    failed_urls: list[str] = field(default_factory=list)
    results: list[dict[str, Any]] = field(default_factory=list)
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None

    def __post_init__(self):
        self.total_urls = len(self.urls)

    def update_progress(self):
        """Update progress percentage."""
        if self.total_urls > 0:
            self.progress = int((self.completed_urls / self.total_urls) * 100)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status,
            "progress": self.progress,
            "total_urls": self.total_urls,
            "completed_urls": self.completed_urls,
            "failed_urls": self.failed_urls,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }


class BatchProcessor:
    """Process multiple URLs in batch."""

    def __init__(
        self,
        max_workers: int = 5,
        timeout: int = 30,
        delay_between_requests: float = 1.0,
    ):
        """
        Initialize batch processor.

        Args:
            max_workers: Maximum concurrent workers
            timeout: Timeout per URL in seconds
            delay_between_requests: Delay between requests (rate limiting)
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.delay = delay_between_requests
        self.analyzer = URLNewsAnalyzer()
        self.jobs: dict[str, BatchJob] = {}

    def create_job(self, urls: list[str]) -> str:
        """
        Create a new batch job.

        Args:
            urls: List of URLs to process

        Returns:
            Job ID
        """
        job_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(self.jobs)}"
        job = BatchJob(job_id=job_id, urls=urls)
        self.jobs[job_id] = job

        logger.info(f"Created batch job {job_id} with {len(urls)} URLs")

        return job_id

    def get_job_status(self, job_id: str) -> dict[str, Any] | None:
        """Get job status."""
        job = self.jobs.get(job_id)
        return job.to_dict() if job else None

    def process_batch(
        self, job_id: str, progress_callback: Callable[[int], None] | None = None
    ) -> BatchJob:
        """
        Process batch job.

        Args:
            job_id: Job ID
            progress_callback: Optional callback for progress updates

        Returns:
            Completed BatchJob
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = "running"
        job.started_at = datetime.utcnow().isoformat()

        logger.info(f"Starting batch job {job_id}")

        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all URLs
                future_to_url = {
                    executor.submit(self._process_single_url, url): url
                    for url in job.urls
                }

                # Process results as they complete
                for future in as_completed(future_to_url):
                    url = future_to_url[future]

                    try:
                        result = future.result(timeout=self.timeout)
                        job.results.append(result)
                        job.completed_urls += 1

                        logger.info(
                            f"Completed {url} ({job.completed_urls}/{job.total_urls})"
                        )

                    except Exception as e:
                        logger.error(f"Failed to process {url}: {e}")
                        job.failed_urls.append(url)
                        job.completed_urls += 1

                    # Update progress
                    job.update_progress()

                    if progress_callback:
                        progress_callback(job.progress)

                    # Rate limiting
                    time.sleep(self.delay)

            job.status = "completed"
            job.completed_at = datetime.utcnow().isoformat()

            logger.info(
                f"Batch job {job_id} completed: {len(job.results)} succeeded, {len(job.failed_urls)} failed"
            )

        except Exception as e:
            logger.error(f"Batch job {job_id} failed: {e}")
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.utcnow().isoformat()

        return job

    def _process_single_url(self, url: str) -> dict[str, Any]:
        """
        Process a single URL.

        Args:
            url: URL to analyze

        Returns:
            Analysis result
        """
        result = self.analyzer.analyze_url(url)

        # Add metadata
        result["processed_at"] = datetime.utcnow().isoformat()
        result["url"] = url

        return result

    def export_results(
        self,
        job_id: str,
        output_dir: Path,
        format: str = "json",
        create_splits: bool = True,
        **split_kwargs,
    ) -> dict[str, Path]:
        """
        Export batch results.

        Args:
            job_id: Job ID
            output_dir: Output directory
            format: Export format ('json', 'conll', 'bio', 'tsv')
            create_splits: Create train/dev/test splits
            **split_kwargs: Arguments for dataset splitting

        Returns:
            Dictionary of output file paths
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        if job.status != "completed":
            raise ValueError(f"Job {job_id} is not completed (status: {job.status})")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert results to AnnotatedDocuments
        documents = []
        for i, result in enumerate(job.results):
            if result.get("success"):
                doc = self._result_to_document(result, doc_id=f"{job_id}_{i}")
                documents.append(doc)

        logger.info(f"Exporting {len(documents)} documents from job {job_id}")

        file_paths = {}

        if create_splits:
            # Export with splits
            file_paths = DatasetSplitter.export_splits(
                documents, output_dir, format=format, **split_kwargs
            )
        else:
            # Export as single file
            if format == "json":
                file_path = output_dir / f"{job_id}.json"
                data = [doc.to_research_json() for doc in documents]
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                file_paths["all"] = file_path

            elif format == "conll":
                file_path = output_dir / f"{job_id}.conll"
                with open(file_path, "w", encoding="utf-8") as f:
                    for doc in documents:
                        f.write(doc.to_conll())
                        f.write("\n\n")
                file_paths["all"] = file_path

            # Add other formats...

        # Export job metadata
        job_meta_path = output_dir / f"{job_id}_job_info.json"
        with open(job_meta_path, "w", encoding="utf-8") as f:
            json.dump(job.to_dict(), f, indent=2)

        file_paths["job_metadata"] = job_meta_path

        logger.info(f"Exported results to {output_dir}")

        return file_paths

    def _result_to_document(
        self, result: dict[str, Any], doc_id: str
    ) -> AnnotatedDocument:
        """
        Convert analysis result to AnnotatedDocument.

        Args:
            result: Analysis result from URL analyzer
            doc_id: Document ID

        Returns:
            AnnotatedDocument instance
        """
        # Create sentences with tokens
        sentences = []
        text = result.get("full_text", result.get("text_preview", ""))

        # Simple tokenization (improve with actual tokenizer)
        for i, sent_text in enumerate(text.split(".")):
            if not sent_text.strip():
                continue

            tokens = []
            for j, token_text in enumerate(sent_text.split()):
                token = AnnotatedToken(text=token_text, sentence_id=i, token_id=j + 1)
                tokens.append(token)

            sentence = AnnotatedSentence(
                tokens=tokens,
                sentence_id=i,
                sentiment=result.get("sentiment", {}).get("label"),
            )
            sentences.append(sentence)

        # Create document
        doc = AnnotatedDocument(
            url=result.get("url", ""),
            title=result.get("title", "Unknown"),
            content=text,
            sentences=sentences,
            sentiment=result.get("sentiment", {}),
            entities=result.get("entities", []),
            keywords=result.get("top_keywords", []),
            topics=result.get("topics", []),
            translation=result.get("translation"),
            metadata={
                "id": doc_id,
                "word_count": result.get("word_count"),
                "lexical_diversity": result.get("vocabulary_richness"),
                "analyzed_at": result.get("processed_at"),
            },
        )

        return doc


class ProgressTracker:
    """Track and report batch processing progress."""

    def __init__(self):
        self.callbacks: list[Callable[[dict[str, Any]], None]] = []

    def add_callback(self, callback: Callable[[dict[str, Any]], None]):
        """Add progress callback."""
        self.callbacks.append(callback)

    def report_progress(
        self,
        job_id: str,
        progress: int,
        completed: int,
        total: int,
        current_url: str | None = None,
    ):
        """Report progress update."""
        update = {
            "job_id": job_id,
            "progress": progress,
            "completed": completed,
            "total": total,
            "current_url": current_url,
            "timestamp": datetime.utcnow().isoformat(),
        }

        for callback in self.callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
