"""Semantic regression tests for research-oriented export formats."""

import json

import pytest

from src.application.services.export_formats import (
    AnnotatedDocument,
    AnnotatedSentence,
    AnnotatedToken,
    ConfidenceScorer,
    DatasetSplitter,
)


def make_document(index: int, label: str = "neutral") -> AnnotatedDocument:
    token = AnnotatedToken(
        text="Ninasoma",
        pos="VERB",
        ner="O",
        morphology={"Root": "som", "FinalVowel": "a"},
        sentence_id=1,
        token_id=1,
    )
    sentence = AnnotatedSentence(tokens=[token], sentence_id=1, sentiment=label)
    return AnnotatedDocument(
        url=f"seed://document/{index}",
        title=f"Document {index}",
        content="Ninasoma.",
        sentences=[sentence],
        sentiment={"label": label, "polarity": 0.0, "confidence": 0.5},
        entities=[],
        keywords=[{"word": "ninasoma", "count": 1}],
        topics=[{"category": "education", "confidence": 0.8}],
        metadata={"id": str(index)},
    )


def test_conll_has_ten_columns_and_morphological_features():
    output = make_document(1).to_conll()
    token_line = next(line for line in output.splitlines() if line.startswith("1\t"))

    assert len(token_line.split("\t")) == 10
    assert "Root=som" in token_line
    assert "FinalVowel=a" in token_line


def test_bio_and_tsv_preserve_token_annotations():
    document = make_document(1)

    assert "Ninasoma\tVERB\tO" in document.to_bio()
    assert "Ninasoma\tVERB\tO\tneutral" in document.to_tsv()


def test_json_ld_and_research_json_are_structured():
    document = make_document(1)

    json_ld = document.to_json_ld()
    research = document.to_research_json(include_confidence=False)

    assert json_ld["@type"] == "NewsArticle"
    assert json_ld["inLanguage"] == "sw"
    assert research["document_id"] == "1"
    assert "confidence" not in research["sentiment"]


def test_document_without_metadata_uses_safe_defaults():
    document = make_document(1)
    document.metadata = None
    document.__post_init__()

    assert document.to_research_json()["document_id"] == "unknown"


def test_dataset_split_is_reproducible_and_complete():
    documents = [
        make_document(i, "positive" if i % 2 else "neutral") for i in range(20)
    ]

    first = DatasetSplitter.split_dataset(documents, random_seed=17)
    second = DatasetSplitter.split_dataset(documents, random_seed=17)

    assert [[doc.url for doc in split] for split in first] == [
        [doc.url for doc in split] for split in second
    ]
    assert sum(len(split) for split in first) == len(documents)
    assert set().union(*(set(doc.url for doc in split) for split in first)) == {
        doc.url for doc in documents
    }


def test_dataset_split_rejects_invalid_ratios():
    with pytest.raises(ValueError, match="sum to 1.0"):
        DatasetSplitter.split_dataset(
            [], train_ratio=0.8, dev_ratio=0.2, test_ratio=0.2
        )


def test_export_splits_writes_parseable_json_and_metadata(tmp_path):
    paths = DatasetSplitter.export_splits(
        [make_document(i) for i in range(10)],
        tmp_path,
        format="json",
        stratify_by=None,
    )

    assert set(paths) == {"train", "dev", "test", "metadata"}
    metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))
    assert metadata["total_documents"] == 10
    assert metadata["train_size"] + metadata["dev_size"] + metadata["test_size"] == 10


def test_confidence_scorer_handles_empty_entity_text():
    assert ConfidenceScorer.calculate_ner_confidence("", "") == 0.5
