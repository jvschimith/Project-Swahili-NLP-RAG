"""
Domain Services - Enhanced Root Extractor (v2.1)

Phase 1 & 2 Enhancements:
- Paradigm generation for data augmentation
- Improved verb component extraction
- Complex prefix chain support
"""
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from ..value_objects_enhanced import VerbTense, SwahiliTenses


@dataclass
class VerbComponents:
    """Extracted components of a Swahili verb."""
    subject: Optional[str] = None
    tense: Optional[str] = None
    object: Optional[str] = None
    root: Optional[str] = None
    final: Optional[str] = None
    is_negative: bool = False
    tense_info: Optional[VerbTense] = None
    
    def __str__(self) -> str:
        parts = []
        if self.subject:
            parts.append(f"SUBJ:{self.subject}")
        if self.tense:
            parts.append(f"TENSE:{self.tense}")
        if self.object:
            parts.append(f"OBJ:{self.object}")
        if self.root:
            parts.append(f"ROOT:{self.root}")
        if self.final:
            parts.append(f"FINAL:{self.final}")
        return " + ".join(parts) if parts else "NO_ANALYSIS"
    
    def reconstruct(self) -> str:
        """Reconstruct verb from components."""
        parts = []
        if self.subject:
            parts.append(self.subject)
        if self.tense:
            parts.append(self.tense)
        if self.object:
            parts.append(self.object)
        if self.root:
            parts.append(self.root)
        if self.final:
            parts.append(self.final)
        return "".join(parts)


class ParadigmGenerator:
    """
    Generate all verb conjugations from a single root.
    
    Essential for low-resource data augmentation:
    - From 1 example, generate 100+ variants
    - Create balanced training data
    - Cover all person/tense combinations
    """
    
    # Subject markers (person agreement)
    SUBJECT_MARKERS = {
        "1sg": "ni",   # mimi (I)
        "2sg": "u",    # wewe (you-sg)
        "3sg": "a",    # yeye (he/she)
        "1pl": "tu",   # sisi (we)
        "2pl": "m",    # ninyi (you-pl)
        "3pl": "wa",   # wao (they)
    }
    
    # Object markers (for transitive verbs)
    OBJECT_MARKERS = {
        "1sg": "ni",   # me
        "2sg": "ku",   # you
        "3sg_human": "m",    # him/her
        "3sg_thing": "ki",   # it (class 7)
        "1pl": "tu",   # us
        "2pl": "wa",   # you (plural)
        "3pl": "wa",   # them
    }
    
    # Common tense markers (simplified from SwahiliTenses)
    TENSE_MARKERS = {
        "present": "na",
        "past": "li",
        "future": "ta",
        "perfect": "me",
        "habitual": "hu",
        "conditional": "nge",
    }
    
    @classmethod
    def generate_all_forms(
        cls,
        root: str,
        include_objects: bool = False,
        tenses: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Generate all conjugations from a verb root.
        
        Args:
            root: Verb root (e.g., "som" for read)
            include_objects: Include object markers
            tenses: List of tenses to generate (default: all)
            
        Returns:
            Dictionary mapping tense -> list of forms
            
        Examples:
            >>> ParadigmGenerator.generate_all_forms("som")
            {
                "present": ["ninasoma", "unasoma", "anasoma", ...],
                "past": ["nilisoma", "ulisoma", "alisoma", ...],
                ...
            }
        """
        if tenses is None:
            tenses = list(cls.TENSE_MARKERS.keys())
        
        results = {}
        
        for tense_name in tenses:
            if tense_name not in cls.TENSE_MARKERS:
                continue
            
            tense_marker = cls.TENSE_MARKERS[tense_name]
            conjugations = []
            
            # Generate for each subject
            for subj_name, subj_marker in cls.SUBJECT_MARKERS.items():
                # Basic form: subject + tense + root + final vowel
                if tense_name == "habitual":
                    # Habitual doesn't use subject prefix
                    form = f"{tense_marker}{root}a"
                else:
                    form = f"{subj_marker}{tense_marker}{root}a"
                
                conjugations.append(form)
                
                # Add object markers if requested
                if include_objects:
                    for obj_name, obj_marker in cls.OBJECT_MARKERS.items():
                        if tense_name == "habitual":
                            obj_form = f"{tense_marker}{obj_marker}{root}a"
                        else:
                            obj_form = f"{subj_marker}{tense_marker}{obj_marker}{root}a"
                        conjugations.append(obj_form)
            
            results[tense_name] = conjugations
        
        return results
    
    @classmethod
    def generate_person_paradigm(
        cls,
        root: str,
        tense: str = "present"
    ) -> Dict[str, str]:
        """
        Generate paradigm for all persons in one tense.
        
        Args:
            root: Verb root
            tense: Tense to use
            
        Returns:
            Dictionary mapping person -> conjugated form
            
        Example:
            >>> ParadigmGenerator.generate_person_paradigm("som", "present")
            {
                "1sg": "ninasoma",
                "2sg": "unasoma",
                "3sg": "anasoma",
                ...
            }
        """
        if tense not in cls.TENSE_MARKERS:
            raise ValueError(f"Unknown tense: {tense}")
        
        tense_marker = cls.TENSE_MARKERS[tense]
        paradigm = {}
        
        for person, subj_marker in cls.SUBJECT_MARKERS.items():
            if tense == "habitual":
                form = f"{tense_marker}{root}a"
            else:
                form = f"{subj_marker}{tense_marker}{root}a"
            paradigm[person] = form
        
        return paradigm
    
    @classmethod
    def augment_dataset(
        cls,
        examples: List[str],
        max_per_root: int = 50
    ) -> List[str]:
        """
        Augment limited dataset by generating morphological variants.
        
        Critical for low-resource scenarios:
        - Input: 10 examples
        - Output: 500+ examples (50x augmentation)
        
        Args:
            examples: List of example verb forms
            max_per_root: Maximum forms to generate per root
            
        Returns:
            Augmented list with all derived forms
        """
        augmented = set(examples)  # Keep originals
        
        for example in examples:
            # Extract root from example
            components = EnhancedRootExtractor.extract_verb_components(example)
            
            if components.root:
                # Generate variants for this root
                all_forms = cls.generate_all_forms(components.root)
                
                # Flatten and limit
                for tense_forms in all_forms.values():
                    augmented.update(tense_forms[:max_per_root])
        
        return list(augmented)
    
    @classmethod
    def generate_minimal_pairs(
        cls,
        root: str,
        vary_by: str = "tense"
    ) -> List[Tuple[str, str, str]]:
        """
        Generate minimal pairs for linguistic analysis.
        
        Minimal pairs differ by only one feature (tense, person, etc.)
        Useful for testing model understanding of morphology.
        
        Args:
            root: Verb root
            vary_by: What to vary ("tense", "person", "object")
            
        Returns:
            List of (form1, form2, difference) tuples
            
        Example:
            >>> ParadigmGenerator.generate_minimal_pairs("som", "tense")
            [
                ("ninasoma", "nilisoma", "present->past"),
                ("ninasoma", "nitasoma", "present->future"),
                ...
            ]
        """
        pairs = []
        
        if vary_by == "tense":
            # Fix person (1sg), vary tense
            for tense1, marker1 in cls.TENSE_MARKERS.items():
                for tense2, marker2 in cls.TENSE_MARKERS.items():
                    if tense1 != tense2:
                        form1 = f"ni{marker1}{root}a"
                        form2 = f"ni{marker2}{root}a"
                        pairs.append((form1, form2, f"{tense1}->{tense2}"))
        
        elif vary_by == "person":
            # Fix tense (present), vary person
            tense_marker = cls.TENSE_MARKERS["present"]
            for person1, subj1 in cls.SUBJECT_MARKERS.items():
                for person2, subj2 in cls.SUBJECT_MARKERS.items():
                    if person1 != person2:
                        form1 = f"{subj1}{tense_marker}{root}a"
                        form2 = f"{subj2}{tense_marker}{root}a"
                        pairs.append((form1, form2, f"{person1}->{person2}"))
        
        elif vary_by == "object":
            # Fix person and tense, add/remove object
            subj = "ni"
            tense = "na"
            base_form = f"{subj}{tense}{root}a"
            
            for obj_name, obj_marker in cls.OBJECT_MARKERS.items():
                obj_form = f"{subj}{tense}{obj_marker}{root}a"
                pairs.append((base_form, obj_form, f"no_obj->obj_{obj_name}"))
        
        return pairs


class EnhancedRootExtractor:
    """
    Enhanced morphological analysis for Swahili verbs.
    
    Improvements over basic version:
    - Complex prefix chain support (subj + tense + obj)
    - Negative form detection
    - Tense identification with metadata
    - Irregular verb handling
    """
    
    # Subject agreement prefixes (ordered by length - longest first)
    SUBJECT_PREFIXES = ["ni", "u", "a", "tu", "m", "wa"]
    
    # Tense markers
    TENSE_MARKERS = ["na", "li", "ta", "me", "hu", "nge", "ngali", "ku"]
    
    # Object markers
    OBJECT_MARKERS = ["ni", "ku", "m", "ki", "vi", "tu", "wa", "ya"]
    
    # Common final vowels
    FINAL_VOWELS = ["a", "e", "i", "o", "u"]
    
    # Negative markers
    NEGATIVE_MARKERS = ["ha", "si"]
    
    @classmethod
    def extract_verb_components(
        cls,
        verb: str,
        strict: bool = True
    ) -> VerbComponents:
        """
        Extract all components from a Swahili verb.
        
        Structure: [NEG] + SUBJ + TENSE + [OBJ] + ROOT + FINAL
        
        Args:
            verb: Full verb form
            strict: If True, require all components
            
        Returns:
            VerbComponents with all extracted parts
            
        Examples:
            >>> EnhancedRootExtractor.extract_verb_components("ninasoma")
            VerbComponents(subject='ni', tense='na', root='som', final='a')
            
            >>> EnhancedRootExtractor.extract_verb_components("anakupenda")
            VerbComponents(subject='a', tense='na', object='ku', root='pend', final='a')
        """
        original = verb
        components = VerbComponents()
        remaining = verb.lower()
        
        # Check for negative
        for neg in cls.NEGATIVE_MARKERS:
            if remaining.startswith(neg):
                components.is_negative = True
                remaining = remaining[len(neg):]
                break
        
        # Extract subject prefix
        for subj in cls.SUBJECT_PREFIXES:
            if remaining.startswith(subj):
                components.subject = subj
                remaining = remaining[len(subj):]
                break
        
        # Extract tense marker
        for tense in cls.TENSE_MARKERS:
            if remaining.startswith(tense):
                components.tense = tense
                # Get tense info
                components.tense_info = SwahiliTenses.get_tense_by_marker(tense)
                remaining = remaining[len(tense):]
                break
        
        # Extract object marker (optional)
        for obj in cls.OBJECT_MARKERS:
            if remaining.startswith(obj) and len(remaining) > len(obj) + 2:
                # Make sure there's still room for root + final
                components.object = obj
                remaining = remaining[len(obj):]
                break
        
        # Extract final vowel
        if remaining and remaining[-1] in cls.FINAL_VOWELS:
            components.final = remaining[-1]
            remaining = remaining[:-1]
        
        # What's left is the root
        if remaining:
            components.root = remaining
        
        return components
    
    @classmethod
    def is_valid_verb(cls, verb: str) -> bool:
        """Check if string looks like a valid Swahili verb."""
        components = cls.extract_verb_components(verb, strict=False)
        return (
            components.root is not None and
            len(components.root) >= 2 and
            components.final in cls.FINAL_VOWELS
        )
    
    @classmethod
    def get_infinitive(cls, verb: str) -> Optional[str]:
        """
        Convert conjugated verb to infinitive form.
        
        Args:
            verb: Conjugated verb (e.g., "ninasoma")
            
        Returns:
            Infinitive form (e.g., "kusoma")
            
        Example:
            >>> EnhancedRootExtractor.get_infinitive("ninasoma")
            "kusoma"
        """
        components = cls.extract_verb_components(verb)
        if components.root:
            return f"ku{components.root}{components.final or 'a'}"
        return None
    
    @classmethod
    def analyze_with_paradigm(cls, verb: str) -> Dict[str, any]:
        """
        Full analysis with paradigm generation.
        
        Returns complete morphological analysis plus all related forms.
        """
        components = cls.extract_verb_components(verb)
        
        analysis = {
            "original": verb,
            "components": {
                "subject": components.subject,
                "tense": components.tense,
                "object": components.object,
                "root": components.root,
                "final": components.final,
                "is_negative": components.is_negative
            },
            "tense_info": {
                "name": components.tense_info.name if components.tense_info else None,
                "aspect": components.tense_info.aspect if components.tense_info else None,
                "time": components.tense_info.time_reference if components.tense_info else None
            } if components.tense_info else None,
            "infinitive": cls.get_infinitive(verb),
            "related_forms": {}
        }
        
        # Generate related forms if we have a root
        if components.root:
            # Same root, different tenses
            person_paradigm = ParadigmGenerator.generate_person_paradigm(
                components.root,
                components.tense or "present"
            )
            analysis["related_forms"]["person_paradigm"] = person_paradigm
            
            # Same person, different tenses
            if components.subject:
                tense_variants = {}
                for tense_name, tense_marker in ParadigmGenerator.TENSE_MARKERS.items():
                    tense_variants[tense_name] = f"{components.subject}{tense_marker}{components.root}a"
                analysis["related_forms"]["tense_variants"] = tense_variants
        
        return analysis
