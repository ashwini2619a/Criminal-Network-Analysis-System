import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict

class IndianLawNER:
    """
    Custom Rule-based and Lexicon-augmented NER pipeline specifically designed for
    Indian Law Enforcement reports, FIRs, CDR records, and intelligence briefs.
    """
    def __init__(self):
        # 1. Regex patterns for structured Indian identifiers
        self.patterns = {
            'PHONE': re.compile(r'(?:\+91[- ]?)?[6-9]\d{9}\b'),
            'AADHAAR': re.compile(r'\b[2-9]\d{3}[ -]\d{4}[ -]\d{4}\b'),
            'VEHICLE_REG': re.compile(r'\b(?:JH|DL|BR|MH|UP|HR|PB|WB|KA|TN|GJ|RJ|MP|OD|CH|TS|AP)[ -]?\d{2}[ -]?[A-Z]{1,2}[ -]?\d{4}\b', re.IGNORECASE),
            'IPC_SECTION': re.compile(r'(?:(?:u/s|u/sec|section|sec\.?)\s*)?(\b(?:120B|302|307|364A|376|395|420|467|468|471|384|506|34|149|201|411|414)\b(?:\s*IPC)?)', re.IGNORECASE),
            'AMOUNT': re.compile(r'(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{2})?)\b', re.IGNORECASE),
            'DATE': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            'TIME': re.compile(r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s*hrs)?\b', re.IGNORECASE),
            'FIR_NO': re.compile(r'\bFIR(?:/|\s*No\.?\s*)?\d{1,5}(?:/\d{4})?\b', re.IGNORECASE),
            'UPI_ID': re.compile(r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b'),
            'IFSC': re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b'),
            'SOCIAL_MEDIA': re.compile(r'(?:@|t\.me\/|twitter\.com\/|x\.com\/|instagram\.com\/|facebook\.com\/)([a-zA-Z0-9_.]{3,32})\b'),
            'CRYPTO_WALLET': re.compile(r'\b(?:0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b'),
            'EMAIL': re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
        }

        # 2. Curated Indian names vocabulary
        self.first_names = {
            "rajesh", "vikram", "anita", "ramesh", "suresh", "deepak", "farooq", "lakshmi",
            "sunita", "arun", "manoj", "sanjay", "pooja", "rahul", "amit", "ravi", "geeta",
            "rizwan", "pradeep", "kavita", "neeraj", "ajay", "vijay", "mohammed", "ashok",
            "dinesh", "alok", "anil", "pankaj", "rohit", "santosh", "vinod", "brijesh",
            "mukesh", "satish", "harish", "dhirendra", "abhimanyu", "devendra", "chhotu",
            "sharma", "singh", "yadav", "patel", "tiwari", "ahmed", "narayan", "kumari",
            "joshi", "dubey", "mishra", "gupta", "verma", "shah", "shankar", "devi", "chauhan",
            "kumar", "khan", "pandey", "ali", "das", "thakur", "jha", "singhania"
        }

        # 3. Known locations & gangs
        self.locations = {
            "patna", "ranchi", "delhi", "mumbai", "lucknow", "kolkata", "jamshedpur",
            "varanasi", "bhopal", "hyderabad", "kanpur", "dhanbad", "muzaffarpur", "gaya",
            "bokaro", "asansol", "allahabad", "prayagraj", "gorakhpur", "meerut", "agra",
            "kotwali", "tower chowk", "bistupur", "dak bunglow", "hazratganj", "chandni chowk"
        }

        self.organizations = {
            "ranchi syndicate", "patna gold mafia", "delhi hawala network",
            "jharkhand mining cartel", "border arms ring", "d-company", "lawrence gang",
            "sand mafia", "coal mafia", "syndicate", "cartel", "gang"
        }

        self.weapons = {
            "pistol", "revolver", "country-made pistol", "desi katta", "ak-47", "rifle",
            "firearm", "cartridges", "ammunition", "knife", "dagger", "explosives"
        }

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extracts structured law enforcement entities with offsets, types, and confidence scores."""
        entities = []
        occupied_spans = []

        def span_overlaps(s, e):
            return any(not (e <= os or s >= oe) for os, oe in occupied_spans)

        # 1. Regex pattern matches (High Confidence = 0.90 - 0.95)
        for etype, pattern in self.patterns.items():
            for m in pattern.finditer(text):
                s, e = m.start(), m.end()
                if not span_overlaps(s, e):
                    entities.append({
                        'text': m.group(0).strip(),
                        'entity_type': etype,
                        'start': s,
                        'end': e,
                        'confidence': 0.95 if etype in ('PHONE', 'AADHAAR', 'VEHICLE_REG') else 0.88
                    })
                    occupied_spans.append((s, e))

        # 2. Location dictionary matching
        lower_text = text.lower()
        for loc in self.locations:
            pattern = r'\b' + re.escape(loc) + r'\b'
            for m in re.finditer(pattern, lower_text):
                s, e = m.start(), m.end()
                if not span_overlaps(s, e):
                    orig_text = text[s:e]
                    entities.append({
                        'text': orig_text,
                        'entity_type': 'LOCATION',
                        'start': s,
                        'end': e,
                        'confidence': 0.85
                    })
                    occupied_spans.append((s, e))

        # 3. Organization matching
        for org in self.organizations:
            pattern = r'\b' + re.escape(org) + r'\b'
            for m in re.finditer(pattern, lower_text):
                s, e = m.start(), m.end()
                if not span_overlaps(s, e):
                    entities.append({
                        'text': text[s:e],
                        'entity_type': 'ORGANIZATION',
                        'start': s,
                        'end': e,
                        'confidence': 0.90
                    })
                    occupied_spans.append((s, e))

        # 4. Weapon matching
        for wpn in self.weapons:
            pattern = r'\b' + re.escape(wpn) + r'\b'
            for m in re.finditer(pattern, lower_text):
                s, e = m.start(), m.end()
                if not span_overlaps(s, e):
                    entities.append({
                        'text': text[s:e],
                        'entity_type': 'WEAPON',
                        'start': s,
                        'end': e,
                        'confidence': 0.85
                    })
                    occupied_spans.append((s, e))

        # 5. Name recognition heuristic (Capitalized 2-3 word sequences containing known Indian names)
        # e.g., "Vikram Singh", "Deepak Tiwari", "Shri Ramesh Yadav", "Anita Devi"
        name_regex = re.compile(r'\b(?:Shri|Smt|Late|Mohd|Md\.\s*)?([A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15}){1,2})\b')
        for m in name_regex.finditer(text):
            s, e = m.start(), m.end()
            cand_name = m.group(1).strip()
            words = [w.lower() for w in cand_name.split()]
            if any(w in self.first_names for w in words):
                if not span_overlaps(s, e):
                    entities.append({
                        'text': cand_name,
                        'entity_type': 'PERSON',
                        'start': s,
                        'end': e,
                        'confidence': 0.82
                    })
                    occupied_spans.append((s, e))

        # Sort entities by start position
        entities.sort(key=lambda x: x['start'])
        return entities

    def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts semantic relationships between entities based on contextual co-occurrence and syntactic triggers.
        """
        relations = []
        sentences = re.split(r'[.\n;]+', text)
        
        # Helper to find which entities fall inside a sentence
        running_idx = 0
        for sentence in sentences:
            sent_start = text.find(sentence, running_idx)
            if sent_start == -1:
                continue
            sent_end = sent_start + len(sentence)
            running_idx = sent_end
            
            sent_lower = sentence.lower()
            sent_entities = [e for e in entities if sent_start <= e['start'] < sent_end]
            
            persons = [e for e in sent_entities if e['entity_type'] == 'PERSON']
            phones = [e for e in sent_entities if e['entity_type'] == 'PHONE']
            vehicles = [e for e in sent_entities if e['entity_type'] == 'VEHICLE_REG']
            locations = [e for e in sent_entities if e['entity_type'] == 'LOCATION']
            amounts = [e for e in sent_entities if e['entity_type'] == 'AMOUNT']
            orgs = [e for e in sent_entities if e['entity_type'] == 'ORGANIZATION']
            
            # Rule 1: Person + Phone -> OWNS / OPERATES
            for p in persons:
                for ph in phones:
                    relations.append({
                        'source': p['text'],
                        'target': ph['text'],
                        'relation_type': 'OWNS',
                        'confidence': 0.85,
                        'source_text': sentence.strip()
                    })

            # Rule 2: Person + Vehicle -> OWNS / SEEN_IN
            for p in persons:
                for v in vehicles:
                    rel = "SEEN_IN" if any(w in sent_lower for w in ["seen", "boarded", "travel", "spotted"]) else "OWNS"
                    relations.append({
                        'source': p['text'],
                        'target': v['text'],
                        'relation_type': rel,
                        'confidence': 0.80,
                        'source_text': sentence.strip()
                    })

            # Rule 3: Person + Location -> LOCATED_AT / OPERATES_IN
            for p in persons:
                for loc in locations:
                    relations.append({
                        'source': p['text'],
                        'target': loc['text'],
                        'relation_type': 'LOCATED_AT',
                        'confidence': 0.75,
                        'source_text': sentence.strip()
                    })

            # Rule 4: Person + Organization -> OPERATES_IN
            for p in persons:
                for org in orgs:
                    relations.append({
                        'source': p['text'],
                        'target': org['text'],
                        'relation_type': 'OPERATES_IN',
                        'confidence': 0.88,
                        'source_text': sentence.strip()
                    })

            # Rule 5: Multiple Persons in same sentence with associative triggers -> ASSOCIATE_OF / COMMITTED
            if len(persons) >= 2:
                for i in range(len(persons)):
                    for j in range(i + 1, len(persons)):
                        p1 = persons[i]['text']
                        p2 = persons[j]['text']
                        rel_type = "COMMITTED" if any(w in sent_lower for w in ["fired", "abducted", "stole", "robbed", "murdered"]) else "ASSOCIATE_OF"
                        relations.append({
                            'source': p1,
                            'target': p2,
                            'relation_type': rel_type,
                            'confidence': 0.82,
                            'source_text': sentence.strip()
                        })

            # Rule 6: Person + Social Media Handle -> USES_HANDLE
            social_handles = [e for e in sent_entities if e['entity_type'] == 'SOCIAL_MEDIA']
            for p in persons:
                for sm in social_handles:
                    relations.append({
                        'source': p['text'],
                        'target': sm['text'],
                        'relation_type': 'USES_HANDLE',
                        'confidence': 0.85,
                        'source_text': sentence.strip()
                    })

            # Rule 7: Person + Crypto Wallet -> CONTROLS_WALLET
            crypto_wallets = [e for e in sent_entities if e['entity_type'] == 'CRYPTO_WALLET']
            for p in persons:
                for cw in crypto_wallets:
                    relations.append({
                        'source': p['text'],
                        'target': cw['text'],
                        'relation_type': 'CONTROLS_WALLET',
                        'confidence': 0.88,
                        'source_text': sentence.strip()
                    })

        return relations
