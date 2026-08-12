"""
Stable linguistic rules for the Swahili core domain.

This module is the source of truth for the frozen linguistic contract
used by the domain and morphology services.
"""
from typing import Iterable, Optional


CORE_WORD_TYPE_VALUES = {
    "noun",
    "verb",
    "adjective",
    "adverb",
    "unknown",
}


NOUN_CLASS_DESCRIPTIONS = {
    "1/2": "People and human referents",
    "3/4": "Plants and elongated objects",
    "5/6": "Fruits, paired items, and augmentatives",
    "7/8": "Tools, artifacts, and instrument-like nouns",
    "9/10": "Animals, common objects, and many loanwords",
    "11/14": "Abstract nouns and mass-like concepts",
    "16/17/18": "Locative nouns and spatial reference",
    "N/A": "Unknown noun class",
}


NOUN_CLASS_SPECIAL_CASES = {
    "mtu": "1/2",
    "watu": "1/2",
    "mti": "3/4",
    "miti": "3/4",
    "kiti": "7/8",
    "viti": "7/8",
    "jicho": "5/6",
    "macho": "5/6",
    "nyumba": "9/10",
    "uzuri": "11/14",
    "pahali": "16/17/18",
}


NOUN_CLASS_PREFIX_RULES = {
    ("mtu", "mwa", "mw", "mu"): "1/2",
    ("wa",): "1/2",
    ("mti", "mw"): "3/4",
    ("mi",): "3/4",
    ("ji", "j"): "5/6",
    ("ma",): "5/6",
    ("ki", "ch"): "7/8",
    ("vi", "vy"): "7/8",
    ("n", "ny", "ng", "ndege", "nyumba"): "9/10",
    ("u",): "11/14",
    ("pa", "ku", "mu", "mw"): "16/17/18",
}


NOUN_CLASS_EXAMPLES = {
    "1/2": [
        ("mtu", "watu", "person/people"),
        ("mwalimu", "walimu", "teacher/teachers"),
        ("mwana", "wana", "child/children"),
    ],
    "3/4": [
        ("mti", "miti", "tree/trees"),
        ("mkono", "mikono", "arm or hand/arms or hands"),
        ("mwaka", "miaka", "year/years"),
    ],
    "5/6": [
        ("jicho", "macho", "eye/eyes"),
        ("tunda", "matunda", "fruit/fruits"),
        ("jina", "majina", "name/names"),
    ],
    "7/8": [
        ("kiti", "viti", "chair/chairs"),
        ("kisu", "visu", "knife/knives"),
        ("kitabu", "vitabu", "book/books"),
    ],
    "9/10": [
        ("nyumba", "nyumba", "house/houses"),
        ("ndege", "ndege", "bird/birds"),
        ("ngoma", "ngoma", "drum/drums"),
    ],
    "11/14": [
        ("uzuri", "", "beauty"),
        ("utu", "", "humanity"),
        ("uchungu", "", "bitterness"),
    ],
    "16/17/18": [
        ("pahali", "", "place"),
        ("kule", "", "over there"),
        ("ndani", "", "inside"),
    ],
}


VERB_SUBJECT_MARKERS = {
    "ni": "1sg",
    "u": "2sg",
    "a": "3sg",
    "tu": "1pl",
    "m": "2pl",
    "wa": "3pl",
}


VERB_TENSE_MARKERS = {
    "na": "present",
    "li": "past",
    "ta": "future",
    "me": "perfect",
    "ku": "infinitive",
    "si": "negative",
}


VERB_OBJECT_MARKERS = ["ni", "ku", "mu", "tu", "wa", "m", "ki", "vi"]


VERBAL_PREFIXES = [
    "ninaku", "ninali", "ninata", "ninana", "ninajua",
    "unaku", "unali", "unata", "unana",
    "anaku", "anali", "anata", "anana",
    "tunaku", "tunali", "tunata", "tunana",
    "mnaku", "mnali", "mnata", "mnana",
    "wanaku", "wanali", "wanata", "wanana",
    "nina", "una", "ana", "tuna", "mna", "wana",
    "nita", "uta", "ata", "tuta", "mta", "wata",
    "nili", "uli", "ali", "tuli", "mli", "wali",
    "nime", "ume", "ame", "tume", "mme", "wame",
    "niku", "uku", "aku", "tuku", "mku", "waku",
    "nihu", "uhu", "ahu", "tuhu", "mhu", "wahu",
    "nisi", "usi", "asi", "tusi", "msi", "wasi",
    "ni", "u", "a", "tu", "m", "wa",
    "ku", "li", "ta", "na", "me", "ka", "hu", "si",
]


NOMINAL_PREFIXES = [
    "wa", "mi", "ma", "ki", "vi", "ku", "pa", "mu",
    "mw", "mtu", "mti", "ji", "ny", "n", "u",
]


VERBAL_SUFFIXES = [
    "wa", "ni", "ye", "e", "a", "i", "o", "u",
    "ka", "sha", "po", "ko", "mo",
]


NOMINAL_SUFFIXES = ["ni", "o", "e", "i"]


AFFIRMATIVE_POLARITY = "affirmative"
NEGATIVE_POLARITY = "negative"


def normalize_linguistic_text(text: str) -> str:
    """Normalize a single linguistic token or marker."""
    return text.strip().lower()


def get_noun_class_description(class_value: str) -> str:
    """Return the stable English description for a noun class."""
    return NOUN_CLASS_DESCRIPTIONS.get(class_value, "Unknown noun class")


def get_noun_class_examples(class_value: str) -> list:
    """Return typical example tuples for a noun class."""
    return NOUN_CLASS_EXAMPLES.get(class_value, [])


def infer_verb_polarity(tense_marker: Optional[str]) -> Optional[str]:
    """Infer polarity when verbal morphology exposes it."""
    if tense_marker is None:
        return None
    if tense_marker == "si":
        return NEGATIVE_POLARITY
    return AFFIRMATIVE_POLARITY


def infer_canonical_verb_lemma(
    root: Optional[str],
    final_vowel: Optional[str],
    fallback: str,
) -> str:
    """Infer a conservative infinitive-style canonical verb lemma."""
    if not root:
        return fallback
    if final_vowel:
        return f"ku{root}{final_vowel}"
    return f"ku{root}"


def infer_nominal_lemma(word: str) -> str:
    """Current noun lemma policy: surface form is the safe canonical form."""
    return normalize_linguistic_text(word)


def normalize_suffixes(values: Optional[Iterable[str]]) -> list[str]:
    """Normalize suffix/extension material while preserving order."""
    normalized = []
    for value in values or []:
        if value:
            cleaned = normalize_linguistic_text(value)
            if cleaned:
                normalized.append(cleaned)
    return normalized


def looks_like_verb_form(
    normalized_word: str,
    subject_marker: Optional[str],
    tense_marker: Optional[str],
    object_marker: Optional[str],
    final_vowel: Optional[str],
) -> bool:
    """Centralized heuristic for current verb-form detection."""
    if any([subject_marker, tense_marker, object_marker, final_vowel]):
        return True
    if normalized_word.startswith("ku") and len(normalized_word) > 3:
        return True
    return normalized_word.endswith("a")
