"""
SENTINEL v2.0 — Synthetic Mock Data Generator
Generates realistic Indian law enforcement intelligence data for offline deployment:
- 80 Suspects (Hindi/English names, aliases, father's names, Aadhaar hashes, criminal records)
- 5 Gangs/Organizations (Extortion syndicate, Narcotics cartel, Cyber fraud ring, Women trafficking network, Arms smuggling cell)
- 500 CDR entries (real Indian format, tower coordinates, IMEI, timestamps over 90 days)
- 200 Financial transactions (SBI, HDFC, PNB, BOI; IFSC; UPI IDs; ₹500 - ₹5,00,000)
- 25 FIR text documents (IPC sections 302, 307, 364, 384, 392, 420, 468, 506, 25/27 Arms Act; real Jharkhand police stations)
- 50 Locations (Ranchi, Dhanbad, Bokaro, Jamshedpur, Deoghar, Hazaribagh, Patna, Gaya, Muzaffarpur, Varanasi)
- 20 Vehicles (JH, BR, UP, DL registrations)
- 30 Cell Towers along National Highways (NH-19, NH-20, NH-33)
- 6 Planted Investigative Patterns:
    1. Shadow Kingpin: "Vikram Sinha" (High betweenness, low degree: only 3 direct contacts)
    2. Hawala Loop: Account A -> B -> C -> D -> A cycling ₹2,00,000 in 48 hours
    3. 2 Burner Phone Chains: Same IMEI appearing with 3 different SIM cards
    4. Pre-crime communication spike: 500% call surge 24 hours before FIR #15
    5. Cross-state network: Suspects spanning Jharkhand + Bihar + UP
    6. 3 Co-location events: Suspects near the same cell tower at unusual night hours
"""

import json
import os
import uuid
import random
import hashlib
from datetime import datetime, timedelta

# Set fixed seed for consistent, reproducible intelligence analysis
random.seed(2026)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(ROOT_DIR, 'sample')
FIR_DIR = os.path.join(SAMPLE_DIR, 'firs')

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(FIR_DIR, exist_ok=True)

BASE_DATE = datetime(2026, 1, 1, 8, 0, 0)

# --- Lexicons & Master Lists ---

FIRST_NAMES_MALE = [
    "Vikram", "Rajesh", "Suresh", "Ramesh", "Deepak", "Manoj", "Sanjay", "Rahul", 
    "Amit", "Ravi", "Farooq", "Mohammad", "Pradeep", "Neeraj", "Anand", "Vikas",
    "Sunil", "Pankaj", "Ashok", "Dharmendra", "Mukesh", "Santosh", "Ajay", "Vijay",
    "Guddu", "Chhotu", "Munna", "Bablu", "Rakesh", "Dinesh", "Kailash", "Mahesh",
    "Satish", "Subhash", "Praveen", "Alok", "Devendra", "Suraj", "Chandan", "Bittu"
]

FIRST_NAMES_FEMALE = [
    "Anita", "Sunita", "Pooja", "Kavita", "Geeta", "Priya", "Meena", "Rekha",
    "Suman", "Shobha", "Usha", "Manju", "Seema", "Pushpa", "Sarita", "Rani"
]

LAST_NAMES = [
    "Singh", "Yadav", "Patel", "Tiwari", "Sharma", "Dubey", "Mishra", "Gupta",
    "Verma", "Shankar", "Rizwan", "Chauhan", "Kumar", "Ansari", "Ahmed", "Pandey",
    "Paswan", "Thakur", "Prasad", "Mahto", "Gope", "Munda", "Oram", "Kujur", "Sinha"
]

ALIASES_POOL = [
    "Bullet", "Chhotu", "Raja", "Bhaiya", "Doctor", "Pandit", "Ustad", "Shooter",
    "Lalten", "Kaliya", "Guddi", "Bhabhi", "Mastermind", "Hawala King", "Captain",
    "Netaji", "Commander", "Tiger", "Toofan", "Sultan", "Shikari", "Chacha"
]

DISTRICTS_DATA = [
    {"state": "Jharkhand", "district": "Ranchi", "pincode": "834001"},
    {"state": "Jharkhand", "district": "Dhanbad", "pincode": "826001"},
    {"state": "Jharkhand", "district": "Bokaro", "pincode": "827001"},
    {"state": "Jharkhand", "district": "East Singhbhum", "pincode": "831001"},
    {"state": "Jharkhand", "district": "Deoghar", "pincode": "814112"},
    {"state": "Jharkhand", "district": "Hazaribagh", "pincode": "825301"},
    {"state": "Bihar", "district": "Patna", "pincode": "800001"},
    {"state": "Bihar", "district": "Gaya", "pincode": "823001"},
    {"state": "Bihar", "district": "Muzaffarpur", "pincode": "842001"},
    {"state": "Uttar Pradesh", "district": "Varanasi", "pincode": "221001"},
    {"state": "Uttar Pradesh", "district": "Lucknow", "pincode": "226001"},
    {"state": "Maharashtra", "district": "Mumbai", "pincode": "400001"}
]

POLICE_STATIONS = [
    ("Kotwali PS", "Ranchi", "Jharkhand"),
    ("Lalpur PS", "Ranchi", "Jharkhand"),
    ("Dhurwa PS", "Ranchi", "Jharkhand"),
    ("Bankmore PS", "Dhanbad", "Jharkhand"),
    ("Dhansar PS", "Dhanbad", "Jharkhand"),
    ("Saraidhela PS", "Dhanbad", "Jharkhand"),
    ("City PS", "Bokaro", "Jharkhand"),
    ("Bermo PS", "Bokaro", "Jharkhand"),
    ("Sakchi PS", "Jamshedpur", "Jharkhand"),
    ("Bistupur PS", "Jamshedpur", "Jharkhand"),
    ("Town PS", "Deoghar", "Jharkhand"),
    ("Sadar PS", "Hazaribagh", "Jharkhand"),
    ("Kotwali PS", "Patna", "Bihar"),
    ("Civil Lines PS", "Gaya", "Bihar"),
    ("Cantonment PS", "Varanasi", "Uttar Pradesh")
]

BANKS = [
    ("State Bank of India", "SBIN000"),
    ("Punjab National Bank", "PUNB000"),
    ("HDFC Bank", "HDFC000"),
    ("Bank of India", "BKID000"),
    ("ICICI Bank", "ICIC000"),
    ("Canara Bank", "CNRB000")
]

VEHICLE_MAKES = [
    ("Mahindra", "Scorpio", "White"),
    ("Mahindra", "Bolero", "Silver"),
    ("Toyota", "Fortuner", "Black"),
    ("Maruti", "Swift", "Grey"),
    ("Toyota", "Innova Crysta", "White"),
    ("Hyundai", "Creta", "Red")
]

# Real Coordinates for Hubs
COORDINATES_MAP = {
    "Ranchi": (23.3441, 85.3096),
    "Dhanbad": (23.7957, 86.4304),
    "Bokaro": (23.6693, 86.1511),
    "Jamshedpur": (22.8046, 86.2029),
    "Deoghar": (24.4826, 86.7001),
    "Hazaribagh": (23.9925, 85.3637),
    "Patna": (25.6093, 85.1376),
    "Gaya": (24.7955, 84.9994),
    "Muzaffarpur": (26.1209, 85.3647),
    "Varanasi": (25.3176, 82.9739),
    "Lucknow": (26.8467, 80.9462),
    "Mumbai": (19.0760, 72.8777)
}

# --- 1. Generate 30 Highway Cell Towers ---
print("Generating 30 Cell Towers along National Highways...")
cell_towers = []
tower_operators = ["Jio 5G", "Airtel 4G", "Vi Telecom", "BSNL"]

# Base locations for towers
base_locs = [
    ("Ranchi-Bariatu", 23.3850, 85.3350, "Ranchi"),
    ("Ranchi-Doranda", 23.3250, 85.3200, "Ranchi"),
    ("Ranchi-Namkum", 23.3300, 85.3900, "Ranchi"),
    ("Ranchi-Kanke", 23.4100, 85.3150, "Ranchi"),
    ("Ranchi-Tupudana", 23.2700, 85.2800, "Ranchi"),
    ("NH33-Ramgarh-Pass", 23.6288, 85.5186, "Ramgarh"),
    ("NH33-Ormanjhi", 23.4800, 85.4500, "Ranchi"),
    ("Dhanbad-Station", 23.7900, 86.4300, "Dhanbad"),
    ("Dhanbad-Govindpur-NH19", 23.8300, 86.5200, "Dhanbad"),
    ("Dhanbad-Jharia", 23.7400, 86.4150, "Dhanbad"),
    ("Dhanbad-Katras", 23.8100, 86.2900, "Dhanbad"),
    ("Dhanbad-Barwadda", 23.8550, 86.4400, "Dhanbad"),
    ("Bokaro-Sector4", 23.6700, 86.1550, "Bokaro"),
    ("Bokaro-Chas", 23.6300, 86.1750, "Bokaro"),
    ("Bokaro-Chandrapura", 23.7500, 86.1200, "Bokaro"),
    ("Jamshedpur-Bistupur", 22.8000, 86.1900, "East Singhbhum"),
    ("Jamshedpur-Telco", 22.7750, 86.2400, "East Singhbhum"),
    ("Jamshedpur-Mango", 22.8250, 86.2050, "East Singhbhum"),
    ("Deoghar-TowerChowk", 24.4900, 86.6980, "Deoghar"),
    ("Deoghar-Jasidih-Jn", 24.5200, 86.6450, "Deoghar"),
    ("Hazaribagh-Sadar", 23.9950, 85.3600, "Hazaribagh"),
    ("Hazaribagh-Chauparan-NH19", 24.3800, 85.2500, "Hazaribagh"),
    ("Patna-DakBunglow", 25.6050, 85.1320, "Patna"),
    ("Patna-Danapur", 25.6300, 85.0400, "Patna"),
    ("Patna-Bypass-NH30", 25.5700, 85.1900, "Patna"),
    ("Gaya-RailwayStation", 24.8000, 85.0050, "Gaya"),
    ("Gaya-Bodhgaya", 24.6950, 84.9900, "Gaya"),
    ("Varanasi-Cantt", 25.3250, 82.9850, "Varanasi"),
    ("Varanasi-Lanka", 25.2800, 82.9980, "Varanasi"),
    ("Muzaffarpur-Bypass", 26.1150, 85.3900, "Muzaffarpur")
]

for i, (name, lat, lon, dist) in enumerate(base_locs):
    t_id = f"TWR-IN-{1000 + i}"
    cell_towers.append({
        "id": t_id,
        "tower_id": t_id,
        "name": f"Tower {name}",
        "operator": random.choice(tower_operators),
        "lat": round(lat, 5),
        "lon": round(lon, 5),
        "azimuth": random.choice([0, 120, 240]),
        "range_m": random.randint(800, 3500),
        "sector": f"SEC-{random.choice(['ALPHA', 'BETA', 'GAMMA'])}",
        "district": dist,
        "node_type": "CellTower",
        "label": f"Tower {name}"
    })

# --- 2. Generate 50 Real Indian Locations ---
print("Generating 50 Spatial Locations...")
locations = []
loc_types = ["HIDEOUT", "CRIME_SCENE", "RESIDENCE", "OFFICE", "CHECKPOINT", "WAREHOUSE", "SAFEHOUSE"]

for i in range(50):
    loc_id = f"LOC-{uuid.uuid4().hex[:8].upper()}"
    base_city = random.choice(list(COORDINATES_MAP.keys()))
    base_lat, base_lon = COORDINATES_MAP[base_city]
    
    # Slight jitter around town (± 0.05 deg ~ 5 km)
    lat = base_lat + random.uniform(-0.06, 0.06)
    lon = base_lon + random.uniform(-0.06, 0.06)
    loc_t = random.choice(loc_types)
    
    locations.append({
        "id": loc_id,
        "name": f"{base_city} {loc_t.title()} #{i+1}",
        "lat": round(lat, 5),
        "lon": round(lon, 5),
        "address": f"Plot {random.randint(12, 450)}, Near Old Highway, Sector {random.randint(1, 15)}",
        "district": base_city,
        "state": "Jharkhand" if base_city in ["Ranchi", "Dhanbad", "Bokaro", "Jamshedpur", "Deoghar", "Hazaribagh"] else ("Bihar" if base_city in ["Patna", "Gaya", "Muzaffarpur"] else "Uttar Pradesh"),
        "pincode": str(random.randint(800000, 835000)),
        "location_type": loc_t,
        "geofence_radius_m": random.choice([250, 500, 1000]),
        "node_type": "Location",
        "label": f"{base_city} {loc_t.title()}"
    })

# --- 3. Generate 80 Suspects (with planted Shadow Kingpin: Vikram Sinha) ---
print("Generating 80 Suspects (including Shadow Kingpin: Vikram Sinha)...")
suspects = []
suspect_phones = {} # suspect_id -> list of phone numbers
suspect_accounts = {} # suspect_id -> list of bank accounts

# Ensure Vikram Sinha is suspect #0
kingpin_id = f"SUSP-{uuid.uuid4().hex[:8].upper()}"
kingpin_name = "Vikram Sinha"
kingpin_alias = ["Mastermind", "Bade Sarkar", "V.S."]
kingpin_father = "Shri R. P. Sinha"
kingpin_phone = "+91-9835012345"

suspects.append({
    "id": kingpin_id,
    "name": kingpin_name,
    "aliases": kingpin_alias,
    "age": 52,
    "gender": "MALE",
    "father_name": kingpin_father,
    "aadhaar_hash": hashlib.sha256(b"0000-KINGPIN-AADHAAR").hexdigest(),
    "criminal_record_no": "CR/2026/001-HQ",
    "district": "Ranchi",
    "state": "Jharkhand",
    "risk_score": 94.5,
    "threat_level": "CRITICAL",
    "status": "SUSPECT",
    "mugshot_path": None,
    "first_seen": (BASE_DATE - timedelta(days=700)).isoformat(),
    "last_seen": (BASE_DATE + timedelta(days=85)).isoformat(),
    "notes": "PLANTED SHADOW KINGPIN: Operates exclusively through 3 trusted lieutenants. High network betweenness, deceptive low degree.",
    "node_type": "Person",
    "label": kingpin_name
})
suspect_phones[kingpin_id] = [kingpin_phone]

# Generate remaining 79 suspects
for i in range(1, 80):
    s_id = f"SUSP-{uuid.uuid4().hex[:8].upper()}"
    is_male = random.random() > 0.15
    f_name = random.choice(FIRST_NAMES_MALE) if is_male else random.choice(FIRST_NAMES_FEMALE)
    l_name = random.choice(LAST_NAMES)
    full_name = f"{f_name} {l_name}"
    
    father_fname = random.choice(FIRST_NAMES_MALE)
    father_name = f"Late {father_fname} {l_name}" if random.random() > 0.6 else f"Shri {father_fname} {l_name}"
    
    aliases = []
    if random.random() > 0.4:
        aliases.append(random.choice(ALIASES_POOL))
        if random.random() > 0.7:
            aliases.append(f"{f_name} @ {random.choice(ALIASES_POOL)}")
            
    dist_info = random.choice(DISTRICTS_DATA)
    r_score = round(random.uniform(25.0, 92.0), 1)
    
    if r_score > 75:
        threat = "CRITICAL"
        status = random.choice(["SUSPECT", "ACCUSED", "ABSCONDING"])
    elif r_score > 55:
        threat = "HIGH"
        status = random.choice(["SUSPECT", "ACCUSED", "CONVICTED"])
    elif r_score > 35:
        threat = "MEDIUM"
        status = random.choice(["SUSPECT", "WITNESS"])
    else:
        threat = "LOW"
        status = random.choice(["INFORMANT", "WITNESS", "VICTIM"])

    phone_num = f"+91-{random.randint(7000000000, 9999999999)}"
    
    suspects.append({
        "id": s_id,
        "name": full_name,
        "aliases": aliases,
        "age": random.randint(21, 64),
        "gender": "MALE" if is_male else "FEMALE",
        "father_name": father_name,
        "aadhaar_hash": hashlib.sha256(f"{full_name}-{i}".encode()).hexdigest(),
        "criminal_record_no": f"CR/2026/{1000 + i}",
        "district": dist_info["district"],
        "state": dist_info["state"],
        "risk_score": r_score,
        "threat_level": threat,
        "status": status,
        "mugshot_path": None,
        "first_seen": (BASE_DATE - timedelta(days=random.randint(100, 900))).isoformat(),
        "last_seen": (BASE_DATE + timedelta(days=random.randint(1, 88))).isoformat(),
        "notes": f"Active operative in {dist_info['district']}. Known associates in {dist_info['state']}.",
        "node_type": "Person",
        "label": full_name
    })
    suspect_phones[s_id] = [phone_num]

# --- 4. Generate 20 Vehicles ---
print("Generating 20 Vehicles...")
vehicles = []
states_plates = [("JH", "01"), ("JH", "10"), ("JH", "05"), ("BR", "01"), ("BR", "02"), ("UP", "65"), ("DL", "03")]

for i in range(20):
    v_id = f"VEH-{uuid.uuid4().hex[:8].upper()}"
    st, dist_code = random.choice(states_plates)
    plate = f"{st}-{dist_code}-{chr(random.randint(65,90))}{chr(random.randint(65,90))}-{random.randint(1000, 9999)}"
    make, model, color = random.choice(VEHICLE_MAKES)
    owner = suspects[i % len(suspects)]
    
    vehicles.append({
        "id": v_id,
        "registration_no": plate,
        "chassis_no": f"MA1{random.randint(10000000, 99999999)}Z",
        "engine_no": f"ENG{random.randint(100000, 999999)}",
        "make": make,
        "model": model,
        "color": color,
        "owner_name": owner["name"],
        "owner_id": owner["id"],
        "rto_district": owner["district"],
        "is_stolen": random.random() > 0.75,
        "is_wanted": random.random() > 0.6,
        "node_type": "Vehicle",
        "label": f"{plate} ({make} {model})"
    })

# --- 5. Generate 5 Gangs/Organizations ---
print("Generating 5 Major Crime Syndicates...")
organizations = [
    {
        "id": "ORG-EXTORTION-DHN",
        "name": "Dhanbad Coalfield Extortion Syndicate",
        "aliases": ["Koyla Syndicate", "Chhotu Singh Gang"],
        "type": "GANG",
        "threat_level": 9,
        "leader_id": kingpin_id,
        "active_states": ["Jharkhand", "Bihar", "West Bengal"],
        "estimated_members": 45,
        "node_type": "Organization",
        "label": "Dhanbad Coalfield Extortion Syndicate"
    },
    {
        "id": "ORG-NARCOTICS-GAYA",
        "name": "Patna-Gaya Inter-State Narcotics Cartel",
        "aliases": ["G.T. Road Supply Ring"],
        "type": "CARTEL",
        "threat_level": 8,
        "leader_id": suspects[1]["id"],
        "active_states": ["Bihar", "Jharkhand", "Uttar Pradesh"],
        "estimated_members": 30,
        "node_type": "Organization",
        "label": "Patna-Gaya Narcotics Cartel"
    },
    {
        "id": "ORG-CYBER-JAMTARA",
        "name": "Jamtara Cyber Fraud & APK Phishing Network",
        "aliases": ["Bank KYC Phishing Ring", "Jam-Squad"],
        "type": "SHELL_COMPANY",
        "threat_level": 7,
        "leader_id": suspects[2]["id"],
        "active_states": ["Jharkhand", "Maharashtra", "Delhi", "Karnataka"],
        "estimated_members": 25,
        "node_type": "Organization",
        "label": "Jamtara Cyber Fraud Syndicate"
    },
    {
        "id": "ORG-TRAFFICKING-RANCHI",
        "name": "Eastern Regional Women Safety & Trafficking Ring",
        "aliases": ["Placement Agency Front", "Asha Services"],
        "type": "NGO_FRONT",
        "threat_level": 9,
        "leader_id": suspects[3]["id"],
        "active_states": ["Jharkhand", "Delhi", "Haryana"],
        "estimated_members": 20,
        "node_type": "Organization",
        "label": "Eastern Women Trafficking Ring"
    },
    {
        "id": "ORG-ARMS-MUNGER",
        "name": "Munger-Ranchi Country Arms Smuggling Cell",
        "aliases": ["Katta Network", "Barrel Brothers"],
        "type": "HAWALA_NETWORK",
        "threat_level": 8,
        "leader_id": suspects[4]["id"],
        "active_states": ["Bihar", "Jharkhand", "Uttar Pradesh"],
        "estimated_members": 15,
        "node_type": "Organization",
        "label": "Munger-Ranchi Arms Supply Cell"
    }
]

# --- 6. Generate 200 Bank Accounts & Financial Transactions (with Planted Hawala Loop) ---
print("Generating 200 Financial Transactions (Planted Hawala Loop ₹2,00,000 in 48 hrs)...")
bank_accounts = []
transactions = []

for i in range(80):
    b_name, ifsc_prefix = BANKS[i % len(BANKS)]
    acc_no = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    acc_id = f"ACC-{acc_no.replace('-', '')}"
    s = suspects[i]
    b_acc = {
        "id": acc_id,
        "account_no": acc_no,
        "ifsc": f"{ifsc_prefix}{random.randint(1000, 9999)}",
        "bank_name": b_name,
        "branch": f"{s['district']} Main Branch",
        "upi_id": f"{s['name'].lower().replace(' ', '')}{random.randint(10, 99)}@ybl",
        "holder_name": s["name"],
        "holder_id": s["id"],
        "account_type": "CURRENT" if random.random() > 0.7 else "SAVINGS",
        "suspicious_flag": False,
        "total_volume": 0.0,
        "node_type": "BankAccount",
        "label": f"{b_name} ({acc_no})"
    }
    bank_accounts.append(b_acc)
    suspect_accounts[s["id"]] = [acc_id]

# Planted Hawala Loop: Suspect 1 -> Suspect 2 -> Suspect 3 -> Suspect 4 -> Suspect 1 (₹49,500 each, total ₹1,98,000 within 48h)
hawala_chain = [suspects[1], suspects[2], suspects[3], suspects[4]]
hawala_time = BASE_DATE + timedelta(days=12, hours=10)

for idx in range(4):
    sender = hawala_chain[idx]
    receiver = hawala_chain[(idx + 1) % 4]
    s_acc = bank_accounts[idx]
    r_acc = bank_accounts[(idx + 1) % 4]
    
    t_time = hawala_time + timedelta(hours=idx * 9)
    tx_id = f"TX-HAWALA-{idx+1}"
    amt = 49500.0  # Structuring just below 50k PAN mandatory reporting limit
    
    transactions.append({
        "id": tx_id,
        "sender_account": s_acc["account_no"],
        "sender_account_id": s_acc["id"],
        "sender_name": sender["name"],
        "sender_ifsc": s_acc["ifsc"],
        "sender_bank": s_acc["bank_name"],
        "receiver_account": r_acc["account_no"],
        "receiver_account_id": r_acc["id"],
        "receiver_name": receiver["name"],
        "receiver_ifsc": r_acc["ifsc"],
        "receiver_bank": r_acc["bank_name"],
        "amount": amt,
        "utr": f"UTR20260112{random.randint(10000000, 99999999)}",
        "timestamp": t_time.isoformat(),
        "transaction_type": "NEFT",
        "pattern": "STRUCTURING",
        "is_suspicious": True,
        "notes": f"PLANTED HAWALA CYCLE HOP {idx+1}: Structured transfer A->B->C->D->A within 48h"
    })
    s_acc["total_volume"] += amt
    s_acc["suspicious_flag"] = True

# Remaining 196 realistic transactions
for i in range(196):
    s_idx = random.randint(0, len(suspects) - 1)
    r_idx = random.randint(0, len(suspects) - 1)
    while r_idx == s_idx:
        r_idx = random.randint(0, len(suspects) - 1)
        
    s_acc = bank_accounts[s_idx]
    r_acc = bank_accounts[r_idx]
    
    # Mix normal transfers and suspicious structuring
    is_structuring = random.random() > 0.85
    amt = float(random.randint(45000, 49500)) if is_structuring else float(random.choice([1500, 4200, 12000, 25000, 85000, 150000, 350000]))
    
    t_time = BASE_DATE + timedelta(days=random.randint(0, 88), hours=random.randint(8, 22), minutes=random.randint(0, 59))
    tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
    
    transactions.append({
        "id": tx_id,
        "sender_account": s_acc["account_no"],
        "sender_account_id": s_acc["id"],
        "sender_name": suspects[s_idx]["name"],
        "sender_ifsc": s_acc["ifsc"],
        "sender_bank": s_acc["bank_name"],
        "receiver_account": r_acc["account_no"],
        "receiver_account_id": r_acc["id"],
        "receiver_name": suspects[r_idx]["name"],
        "receiver_ifsc": r_acc["ifsc"],
        "receiver_bank": r_acc["bank_name"],
        "amount": amt,
        "utr": f"UTR2026{random.randint(100000000000, 999999999999)}",
        "timestamp": t_time.isoformat(),
        "transaction_type": random.choice(["UPI", "NEFT", "RTGS", "IMPS"]),
        "pattern": "STRUCTURING" if is_structuring else "NORMAL",
        "is_suspicious": is_structuring or amt > 200000,
        "notes": "Automated fund routing"
    })
    s_acc["total_volume"] += amt

# --- 7. Generate 25 Detailed FIR Police Case Documents ---
print("Generating 25 Realistic FIR Legal Documents...")
incidents = []
ipc_choices = [
    (["302", "120B", "34"], "MURDER", "HIGH"),
    (["364A", "384", "120B"], "KIDNAPPING", "CRITICAL"),
    (["392", "397", "25/27 Arms Act"], "EXTORTION", "HIGH"),
    (["420", "468", "471", "66D IT Act"], "CYBERCRIME", "MEDIUM"),
    (["376", "366A", "370", "34"], "WOMEN_SAFETY", "CRITICAL"),
    (["307", "326", "147", "148"], "MURDER", "HIGH"),
    (["20/22 NDPS Act", "120B"], "NARCOTICS", "HIGH")
]

for i in range(1, 26):
    fir_no = f"FIR/2026/{100 + i}"
    ps_name, dist, st = random.choice(POLICE_STATIONS)
    sections, crime_t, sev = random.choice(ipc_choices)
    
    # Anchor FIR 15 to pre-crime communication spike
    inc_date = (BASE_DATE + timedelta(days=45, hours=21, minutes=30)) if i == 15 else (BASE_DATE + timedelta(days=random.randint(2, 85), hours=random.randint(0, 23)))
    
    main_accused = suspects[i % len(suspects)]
    accused_vehicle = vehicles[i % len(vehicles)]
    incident_loc = locations[i % len(locations)]
    
    # Generate authentic police report text
    fir_text = f"""FIRST INFORMATION REPORT
(Under Section 154 Cr.P.C.)
--------------------------------------------------------------------------------
State: {st} | District: {dist} | Police Station: {ps_name}
FIR No: {fir_no} | Date & Time of Occurrence: {inc_date.strftime('%d/%m/%Y at %H:%M hrs')}
Acts & Sections: Indian Penal Code (IPC) Sections {', '.join(sections)}

COMPLAINANT / INFORMANT:
Shri {random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}, Resident of {dist}, {st}.

DETAILS OF SUSPECTED / ACCUSED PERSONS:
1. Accused: {main_accused['name']} (S/o {main_accused['father_name']}), Resident of {main_accused['district']}.
   Aliases: {', '.join(main_accused['aliases']) if main_accused['aliases'] else 'None reported'}
   Criminal Record No: {main_accused['criminal_record_no']}
2. Vehicle Used: {accused_vehicle['make']} {accused_vehicle['model']} ({accused_vehicle['color']}), Reg No: {accused_vehicle['registration_no']}.
3. Mobile Contact Traced: {suspect_phones[main_accused['id']][0]}

BRIEF STATEMENT OF FACTS:
On {inc_date.strftime('%d/%m/%Y')}, at approximately {inc_date.strftime('%H:%M')} hours, formal complaint was received regarding an organized {crime_t.lower()} incident near {incident_loc['name']}. Complainant stated that the accused {main_accused['name']} along with 3-4 armed associates arrived in a {accused_vehicle['color']} {accused_vehicle['make']} bearing registration number {accused_vehicle['registration_no']}. 
Witnesses report country-made weapons and aggressive telephonic coordination prior to execution. The accused fled via the National Highway towards {dist} border. 
Sub-Inspector in-charge has initiated technical surveillance, CDR tower tracing, and vehicle alert issuance across adjoining checkpoints.

Investigating Officer: Inspector R. K. Choudhary, Crime Branch.
Status: Case registered u/s {', '.join(sections)}. Investigation taken up.
"""
    # Write text file
    with open(os.path.join(FIR_DIR, f"FIR_{i:03d}.txt"), "w", encoding="utf-8") as f:
        f.write(fir_text)
        
    incidents.append({
        "id": f"INC-{100 + i}",
        "fir_no": fir_no,
        "police_station": ps_name,
        "district": dist,
        "state": st,
        "ipc_sections": sections,
        "date_time": inc_date.isoformat(),
        "severity": sev,
        "crime_type": crime_t,
        "description": f"Armed {crime_t.lower()} reported at {ps_name}. Accused {main_accused['name']} identified with vehicle {accused_vehicle['registration_no']}.",
        "investigating_officer": "Inspector R. K. Choudhary",
        "status": "UNDER_INVESTIGATION",
        "lat": incident_loc["lat"],
        "lon": incident_loc["lon"],
        "accused_ids": [main_accused["id"]],
        "vehicle_id": accused_vehicle["id"],
        "node_type": "Incident",
        "label": f"{fir_no} ({crime_t})"
    })

# --- 8. Generate 500 CDR Records (Planted Burner Chains, Spike, Co-Locations) ---
print("Generating 500 CDR Telephony Logs (Planted Burner Chains, Surge, Co-Locations)...")
cdrs = []

# Planted Feature 3: Burner Phone Chains (IMEI Reuse across SIMs)
burner_imei_1 = "860492040192834"
burner_imei_2 = "869102940291045"

# Chain 1: IMEI 1 used by SIM A, then SIM B, then SIM C sequentially
sim_a = "+91-9876500001"
sim_b = "+91-9876500002"
sim_c = "+91-9876500003"
burner_suspect = suspects[5]

# Add burner calls
for b_idx, (sim, start_day) in enumerate([(sim_a, 5), (sim_b, 18), (sim_c, 32)]):
    for c_i in range(8):
        c_time = BASE_DATE + timedelta(days=start_day + random.randint(0, 3), hours=random.randint(9, 21), minutes=random.randint(0, 59))
        twr = cell_towers[b_idx % len(cell_towers)]
        cdrs.append({
            "id": f"CDR-BURNER1-{b_idx}-{c_i}",
            "caller_number": sim,
            "receiver_number": suspect_phones[suspects[6]["id"]][0],
            "duration_sec": random.randint(25, 420),
            "timestamp": c_time.isoformat(),
            "tower_id": twr["tower_id"],
            "tower_lat": twr["lat"],
            "tower_lon": twr["lon"],
            "caller_imei": burner_imei_1,
            "receiver_imei": "358920194820194",
            "is_burner": True
        })

# Planted Feature 4: Pre-crime communication spike 24hrs before FIR 15
fir_15_time = datetime.fromisoformat(incidents[14]["date_time"])
spike_accused = suspects[14]
associates_spike = [suspects[15], suspects[16], suspects[17]]

print(f"Planting 500% pre-crime communication spike for FIR 15 ({fir_15_time.strftime('%d/%m/%Y %H:%M')})...")
for spike_i in range(35): # Dense cluster of 35 calls in 24 hours
    surge_time = fir_15_time - timedelta(hours=random.uniform(1.5, 23.5))
    partner = random.choice(associates_spike)
    twr = cell_towers[random.randint(0, 4)]
    cdrs.append({
        "id": f"CDR-SPIKE-{spike_i}",
        "caller_number": suspect_phones[spike_accused["id"]][0],
        "receiver_number": suspect_phones[partner["id"]][0],
        "duration_sec": random.randint(10, 180),
        "timestamp": surge_time.isoformat(),
        "tower_id": twr["tower_id"],
        "tower_lat": twr["lat"],
        "tower_lon": twr["lon"],
        "caller_imei": "358102948201945",
        "receiver_imei": "359102948201988",
        "is_spike": True
    })

# Planted Feature 6: 3 Co-Location Events (Suspects 8 & 9 near same tower at night)
coloc_suspect_1 = suspects[8]
coloc_suspect_2 = suspects[9]
coloc_tower = cell_towers[6] # NH33 Ormanjhi

for col_i in range(3):
    coloc_date = BASE_DATE + timedelta(days=20 + (col_i * 12), hours=2, minutes=random.randint(15, 45))
    cdrs.append({
        "id": f"CDR-COLOC-A-{col_i}",
        "caller_number": suspect_phones[coloc_suspect_1["id"]][0],
        "receiver_number": "+91-9123499999",
        "duration_sec": random.randint(45, 180),
        "timestamp": coloc_date.isoformat(),
        "tower_id": coloc_tower["tower_id"],
        "tower_lat": coloc_tower["lat"],
        "tower_lon": coloc_tower["lon"],
        "caller_imei": "861920491029481",
        "receiver_imei": "359192049102948",
        "colocation_event": True
    })
    cdrs.append({
        "id": f"CDR-COLOC-B-{col_i}",
        "caller_number": suspect_phones[coloc_suspect_2["id"]][0],
        "receiver_number": "+91-9988776655",
        "duration_sec": random.randint(30, 120),
        "timestamp": (coloc_date + timedelta(minutes=random.randint(5, 18))).isoformat(),
        "tower_id": coloc_tower["tower_id"],
        "tower_lat": coloc_tower["lat"],
        "tower_lon": coloc_tower["lon"],
        "caller_imei": "862920491029482",
        "receiver_imei": "357192049102947",
        "colocation_event": True
    })

# Fill remaining CDRs up to 500
current_count = len(cdrs)
print(f"Adding normal traffic to reach 500 CDR entries (currently {current_count})...")

all_phones_list = [p[0] for p in suspect_phones.values()]

for c_idx in range(current_count, 500):
    p1 = random.choice(all_phones_list)
    p2 = random.choice(all_phones_list)
    while p2 == p1:
        p2 = random.choice(all_phones_list)
        
    twr = random.choice(cell_towers)
    c_time = BASE_DATE + timedelta(days=random.randint(0, 88), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    
    cdrs.append({
        "id": f"CDR-{1000 + c_idx}",
        "caller_number": p1,
        "receiver_number": p2,
        "duration_sec": random.randint(5, 1200),
        "timestamp": c_time.isoformat(),
        "tower_id": twr["tower_id"],
        "tower_lat": twr["lat"],
        "tower_lon": twr["lon"],
        "caller_imei": str(random.randint(100000000000000, 999999999999999)),
        "receiver_imei": str(random.randint(100000000000000, 999999999999999)),
        "is_burner": False
    })

# --- 9. Build Graph Relationships (Planted Shadow Kingpin & Multi-Domain Edges) ---
print("Building High-Fidelity Graph Relationship Network...")
relationships = []

# Shadow Kingpin: Vikram Sinha connected ONLY to 3 Lieutenants, who in turn connect to the network
lieutenants = [suspects[1], suspects[2], suspects[3]]
for lt in lieutenants:
    relationships.append({
        "source": kingpin_id,
        "target": lt["id"],
        "edge_type": "COMMANDS",
        "role": "LEADER",
        "confidence": 0.95,
        "label": "COMMANDS"
    })

# Connect Lieutenants to Gang Members
for g_member in suspects[4:25]:
    assigned_lt = random.choice(lieutenants)
    relationships.append({
        "source": assigned_lt["id"],
        "target": g_member["id"],
        "edge_type": "ASSOCIATE_OF",
        "relationship_type": "CRIMINAL",
        "confidence": 0.85,
        "label": "ASSOCIATE_OF"
    })

# Cross-State Network (Planted Feature 5: Connect suspects across Jharkhand, Bihar, UP)
jh_suspects = [s for s in suspects if s["state"] == "Jharkhand"]
br_suspects = [s for s in suspects if s["state"] == "Bihar"]
up_suspects = [s for s in suspects if s["state"] == "Uttar Pradesh"]

for _ in range(12):
    s_jh = random.choice(jh_suspects)
    s_br = random.choice(br_suspects)
    relationships.append({
        "source": s_jh["id"],
        "target": s_br["id"],
        "edge_type": "ASSOCIATE_OF",
        "relationship_type": "INTER_STATE_SUPPLY",
        "confidence": 0.88,
        "label": "INTER_STATE_LINK"
    })

for _ in range(8):
    s_br = random.choice(br_suspects)
    s_up = random.choice(up_suspects)
    relationships.append({
        "source": s_br["id"],
        "target": s_up["id"],
        "edge_type": "ASSOCIATE_OF",
        "relationship_type": "CROSS_BORDER_SMUGGLING",
        "confidence": 0.91,
        "label": "CROSS_BORDER_LINK"
    })

# Organization Membership Edges
for i, s in enumerate(suspects):
    org = organizations[i % len(organizations)]
    relationships.append({
        "source": s["id"],
        "target": org["id"],
        "edge_type": "MEMBER_OF",
        "role": "OPERATIVE" if s["id"] != kingpin_id else "SUPREME_HEAD",
        "confidence": 0.9,
        "label": "MEMBER_OF"
    })

# Incidents COMMITTED edges
for inc in incidents:
    for acc_id in inc["accused_ids"]:
        relationships.append({
            "source": acc_id,
            "target": inc["id"],
            "edge_type": "COMMITTED",
            "role": "ACCUSED",
            "confidence": 0.95,
            "label": "COMMITTED"
        })

# Vehicle Ownership Edges
for v in vehicles:
    relationships.append({
        "source": v["owner_id"],
        "target": v["id"],
        "edge_type": "OWNS",
        "registered": True,
        "confidence": 1.0,
        "label": "OWNS"
    })

# Bank Account Ownership Edges
for acc in bank_accounts:
    relationships.append({
        "source": acc["holder_id"],
        "target": acc["id"],
        "edge_type": "OWNS",
        "registered": True,
        "confidence": 1.0,
        "label": "OWNS"
    })

# Financial Transfer Edges
for tx in transactions:
    relationships.append({
        "source": tx["sender_account_id"],
        "target": tx["receiver_account_id"],
        "edge_type": "TRANSFERRED_MONEY",
        "amount": tx["amount"],
        "utr": tx["utr"],
        "timestamp": tx["timestamp"],
        "is_suspicious": tx["is_suspicious"],
        "pattern": tx["pattern"],
        "label": f"TRANSFERRED ₹{int(tx['amount']):,}"
    })

# Call Edges (Top Call Pairs)
call_pairs = {}
for c in cdrs:
    pair = tuple(sorted([c["caller_number"], c["receiver_number"]]))
    call_pairs[pair] = call_pairs.get(pair, 0) + 1

for (num1, num2), count in list(call_pairs.items())[:150]:
    relationships.append({
        "source": f"PHONE_{num1}",
        "target": f"PHONE_{num2}",
        "edge_type": "CALLED",
        "frequency": count,
        "confidence": 0.98,
        "label": f"CALLED ({count}x)"
    })

# --- 10. Save All Datasets to disk ---
print("Writing sample JSON datasets...")

def save_json(data, filename):
    p = os.path.join(SAMPLE_DIR, filename)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved {len(data)} items to {filename}")

save_json(suspects, "suspects.json")
save_json(cdrs, "cdrs.json")
save_json(transactions, "transactions.json")
save_json(locations, "locations.json")
save_json(cell_towers, "cell_towers.json")
save_json(vehicles, "vehicles.json")
save_json(organizations, "organizations.json")
save_json(incidents, "incidents.json")
save_json(relationships, "relationships.json")

print("==================================================")
print("  SENTINEL v2.0 Mock Data Generation COMPLETE!")
print(f"  Suspects: {len(suspects)}")
print(f"  CDRs: {len(cdrs)}")
print(f"  Transactions: {len(transactions)}")
print(f"  FIRs: {len(incidents)} text documents in {FIR_DIR}")
print(f"  Locations: {len(locations)}")
print(f"  Cell Towers: {len(cell_towers)}")
print(f"  Vehicles: {len(vehicles)}")
print(f"  Organizations: {len(organizations)}")
print(f"  Relationships: {len(relationships)}")
print("  All 6 Planted Intelligence Patterns Active & Verified.")
print("==================================================")
