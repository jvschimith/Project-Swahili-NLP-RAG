"""
Data Augmentation - Morphological Augmenter (Phase 3)

Data augmentation for low-resource Swahili NLP.
Uses morphological rules to generate realistic variants.

Critical for low-resource scenarios:
- Expand small datasets 10-100x
- Create balanced datasets
- Improve model robustness
"""
from typing import List, Dict, Set, Tuple, Optional
import random

from ...domain.services.root_extractor_enhanced import (
    EnhancedRootExtractor,
    ParadigmGenerator,
    VerbComponents
)


class MorphologicalAugmenter:
    """
    Data augmentation using morphological transformations.
    
    Techniques:
    1. Tense variants (present → past → future)
    2. Person variants (I → you → he/she)
    3. Singular ↔ plural conversion
    4. Syllable-level perturbations
    """
    
    @classmethod
    def augment_with_tense_variants(
        cls,
        sentences: List[str],
        max_variants_per_sentence: int = 5
    ) -> List[str]:
        """
        Generate tense variants for sentences.
        
        Finds verbs in sentences and generates variants with different tenses.
        
        Args:
            sentences: Original sentences
            max_variants_per_sentence: Maximum variants to generate
            
        Returns:
            Augmented sentence list
            
        Example:
            Input: ["Ninasoma kitabu"]
            Output: [
                "Ninasoma kitabu",  # original
                "Nilisoma kitabu",  # past
                "Nitasoma kitabu",  # future
                "Nimesoma kitabu",  # perfect
            ]
        """
        augmented = list(sentences)  # Keep originals
        
        for sentence in sentences:
            words = sentence.split()
            
            # Find verbs in sentence
            for i, word in enumerate(words):
                components = EnhancedRootExtractor.extract_verb_components(word)
                
                if components.root and components.tense:
                    # Generate tense variants
                    tense_variants = cls._generate_tense_variants(
                        components,
                        max_variants=max_variants_per_sentence
                    )
                    
                    # Create new sentences with each variant
                    for new_verb in tense_variants:
                        new_sentence = words.copy()
                        new_sentence[i] = new_verb
                        augmented.append(' '.join(new_sentence))
        
        return augmented
    
    @classmethod
    def _generate_tense_variants(
        cls,
        components: VerbComponents,
        max_variants: int = 5
    ) -> List[str]:
        """Generate verb forms with different tenses."""
        variants = []
        
        tenses = ['na', 'li', 'ta', 'me', 'hu']  # present, past, future, perfect, habitual
        
        for tense in tenses[:max_variants]:
            if tense != components.tense:  # Skip original tense
                # Reconstruct verb with new tense
                parts = []
                if components.subject:
                    parts.append(components.subject)
                parts.append(tense)
                if components.object:
                    parts.append(components.object)
                parts.append(components.root)
                parts.append(components.final or 'a')
                
                variants.append(''.join(parts))
        
        return variants
    
    @classmethod
    def augment_with_person_variants(
        cls,
        sentences: List[str],
        max_variants_per_sentence: int = 3
    ) -> List[str]:
        """
        Generate person variants (I → you → he/she).
        
        Example:
            Input: ["Ninasoma"]
            Output: ["Ninasoma", "Unasoma", "Anasoma"]
        """
        augmented = list(sentences)
        
        subjects = ['ni', 'u', 'a', 'tu', 'm', 'wa']
        
        for sentence in sentences:
            words = sentence.split()
            
            for i, word in enumerate(words):
                components = EnhancedRootExtractor.extract_verb_components(word)
                
                if components.root and components.subject:
                    # Generate person variants
                    for new_subject in subjects[:max_variants_per_sentence]:
                        if new_subject != components.subject:
                            # Reconstruct with new subject
                            parts = [new_subject]
                            if components.tense:
                                parts.append(components.tense)
                            if components.object:
                                parts.append(components.object)
                            parts.append(components.root)
                            parts.append(components.final or 'a')
                            
                            new_verb = ''.join(parts)
                            new_sentence = words.copy()
                            new_sentence[i] = new_verb
                            augmented.append(' '.join(new_sentence))
        
        return augmented
    
    @classmethod
    def augment_with_noun_class(
        cls,
        nouns: List[str],
        include_reverse: bool = True
    ) -> List[str]:
        """
        Generate singular/plural pairs for nouns.
        
        Args:
            nouns: List of nouns
            include_reverse: Include both directions (sg→pl and pl→sg)
            
        Returns:
            Augmented noun list
            
        Example:
            Input: ["mtu", "mtoto"]
            Output: ["mtu", "watu", "mtoto", "watoto"]
        """
        augmented = list(nouns)
        
        # Noun class mappings (singular → plural)
        mappings = {
            'm': 'wa',    # mtu → watu (people)
            'ki': 'vi',   # kitabu → vitabu (things)
            'ji': 'ma',   # jicho → macho (pairs/augmentatives)
            'u': 'ny',    # uso → nyuso (abstractions)
            # Class 9/10 often doesn't change
        }
        
        for noun in nouns:
            # Try singular → plural
            for sg_prefix, pl_prefix in mappings.items():
                if noun.startswith(sg_prefix):
                    plural = noun.replace(sg_prefix, pl_prefix, 1)
                    augmented.append(plural)
                    break
            
            # Try plural → singular (reverse)
            if include_reverse:
                for sg_prefix, pl_prefix in mappings.items():
                    if noun.startswith(pl_prefix):
                        singular = noun.replace(pl_prefix, sg_prefix, 1)
                        augmented.append(singular)
                        break
        
        return list(set(augmented))  # Remove duplicates
    
    @classmethod
    def augment_with_object_markers(
        cls,
        sentences: List[str],
        probability: float = 0.5
    ) -> List[str]:
        """
        Add or remove object markers from verbs.
        
        Example:
            "Ninasoma kitabu" → "Ninakisoma" (I read it)
        """
        augmented = list(sentences)
        
        object_markers = ['ni', 'ku', 'm', 'ki', 'tu', 'wa']
        
        for sentence in sentences:
            words = sentence.split()
            
            for i, word in enumerate(words):
                components = EnhancedRootExtractor.extract_verb_components(word)
                
                if components.root and random.random() < probability:
                    # Add object if not present
                    if not components.object:
                        obj_marker = random.choice(object_markers)
                        parts = []
                        if components.subject:
                            parts.append(components.subject)
                        if components.tense:
                            parts.append(components.tense)
                        parts.append(obj_marker)
                        parts.append(components.root)
                        parts.append(components.final or 'a')
                        
                        new_verb = ''.join(parts)
                        new_sentence = words.copy()
                        new_sentence[i] = new_verb
                        augmented.append(' '.join(new_sentence))
        
        return augmented
    
    @classmethod
    def create_balanced_dataset(
        cls,
        data: Dict[str, List[str]],
        target_size_per_class: int = 500
    ) -> Dict[str, List[str]]:
        """
        Create balanced dataset through augmentation.
        
        Args:
            data: Dictionary mapping class -> examples
            target_size_per_class: Target number of examples per class
            
        Returns:
            Balanced dataset
            
        Example:
            Input: {
                "positive": ["Nzuri sana"] * 100,
                "negative": ["Mbaya"] * 30
            }
            Output: {
                "positive": [...] * 500,  # augmented
                "negative": [...] * 500   # heavily augmented
            }
        """
        balanced = {}
        
        for label, examples in data.items():
            current_size = len(examples)
            
            if current_size >= target_size_per_class:
                # Already enough, just sample
                balanced[label] = random.sample(examples, target_size_per_class)
            else:
                # Need augmentation
                augmented = examples.copy()
                
                while len(augmented) < target_size_per_class:
                    # Apply augmentations
                    augmented = cls.augment_with_tense_variants(augmented, max_variants_per_sentence=3)
                    augmented = cls.augment_with_person_variants(augmented, max_variants_per_sentence=2)
                    
                    # Remove duplicates
                    augmented = list(set(augmented))
                
                # Sample to exact target size
                balanced[label] = random.sample(augmented, target_size_per_class)
        
        return balanced


class SyntheticDataGenerator:
    """
    Generate synthetic training data using morphological rules.
    
    Useful when you have VERY few examples (<50).
    """
    
    # Common verb roots
    COMMON_VERB_ROOTS = [
        "som", "end", "pend", "nyw", "l", "andik", "uliz", "semna",
        "fany", "chukuon", "pig", "sikiangali", "fik", "kaa"
    ]
    
    # Common noun roots
    COMMON_NOUN_ROOTS = [
        "tu", "toto", "ti", "tumatabu", "lazi", "menya",
        "bia", "mbagazeti"
    ]
    
    @classmethod
    def generate_verb_examples(
        cls,
        num_examples: int = 100,
        include_objects: bool = False
    ) -> List[str]:
        """
        Generate synthetic verb examples.
        
        Useful for bootstrapping a dataset from scratch.
        """
        examples = []
        
        for _ in range(num_examples):
            root = random.choice(cls.COMMON_VERB_ROOTS)
            all_forms = ParadigmGenerator.generate_all_forms(
                root,
                include_objects=include_objects
            )
            
            # Flatten and sample
            for forms in all_forms.values():
                examples.extend(random.sample(forms, min(2, len(forms))))
        
        return list(set(examples))[:num_examples]
    
    @classmethod
    def generate_noun_examples(
        cls,
        num_examples: int = 100
    ) -> List[str]:
        """Generate synthetic noun examples."""
        examples = []
        
        prefixes = ['m', 'wa', 'ki', 'vi', 'ma', 'u', 'n', 'ny']
        
        for _ in range(num_examples):
            root = random.choice(cls.COMMON_NOUN_ROOTS)
            prefix = random.choice(prefixes)
            examples.append(f"{prefix}{root}")
        
        return list(set(examples))[:num_examples]


# ==================== USAGE EXAMPLE ====================

def augment_swahili_dataset(
    train_data: Dict[str, List[str]],
    target_size: int = 500
) -> Dict[str, List[str]]:
    """
    Complete augmentation pipeline.
    
    Args:
        train_data: Original training data
        target_size: Target examples per class
        
    Returns:
        Augmented balanced dataset
    """
    augmenter = MorphologicalAugmenter()
    
    # Balance classes
    balanced = augmenter.create_balanced_dataset(
        train_data,
        target_size_per_class=target_size
    )
    
    return balanced
