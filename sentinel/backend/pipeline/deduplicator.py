"""
SENTINEL v2.0 — Entity Deduplicator & Alias Resolver (Auto-Feature 1)
Implements Jaro-Winkler string similarity and prefix weighting to detect
aliases and duplicate suspects (e.g. 'Rajesh @ Chhotu', 'R. Kumar', 'Ramesh K.').
"""

from typing import List, Dict, Any, Tuple
import re

def jaro_distance(s1: str, s2: str) -> float:
    """Computes basic Jaro distance between two strings."""
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    max_dist = (max(len1, len2) // 2) - 1
    match1 = [False] * len1
    match2 = [False] * len2

    matches = 0
    for i in range(len1):
        start = max(0, i - max_dist)
        end = min(i + max_dist + 1, len2)
        for j in range(start, end):
            if not match2[j] and s1[i] == s2[j]:
                match1[i] = True
                match2[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    transpositions = 0
    k = 0
    for i in range(len1):
        if match1[i]:
            while not match2[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

    t = transpositions / 2.0
    return (matches / len1 + matches / len2 + (matches - t) / matches) / 3.0

def jaro_winkler_similarity(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
    """
    Computes Jaro-Winkler similarity with a prefix bonus up to 4 characters.
    Returns float in range [0.0, 1.0].
    """
    j_dist = jaro_distance(s1, s2)
    prefix_len = 0
    for c1, c2 in zip(s1.lower(), s2.lower()):
        if c1 == c2:
            prefix_len += 1
            if prefix_len == 4:
                break
        else:
            break
    return j_dist + (prefix_len * prefix_scale * (1.0 - j_dist))

class EntityDeduplicator:
    """
    Scans candidate entities against an existing entity repository
    to identify duplicates and alias matches (similarity > threshold, default 0.85).
    """
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def normalize_name(self, name: str) -> str:
        # Strip honorifics (Shri, Smt, Late) and aliases (@ Chhotu)
        cleaned = re.sub(r'\b(shri|smt|late|mr|mrs|dr)\b', '', name, flags=re.IGNORECASE)
        # Extract base if @ alias format
        if '@' in cleaned:
            cleaned = cleaned.split('@')[0]
        return re.sub(r'[^a-zA-Z\s]', '', cleaned).strip()

    def find_potential_matches(self, candidate_name: str, existing_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        norm_candidate = self.normalize_name(candidate_name)
        matches = []

        for entity in existing_entities:
            target_name = entity.get("name", "")
            norm_target = self.normalize_name(target_name)

            score = jaro_winkler_similarity(norm_candidate, norm_target)
            
            # Also check alias list
            alias_scores = [jaro_winkler_similarity(candidate_name, alias) for alias in entity.get("aliases", [])]
            max_alias_score = max(alias_scores) if alias_scores else 0.0
            
            best_score = max(score, max_alias_score)

            if best_score >= self.threshold:
                matches.append({
                    "existing_entity_id": entity.get("id"),
                    "existing_name": target_name,
                    "candidate_name": candidate_name,
                    "similarity_score": round(best_score, 3),
                    "suggested_action": "MERGE" if best_score >= 0.92 else "REVIEW_ALIAS"
                })

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches
