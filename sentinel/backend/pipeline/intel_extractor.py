import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import networkx as nx

from pipeline.ner_extractor import IndianLawNER
from pipeline.relation_builder import deduplicate_entities

class IntelReportExtractor:
    """
    Processes unstructured surveillance and field intelligence reports.
    Extracts entities with strict sentence-level and character-level PROVENANCE linking,
    enabling court-admissible evidential trace-back to the exact source text.
    """
    def __init__(self):
        self.ner = IndianLawNER()

    def process_intel_text(
        self,
        text: str,
        doc_id: str = "INTEL_REPORT",
        doc_title: str = "Field Intelligence Note",
        author: str = "Field Informant / Special Cell",
        source_type: str = "HUMINT_SURVEILLANCE"
    ) -> Dict[str, Any]:
        """
        Splits text into sentences, runs NER, extracts relations, and attaches full provenance.
        """
        # Split into sentences using punctuation boundaries
        sentence_spans = []
        raw_sentences = re.split(r'(?<=[.!?\n])\s+', text)
        curr_offset = 0
        for idx, s in enumerate(raw_sentences):
            cleaned = s.strip()
            if not cleaned:
                continue
            start = text.find(cleaned, curr_offset)
            if start == -1:
                start = curr_offset
            end = start + len(cleaned)
            curr_offset = end
            sentence_spans.append({
                'sentence_index': idx,
                'sentence_text': cleaned,
                'char_start': start,
                'char_end': end
            })

        extracted_entities = []
        # Extract entities across whole text
        raw_entities = self.ner.extract_entities(text)

        # Attach provenance to each entity
        for ent in raw_entities:
            s_start = ent.get('start', 0)
            s_end = ent.get('end', 0)
            
            matching_sent = None
            for s in sentence_spans:
                if s['char_start'] <= s_start < s['char_end']:
                    matching_sent = s
                    break

            provenance = {
                'doc_id': doc_id,
                'doc_title': doc_title,
                'author': author,
                'source_type': source_type,
                'sentence_index': matching_sent['sentence_index'] if matching_sent else 0,
                'snippet': matching_sent['sentence_text'] if matching_sent else text[max(0, s_start-20):min(len(text), s_end+20)],
                'char_start': s_start,
                'char_end': s_end,
                'extracted_at': datetime.now().isoformat()
            }

            extracted_entities.append({
                'id': str(uuid.uuid4())[:8],
                'text': ent['text'],
                'entity_type': ent['entity_type'],
                'confidence': ent.get('confidence', 0.85),
                'provenance': provenance
            })

        # Extract relationships with provenance
        raw_relations = self.ner.extract_relations(text, raw_entities)
        extracted_relations = []

        for rel in raw_relations:
            snippet = rel.get('source_text', '')
            matching_sent_idx = 0
            for s in sentence_spans:
                if snippet in s['sentence_text'] or s['sentence_text'] in snippet:
                    matching_sent_idx = s['sentence_index']
                    break

            extracted_relations.append({
                'source': rel['source'],
                'target': rel['target'],
                'relation_type': rel['relation_type'],
                'confidence': rel.get('confidence', 0.8),
                'provenance': {
                    'doc_id': doc_id,
                    'doc_title': doc_title,
                    'sentence_index': matching_sent_idx,
                    'snippet': snippet,
                    'source_type': source_type,
                    'extracted_at': datetime.now().isoformat()
                }
            })

        return {
            'doc_id': doc_id,
            'doc_title': doc_title,
            'total_sentences': len(sentence_spans),
            'entities': extracted_entities,
            'relations': extracted_relations,
            'sentence_spans': sentence_spans
        }

    def ingest_intel_into_graph(
        self,
        G: nx.MultiDiGraph,
        intel_result: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Ingests extracted intelligence entities and relationships into the active NetworkX graph,
        persisting all provenance attributes directly on nodes and edges.
        """
        doc_id = intel_result['doc_id']
        doc_node_id = f"INTEL_{doc_id}"

        # 1. Create a Document Node for provenance linking
        G.add_node(
            doc_node_id,
            node_type="Evidence",
            label=intel_result.get('doc_title', 'Intel Note'),
            title=intel_result.get('doc_title', 'Intel Note'),
            file_type="SURVEILLANCE_REPORT",
            created_at=datetime.now().isoformat(),
            risk_score=0.7
        )

        nodes_added = 1
        edges_added = 0

        # 2. Add Entities
        for ent in intel_result.get('entities', []):
            etype = ent['entity_type']
            txt = ent['text']
            node_id = f"{etype}_{re.sub(r'[^a-zA-Z0-9]', '_', txt.upper())}"

            # If node doesn't exist, add it
            if not G.has_node(node_id):
                n_type = "Person" if etype in ("PERSON", "NAME") else \
                         "Phone" if etype == "PHONE" else \
                         "Vehicle" if etype == "VEHICLE_REG" else \
                         "Location" if etype == "LOCATION" else \
                         "Weapon" if etype == "WEAPON" else "Evidence"
                
                G.add_node(
                    node_id,
                    node_type=n_type,
                    label=txt,
                    name=txt,
                    provenance=ent.get('provenance', {}),
                    confidence=ent.get('confidence', 0.85),
                    risk_score=0.65
                )
                nodes_added += 1

            # Connect entity to the source intelligence document node
            G.add_edge(
                node_id,
                doc_node_id,
                edge_type="DOCUMENTED_IN",
                confidence=ent.get('confidence', 0.85),
                provenance=ent.get('provenance', {})
            )
            edges_added += 1

        # 3. Add Relations
        for rel in intel_result.get('relations', []):
            src_node = f"PERSON_{re.sub(r'[^a-zA-Z0-9]', '_', rel['source'].upper())}"
            tgt_node = f"PERSON_{re.sub(r'[^a-zA-Z0-9]', '_', rel['target'].upper())}"
            if not G.has_node(src_node):
                src_node = rel['source']
            if not G.has_node(tgt_node):
                tgt_node = rel['target']

            G.add_edge(
                src_node,
                tgt_node,
                edge_type=rel['relation_type'],
                confidence=rel.get('confidence', 0.8),
                provenance=rel.get('provenance', {})
            )
            edges_added += 1

        return {'nodes_added': nodes_added, 'edges_added': edges_added}
