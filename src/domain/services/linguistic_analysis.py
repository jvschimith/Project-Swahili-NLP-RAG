"""
Domain Service: Linguistic Analysis

Turns a single Swahili word into lexeme-first domain entities using the
existing morphology services.
"""
from dataclasses import dataclass
from typing import Optional

from ..entities import Lexeme, WordForm
from ..linguistic_rules import (
    infer_canonical_verb_lemma,
    infer_nominal_lemma,
    looks_like_verb_form,
)
from ..services.bantu_classifier import BantuClassifierService
from ..services.root_extractor import RootExtractorService
from ..value_objects import MorphologicalRoot, VerbComponents, WordType


@dataclass(frozen=True)
class LinguisticAnalysisResult:
    """
    Structured result of analyzing a single Swahili word.

    The service always returns a populated WordForm and a minimal Lexeme
    containing that form.
    """
    word_form: WordForm
    lexeme: Lexeme


class LinguisticAnalysisService:
    """
    Domain service that builds lexeme-first objects from one surface form.
    """

    def __init__(
        self,
        root_service: Optional[RootExtractorService] = None,
        bantu_service: Optional[BantuClassifierService] = None,
    ):
        self.root_service = root_service or RootExtractorService()
        self.bantu_service = bantu_service or BantuClassifierService()

    def analyze_word(self, word: str) -> LinguisticAnalysisResult:
        """
        Analyze a single Swahili word into structured domain objects.
        """
        normalized_word = self._normalize_word(word)
        word_type = self._infer_word_type(normalized_word)
        root = self.root_service.extract(normalized_word, word_type=word_type)
        verb_components = self._extract_verb_components(normalized_word, word_type)
        lexeme_lemma = self._infer_lexeme_lemma(
            normalized_word=normalized_word,
            word_type=word_type,
            root=root,
            verb_components=verb_components,
        )

        word_form = self._build_word_form(
            normalized_word=normalized_word,
            lexeme_lemma=lexeme_lemma,
            word_type=word_type,
            root=root,
            verb_components=verb_components,
        )
        lexeme = self._build_lexeme(lexeme_lemma, word_type, word_form)
        return LinguisticAnalysisResult(word_form=word_form, lexeme=lexeme)

    @staticmethod
    def _normalize_word(word: str) -> str:
        """Normalize the input surface form safely."""
        return word.strip().lower()

    def _infer_word_type(self, normalized_word: str) -> WordType:
        """
        Infer a conservative lexical type from existing morphology clues.

        Preference:
        1. Known Bantu noun-class evidence
        2. Verb morphology evidence
        3. Safe fallback to UNKNOWN
        """
        inferred_noun_class = self.bantu_service.infer_class(normalized_word, WordType.NOUN)
        if inferred_noun_class.is_identified:
            return WordType.NOUN

        if self._looks_like_verb(normalized_word):
            return WordType.VERB

        return WordType.UNKNOWN

    def _looks_like_verb(self, normalized_word: str) -> bool:
        """Use the current morphology engine to detect likely verbs."""
        verb_components = self.root_service.extract_verb_components(normalized_word)
        return looks_like_verb_form(
            normalized_word=normalized_word,
            subject_marker=verb_components.subject_marker,
            tense_marker=verb_components.tense_marker,
            object_marker=verb_components.object_marker,
            final_vowel=verb_components.final_vowel,
        )

    def _extract_verb_components(
        self,
        normalized_word: str,
        word_type: WordType,
    ) -> Optional[VerbComponents]:
        """Only attach explicit verbal morphology when the word looks verbal."""
        if word_type != WordType.VERB:
            return None
        return self.root_service.extract_verb_components(normalized_word)

    def _infer_lexeme_lemma(
        self,
        normalized_word: str,
        word_type: WordType,
        root: MorphologicalRoot,
        verb_components: Optional[VerbComponents],
    ) -> str:
        """
        Infer a stable lexeme lemma from the analysis.

        For verbs, prefer an infinitive/canonical representation built
        from the extracted root and final vowel when that information is
        available. Otherwise, fall back to the normalized surface form.
        """
        if word_type == WordType.VERB:
            canonical = self._build_canonical_verb_lemma(verb_components, root)
            if canonical:
                return canonical
        elif word_type == WordType.NOUN:
            return infer_nominal_lemma(normalized_word)

        return normalized_word

    @staticmethod
    def _build_canonical_verb_lemma(
        verb_components: Optional[VerbComponents],
        root: MorphologicalRoot,
    ) -> Optional[str]:
        """Construct a conservative infinitive-style lemma for verbs."""
        root_text = None
        final_vowel = None

        if verb_components and verb_components.root:
            root_text = verb_components.root
            final_vowel = verb_components.final_vowel
        elif root and root.root:
            root_text = root.root
            final_vowel = root.suffix

        if not root_text:
            return None

        return infer_canonical_verb_lemma(
            root=root_text,
            final_vowel=final_vowel,
            fallback=root.full_word if root else "",
        )

    def _build_word_form(
        self,
        normalized_word: str,
        lexeme_lemma: str,
        word_type: WordType,
        root: MorphologicalRoot,
        verb_components: Optional[VerbComponents],
    ) -> WordForm:
        """Create a structured word form from morphology analysis."""
        suffixes_extensions = []
        if verb_components is not None:
            suffixes_extensions = list(verb_components.suffixes_extensions)
        elif root.suffix:
            suffixes_extensions = [root.suffix]

        return WordForm(
            lexeme_lemma=lexeme_lemma,
            form=normalized_word,
            word_type=word_type,
            root=root,
            verb_components=verb_components,
            subject_marker=verb_components.subject_marker if verb_components else None,
            tense_marker=verb_components.tense_marker if verb_components else None,
            object_marker=verb_components.object_marker if verb_components else None,
            suffixes_extensions=suffixes_extensions,
            final_vowel=verb_components.final_vowel if verb_components else root.suffix,
            polarity=verb_components.polarity if verb_components else None,
            is_canonical=(lexeme_lemma == normalized_word),
        )

    def _build_lexeme(
        self,
        lexeme_lemma: str,
        word_type: WordType,
        word_form: WordForm,
    ) -> Lexeme:
        """Create a minimal lexeme and attach the analyzed word form."""
        noun_class = self.bantu_service.infer_class(lexeme_lemma, word_type)
        lexeme_root = word_form.root
        if word_form.verb_components and word_form.verb_components.root:
            lexeme_root = MorphologicalRoot(root=word_form.verb_components.root)

        lexeme = Lexeme(
            lemma=lexeme_lemma,
            word_type=word_type,
            noun_class=noun_class,
            root=lexeme_root,
        )
        lexeme.add_word_form(word_form)
        return lexeme
