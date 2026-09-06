import networkx as nx
from typing import List, Dict, Any, Optional
import uuid
import re

def normalize_text_id(prefix: str, text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9]', '_', text.strip()).strip('_')
    if not cleaned:
        cleaned = uuid.uuid4().hex[:8]
    return f"{prefix}_{cleaned.upper()}"

def add_entities_to_graph(G: nx.MultiDiGraph, entities: List[Dict[str, Any]]) -> Dict[str, int]:
    """Adds or merges extracted entities as typed nodes into the NetworkX MultiDiGraph."""
    added = 0
    updated = 0
    skipped = 0

    type_mapping = {
        'PERSON': ('Person', 'PER'),
        'PHONE': ('Phone', 'PHN'),
        'LOCATION': ('Location', 'LOC'),
        'VEHICLE_REG': ('Vehicle', 'VEH'),
        'ORGANIZATION': ('Organization', 'ORG'),
        'IPC_SECTION': ('Incident', 'IPC'),
        'FIR_NO': ('Incident', 'FIR'),
        'AADHAAR': ('Person', 'ADH'),
        'WEAPON': ('Weapon', 'WPN'),
        'BANK_ACCOUNT': ('BankAccount', 'ACC'),
        'AMOUNT': ('BankAccount', 'AMT'),
        'CRYPTO_WALLET': ('BankAccount', 'WLT'),
        'UPI_ID': ('BankAccount', 'UPI'),
        'SOCIAL_MEDIA': ('Evidence', 'SOC'),
        'EMAIL': ('Evidence', 'EML')
    }

    for ent in entities:
        text = ent.get('text', '').strip()
        etype = ent.get('entity_type', 'Evidence')
        if not text:
            skipped += 1
            continue

        canonical_type, prefix = type_mapping.get(etype, ('Evidence', 'EVD'))
        node_id = ent.get('matched_id') or ent.get('id') or normalize_text_id(prefix, text)
        ent['matched_id'] = node_id

        if G.has_node(node_id):
            G.nodes[node_id]['last_updated'] = 'Recent'
            updated += 1
        else:
            attrs = {
                'id': node_id,
                'label': text,
                'name': text,
                'node_type': canonical_type,
                'type': canonical_type,
                'confidence': ent.get('confidence', 0.9),
                'source': ent.get('source', 'INGESTION_PIPELINE')
            }
            if canonical_type == 'Person':
                attrs['status'] = 'SUSPECT'
                attrs['risk_score'] = 0.5
            elif canonical_type == 'Phone':
                attrs['number'] = text
                attrs['is_burner'] = False
            elif canonical_type == 'Vehicle':
                attrs['registration_no'] = text

            G.add_node(node_id, **attrs)
            added += 1

    return {'added': added, 'updated': updated, 'skipped': skipped}

def add_relations_to_graph(G: nx.MultiDiGraph, relations: List[Dict[str, Any]], entities: Optional[List[Dict[str, Any]]] = None) -> Dict[str, int]:
    """Adds typed relationship edges between resolved nodes in the graph."""
    added = 0
    skipped = 0

    # Build text lookup map to match source/target strings to real node IDs
    text_to_id = {}
    if entities:
        for ent in entities:
            t = ent.get('text', '').strip().lower()
            m_id = ent.get('matched_id') or ent.get('id')
            if t and m_id:
                text_to_id[t] = m_id

    for node, data in G.nodes(data=True):
        lbl = str(data.get('label', '')).strip().lower()
        if lbl:
            text_to_id[lbl] = node
        name = str(data.get('name', '')).strip().lower()
        if name:
            text_to_id[name] = node

    for rel in relations:
        src_raw = str(rel.get('source', '')).strip()
        tgt_raw = str(rel.get('target', '')).strip()
        rtype = rel.get('relation_type', 'ASSOCIATE_OF')

        if not src_raw or not tgt_raw:
            skipped += 1
            continue

        src_id = text_to_id.get(src_raw.lower(), src_raw)
        tgt_id = text_to_id.get(tgt_raw.lower(), tgt_raw)

        if not G.has_node(src_id):
            G.add_node(src_id, id=src_id, label=src_raw, name=src_raw, node_type='Person', type='Person')
        if not G.has_node(tgt_id):
            G.add_node(tgt_id, id=tgt_id, label=tgt_raw, name=tgt_raw, node_type='Evidence', type='Evidence')

        # Prevent duplicate edge
        exists = False
        if G.has_edge(src_id, tgt_id):
            for k, data in G.get_edge_data(src_id, tgt_id).items():
                if data.get('edge_type') == rtype or data.get('type') == rtype:
                    exists = True
                    break

        if not exists:
            G.add_edge(
                src_id, tgt_id,
                edge_type=rtype,
                type=rtype,
                label=rtype,
                confidence=rel.get('confidence', 0.85),
                source_text=rel.get('source_text', '')
            )
            added += 1
        else:
            skipped += 1

    return {'added': added, 'skipped': skipped}

def process_ingested_data(G: nx.MultiDiGraph, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Coordinates entity insertion and edge creation into graph store."""
    ent_res = add_entities_to_graph(G, entities)
    rel_res = add_relations_to_graph(G, relations, entities)
    return {
        'entities_added': ent_res['added'],
        'entities_updated': ent_res['updated'],
        'relations_added': rel_res['added'],
        'total_graph_nodes': G.number_of_nodes(),
        'total_graph_edges': G.number_of_edges()
    }
