import re
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher

def fuzzy_match_name(name1: str, name2: str, threshold: float = 0.82) -> bool:
    """Computes similarity ratio between two names, handling titles like Shri, Late, etc."""
    clean1 = re.sub(r'\b(shri|smt|late|mohd|md|mr|dr)\b', '', name1.lower()).strip()
    clean2 = re.sub(r'\b(shri|smt|late|mohd|md|mr|dr)\b', '', name2.lower()).strip()
    if not clean1 or not clean2:
        return False
    if clean1 == clean2 or clean1 in clean2 or clean2 in clean1:
        return True
    return SequenceMatcher(None, clean1, clean2).ratio() >= threshold

def normalize_phone(phone: str) -> str:
    """Normalizes phone string to standard 10-digit format for canonical deduplication."""
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 12 and digits.startswith('91'):
        return digits[2:]
    if len(digits) == 11 and digits.startswith('0'):
        return digits[1:]
    return digits[-10:] if len(digits) >= 10 else digits

def deduplicate_entities(new_entities: List[Dict[str, Any]], existing_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Matches extracted entities against existing graph nodes to prevent entity duplication.
    Assigns 'matched_id' and 'is_new' flags.
    """
    processed = []
    
    for ent in new_entities:
        e_type = ent.get('entity_type')
        e_text = ent.get('text', '').strip()
        matched_id = None
        
        if e_type == 'PHONE':
            norm = normalize_phone(e_text)
            for ex in existing_nodes:
                if ex.get('node_type') == 'Phone':
                    ex_phone = normalize_phone(ex.get('number', '') or ex.get('id', ''))
                    if ex_phone and ex_phone == norm:
                        matched_id = ex.get('id')
                        break

        elif e_type == 'PERSON':
            for ex in existing_nodes:
                if ex.get('node_type') == 'Person':
                    ex_name = ex.get('name') or ex.get('label') or ''
                    if fuzzy_match_name(e_text, ex_name):
                        matched_id = ex.get('id')
                        break

        elif e_type == 'VEHICLE_REG':
            clean_reg = re.sub(r'[^A-Za-z0-9]', '', e_text).upper()
            for ex in existing_nodes:
                if ex.get('node_type') == 'Vehicle':
                    ex_reg = re.sub(r'[^A-Za-z0-9]', '', ex.get('registration_no', '')).upper()
                    if ex_reg and ex_reg == clean_reg:
                        matched_id = ex.get('id')
                        break

        processed.append({
            **ent,
            'matched_id': matched_id,
            'is_new': matched_id is None
        })

    return processed

def build_relations_from_cooccurrence(entities: List[Dict[str, Any]], document_id: str) -> List[Dict[str, Any]]:
    """
    Builds documentary provenance links (REPORTED_IN) for all entities mentioned in a case document.
    """
    relations = []
    for ent in entities:
        target = ent.get('matched_id') or ent.get('text')
        relations.append({
            'source': target,
            'target': document_id,
            'relation_type': 'REPORTED_IN',
            'confidence': ent.get('confidence', 0.9),
            'notes': f"Extracted from document ID {document_id}"
        })
    return relations
