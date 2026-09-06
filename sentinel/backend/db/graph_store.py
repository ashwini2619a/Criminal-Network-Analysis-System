import networkx as nx
import json
import os
from typing import Dict, List, Optional, Any

class GraphStore:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.version = 1
        
    def load_from_json(self, data_dir: str):
        if not os.path.exists(data_dir):
            print(f"GraphStore: Directory {data_dir} does not exist.")
            return

        suspects_path = os.path.join(data_dir, "suspects.json")
        suspect_by_phone = {}
        suspect_by_account = {}
        
        if os.path.exists(suspects_path):
            with open(suspects_path, 'r', encoding='utf-8') as f:
                suspects = json.load(f)
                for s in suspects:
                    s_id = s["id"]
                    self.add_node(
                        node_type="Person",
                        node_id=s_id,
                        label=s.get("name", "Unknown"),
                        name=s.get("name", "Unknown"),
                        aliases=s.get("aliases", []),
                        age=s.get("age", 30),
                        gender=s.get("gender", "M"),
                        aadhaar_hash=s.get("aadhaar_hash", ""),
                        criminal_record_no=s.get("criminal_record_no", ""),
                        risk_score=s.get("risk_score", 0.5),
                        status=s.get("status", "SUSPECT"),
                        mugshot_path=s.get("mugshot_path"),
                        phone=s.get("phone", ""),
                        account=s.get("account", "")
                    )
                    
                    if s.get("phone"):
                        phone_id = f"PHONE_{s['phone']}"
                        sus_phone = s["phone"]
                        suspect_by_phone[sus_phone] = s_id
                        self.add_node(
                            node_type="Phone",
                            node_id=phone_id,
                            label=sus_phone,
                            number=sus_phone,
                            is_burner=False
                        )
                        self.add_edge(s_id, phone_id, edge_type="OWNS", label="OWNS")

                    if s.get("account"):
                        acc_id = f"ACC_{s['account']}"
                        sus_acc = s["account"]
                        suspect_by_account[sus_acc] = s_id
                        self.add_node(
                            node_type="BankAccount",
                            node_id=acc_id,
                            label=sus_acc,
                            account_no=sus_acc,
                            holder_name=s.get("name", "Unknown")
                        )
                        self.add_edge(s_id, acc_id, edge_type="OWNS", label="OWNS")

        locations_path = os.path.join(data_dir, "locations.json")
        if os.path.exists(locations_path):
            with open(locations_path, 'r', encoding='utf-8') as f:
                locations = json.load(f)
                for loc in locations:
                    self.add_node(
                        node_type="Location",
                        node_id=loc["id"],
                        label=loc.get("name", "Location"),
                        name=loc.get("name", "Location"),
                        lat=loc.get("lat", 0.0),
                        lon=loc.get("lon", 0.0),
                        district=loc.get("district", ""),
                        state=loc.get("state", ""),
                        location_type=loc.get("location_type", "HIDEOUT")
                    )

        vehicles_path = os.path.join(data_dir, "vehicles.json")
        if os.path.exists(vehicles_path):
            with open(vehicles_path, 'r', encoding='utf-8') as f:
                vehicles = json.load(f)
                for v in vehicles:
                    v_id = v["id"]
                    reg = v.get("registration_no", "Unknown")
                    self.add_node(
                        node_type="Vehicle",
                        node_id=v_id,
                        label=reg,
                        registration_no=reg,
                        chassis_no=v.get("chassis_no", ""),
                        engine_no=v.get("engine_no", ""),
                        make=v.get("make", ""),
                        model=v.get("model", ""),
                        color=v.get("color", ""),
                        owner_name=v.get("owner_name", "")
                    )

        orgs_path = os.path.join(data_dir, "organizations.json")
        if os.path.exists(orgs_path):
            with open(orgs_path, 'r', encoding='utf-8') as f:
                orgs = json.load(f)
                for org in orgs:
                    org_id = org["id"]
                    self.add_node(
                        node_type="Organization",
                        node_id=org_id,
                        label=org.get("name", "Organization"),
                        name=org.get("name", "Organization"),
                        org_type=org.get("type", "GANG"),
                        type=org.get("type", "GANG"),
                        threat_level=org.get("threat_level", 3),
                        members=org.get("members", [])
                    )
                    for m_id in org.get("members", []):
                        if self.graph.has_node(m_id):
                            self.add_edge(m_id, org_id, edge_type="OPERATES_IN", label="OPERATES_IN")

        incidents_path = os.path.join(data_dir, "incidents.json")
        if os.path.exists(incidents_path):
            with open(incidents_path, 'r', encoding='utf-8') as f:
                incidents = json.load(f)
                for inc in incidents:
                    inc_id = inc["id"]
                    self.add_node(
                        node_type="Incident",
                        node_id=inc_id,
                        label=inc.get("fir_no", "Incident"),
                        fir_no=inc.get("fir_no", ""),
                        police_station=inc.get("police_station", ""),
                        ipc_sections=inc.get("ipc_sections", []),
                        date_time=inc.get("date_time", ""),
                        severity=inc.get("severity", "MEDIUM"),
                        description=inc.get("description", "")
                    )

        towers_path = os.path.join(data_dir, "cell_towers.json")
        if os.path.exists(towers_path):
            with open(towers_path, 'r', encoding='utf-8') as f:
                towers = json.load(f)
                for twr in towers:
                    t_id = twr["id"]
                    self.add_node(
                        node_type="CellTower",
                        node_id=t_id,
                        label=twr.get("name", t_id),
                        tower_id=twr.get("tower_id", t_id),
                        operator=twr.get("operator", "Jio"),
                        lat=twr.get("lat", 0.0),
                        lon=twr.get("lon", 0.0),
                        district=twr.get("district", "")
                    )

        rel_path = os.path.join(data_dir, "relationships.json")
        if os.path.exists(rel_path):
            with open(rel_path, 'r', encoding='utf-8') as f:
                relationships = json.load(f)
                for rel in relationships:
                    src = rel.get("source")
                    tgt = rel.get("target")
                    rtype = rel.get("edge_type") or rel.get("type", "ASSOCIATE_OF")
                    if src and tgt and self.graph.has_node(src) and self.graph.has_node(tgt):
                        self.add_edge(src, tgt, edge_type=rtype, label=rel.get("label", rtype), **{k: v for k, v in rel.items() if k not in ("source", "target", "type", "edge_type", "label")})

        cdrs_path = os.path.join(data_dir, "cdrs.json")
        if os.path.exists(cdrs_path):
            with open(cdrs_path, 'r', encoding='utf-8') as f:
                cdrs = json.load(f)
                for cdr in cdrs:
                    c_num = cdr.get("caller_number")
                    r_num = cdr.get("receiver_number")
                    c_phone_id = f"PHONE_{c_num}"
                    r_phone_id = f"PHONE_{r_num}"

                    if not self.graph.has_node(c_phone_id):
                        self.add_node(node_type="Phone", node_id=c_phone_id, label=c_num, number=c_num, is_burner="BURNER" in cdr.get("caller_imei", ""))
                    if not self.graph.has_node(r_phone_id):
                        self.add_node(node_type="Phone", node_id=r_phone_id, label=r_num, number=r_num, is_burner="BURNER" in cdr.get("receiver_imei", ""))

                    self.add_edge(
                        c_phone_id,
                        r_phone_id,
                        edge_type="CALLED",
                        label="CALLED",
                        duration_sec=cdr.get("duration_sec", 60),
                        timestamp=cdr.get("timestamp", ""),
                        tower_id=cdr.get("tower_id", ""),
                        tower_lat=cdr.get("tower_lat", 0.0),
                        tower_lon=cdr.get("tower_lon", 0.0),
                        caller_imei=cdr.get("caller_imei", ""),
                        receiver_imei=cdr.get("receiver_imei", "")
                    )

                    s1 = suspect_by_phone.get(c_num)
                    s2 = suspect_by_phone.get(r_num)
                    if s1 and s2 and s1 != s2:
                        self.add_edge(
                            s1, s2,
                            edge_type="CALLED",
                            label="CALLED",
                            duration_sec=cdr.get("duration_sec", 60),
                            timestamp=cdr.get("timestamp", "")
                        )

        tx_path = os.path.join(data_dir, "transactions.json")
        if os.path.exists(tx_path):
            with open(tx_path, 'r', encoding='utf-8') as f:
                txs = json.load(f)
                for tx in txs:
                    s_acc = tx.get("sender_account")
                    r_acc = tx.get("receiver_account")
                    s_acc_id = f"ACC_{s_acc}"
                    r_acc_id = f"ACC_{r_acc}"

                    if not self.graph.has_node(s_acc_id):
                        self.add_node(node_type="BankAccount", node_id=s_acc_id, label=s_acc, account_no=s_acc, holder_name=tx.get("sender_name", ""), bank_name=tx.get("sender_bank", ""))
                    if not self.graph.has_node(r_acc_id):
                        self.add_node(node_type="BankAccount", node_id=r_acc_id, label=r_acc, account_no=r_acc, holder_name=tx.get("receiver_name", ""), bank_name=tx.get("receiver_bank", ""))

                    self.add_edge(
                        s_acc_id,
                        r_acc_id,
                        edge_type="TRANSFERRED_MONEY",
                        label="TRANSFERRED_MONEY",
                        amount=float(tx.get("amount", 0)),
                        utr=tx.get("utr", ""),
                        timestamp=tx.get("timestamp", ""),
                        transaction_type=tx.get("transaction_type", "NEFT")
                    )

                    s1 = suspect_by_account.get(s_acc)
                    s2 = suspect_by_account.get(r_acc)
                    if s1 and s2 and s1 != s2:
                        self.add_edge(
                            s1, s2,
                            edge_type="TRANSFERRED_MONEY",
                            label="TRANSFERRED_MONEY",
                            amount=float(tx.get("amount", 0)),
                            utr=tx.get("utr", ""),
                            timestamp=tx.get("timestamp", "")
                        )

        print(f"GraphStore: Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

    def save_graph(self, path: str):
        nx.write_graphml(self.graph, path)
        
    def load_graph(self, path: str):
        if os.path.exists(path):
            self.graph = nx.read_graphml(path)
            
    def add_node(self, node_type: str, node_id: str, **attrs):
        attrs['node_type'] = node_type
        attrs['type'] = node_type
        if 'label' not in attrs:
            attrs['label'] = attrs.get('name', node_id)
        self.graph.add_node(node_id, **attrs)
        self.version += 1
        
    def add_edge(self, source: str, target: str, edge_type: str, **attrs):
        attrs['edge_type'] = edge_type
        attrs['type'] = edge_type
        if 'label' not in attrs:
            attrs['label'] = edge_type
        self.graph.add_edge(source, target, **attrs)
        self.version += 1
        
    def resolve_node_id(self, identifier: str) -> Optional[str]:
        if not identifier:
            return None
        if self.graph.has_node(identifier):
            return identifier
        matches = self.search_nodes(identifier)
        if matches:
            return matches[0]["id"]
        cleaned = identifier
        for prefix in ["SUSP-", "SUSP_", "PERSON-", "PERSON_", "ACC-", "ACC_", "PHONE-", "PHONE_", "INC-", "INC_"]:
            if cleaned.upper().startswith(prefix):
                cleaned = cleaned[len(prefix):]
        cleaned_search = cleaned.replace("-", " ").replace("_", " ").strip()
        if cleaned_search:
            matches = self.search_nodes(cleaned_search)
            if matches:
                return matches[0]["id"]
        return None

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        actual_id = self.resolve_node_id(node_id) or node_id
        if self.graph.has_node(actual_id):
            data = dict(self.graph.nodes[actual_id])
            data['id'] = actual_id
            return data
        return None
        
    def get_neighbors(self, node_id: str, depth: int = 1) -> Dict[str, List[Any]]:
        actual_id = self.resolve_node_id(node_id) or node_id
        if not self.graph.has_node(actual_id):
            return {"nodes": [], "edges": []}
            
        visited_nodes = {actual_id}
        edges = []
        current_level = [actual_id]
        
        for _ in range(depth):
            next_level = []
            for n in current_level:
                for neighbor in list(self.graph.neighbors(n)) + list(self.graph.predecessors(n)):
                    if neighbor not in visited_nodes:
                        visited_nodes.add(neighbor)
                        next_level.append(neighbor)
                    
                    if self.graph.has_edge(n, neighbor):
                        for k, edge_data in self.graph.get_edge_data(n, neighbor).items():
                            edges.append({"source": n, "target": neighbor, **edge_data})
                    if self.graph.has_edge(neighbor, n):
                        for k, edge_data in self.graph.get_edge_data(neighbor, n).items():
                            edges.append({"source": neighbor, "target": n, **edge_data})
            current_level = next_level
            
        nodes = [{"id": n, **self.graph.nodes[n]} for n in visited_nodes]
        return {"nodes": nodes, "edges": edges}
        
    def get_full_graph(self) -> Dict[str, List[Dict[str, Any]]]:
        nodes = [{"id": n, **attr} for n, attr in self.graph.nodes(data=True)]
        edges = [{"source": u, "target": v, **attr} for u, v, k, attr in self.graph.edges(keys=True, data=True)]
        return {"nodes": nodes, "edges": edges}
        
    def get_subgraph(self, node_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        sub = self.graph.subgraph(node_ids)
        nodes = [{"id": n, **attr} for n, attr in sub.nodes(data=True)]
        edges = [{"source": u, "target": v, **attr} for u, v, k, attr in sub.edges(keys=True, data=True)]
        return {"nodes": nodes, "edges": edges}
        
    def shortest_path(self, source: str, target: str) -> List[str]:
        try:
            s_actual = self.resolve_node_id(source) or source
            t_actual = self.resolve_node_id(target) or target
            undirected = self.graph.to_undirected()
            return nx.shortest_path(undirected, source=s_actual, target=t_actual)
        except Exception:
            return []
            
    def search_nodes(self, query: str) -> List[Dict[str, Any]]:
        results = []
        if not query:
            return results
        q = query.lower().strip()
        
        cleaned = query
        for prefix in ["SUSP-", "SUSP_", "PERSON-", "PERSON_", "ACC-", "ACC_", "PHONE-", "PHONE_"]:
            if cleaned.upper().startswith(prefix):
                cleaned = cleaned[len(prefix):]
        q_clean = cleaned.replace("-", " ").replace("_", " ").lower().strip()

        for n, attr in self.graph.nodes(data=True):
            matched = False
            n_str = str(n).lower()
            if q == n_str or q in n_str or (q_clean and q_clean in n_str):
                matched = True
            
            if not matched:
                for k, v in attr.items():
                    if isinstance(v, str):
                        v_lower = v.lower()
                        if q in v_lower or (q_clean and len(q_clean) >= 3 and q_clean in v_lower):
                            matched = True
                            break
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str):
                                item_lower = item.lower()
                                if q in item_lower or (q_clean and len(q_clean) >= 3 and q_clean in item_lower):
                                    matched = True
                                    break
                        if matched:
                            break
            if matched:
                results.append({"id": n, **attr})
        return results
        
    def get_stats(self) -> Dict[str, Any]:
        node_types = {}
        edge_types = {}
        for _, d in self.graph.nodes(data=True):
            t = d.get('node_type', 'Unknown')
            node_types[t] = node_types.get(t, 0) + 1
        for _, _, d in self.graph.edges(data=True):
            t = d.get('edge_type', 'Unknown')
            edge_types[t] = edge_types.get(t, 0) + 1
            
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "nodes_by_type": node_types,
            "edges_by_type": edge_types
        }

    def expand_network(self, start_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        One-Click Network Expansion (Auto-Feature 3):
        Expands 1st and 2nd degree connections, computes sub-network metrics,
        and returns the complete induced subgraph.
        """
        actual_id = self.resolve_node_id(start_id) or start_id
        if not self.graph.has_node(actual_id):
            return {"root_node": start_id, "depth": depth, "nodes": [], "edges": [], "total_nodes": 0, "total_edges": 0}

        visited = {actual_id}
        frontier = [actual_id]

        for _ in range(depth):
            next_frontier = []
            for node in frontier:
                neighbors = set(self.graph.neighbors(node)) | set(self.graph.predecessors(node))
                for nbr in neighbors:
                    if nbr not in visited:
                        visited.add(nbr)
                        next_frontier.append(nbr)
            frontier = next_frontier

        sub = self.graph.subgraph(visited)
        nodes = [{"id": n, **attr} for n, attr in sub.nodes(data=True)]
        edges = [{"source": u, "target": v, **attr} for u, v, k, attr in sub.edges(keys=True, data=True)]

        return {
            "root_node": start_id,
            "depth": depth,
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }

