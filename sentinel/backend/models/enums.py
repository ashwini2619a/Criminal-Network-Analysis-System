"""
SENTINEL v2.0 — Canonical Enumerations
Defines standard status, severity, crime types, roles, and relationship types
for Indian law enforcement criminal network intelligence analysis.
"""

from enum import Enum

class PersonStatus(str, Enum):
    SUSPECT = "SUSPECT"
    ACCUSED = "ACCUSED"
    CONVICTED = "CONVICTED"
    ABSCONDING = "ABSCONDING"
    WITNESS = "WITNESS"
    VICTIM = "VICTIM"
    INFORMANT = "INFORMANT"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class ThreatLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class LocationType(str, Enum):
    HIDEOUT = "HIDEOUT"
    CRIME_SCENE = "CRIME_SCENE"
    RESIDENCE = "RESIDENCE"
    OFFICE = "OFFICE"
    TOWER = "TOWER"
    CHECKPOINT = "CHECKPOINT"
    BORDER = "BORDER"
    WAREHOUSE = "WAREHOUSE"
    SAFEHOUSE = "SAFEHOUSE"

class OrgType(str, Enum):
    GANG = "GANG"
    CARTEL = "CARTEL"
    TERROR_CELL = "TERROR_CELL"
    SHELL_COMPANY = "SHELL_COMPANY"
    NGO_FRONT = "NGO_FRONT"
    HAWALA_NETWORK = "HAWALA_NETWORK"

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CrimeType(str, Enum):
    MURDER = "MURDER"
    KIDNAPPING = "KIDNAPPING"
    EXTORTION = "EXTORTION"
    NARCOTICS = "NARCOTICS"
    CYBERCRIME = "CYBERCRIME"
    TERRORISM = "TERRORISM"
    WOMEN_SAFETY = "WOMEN_SAFETY"
    FRAUD = "FRAUD"
    ARMS = "ARMS"
    DACOITY = "DACOITY"

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CHARGESHEET_FILED = "CHARGESHEET_FILED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"

class PhoneStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SEIZED = "SEIZED"

class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    WALLET = "WALLET"

class TransactionType(str, Enum):
    NEFT = "NEFT"
    RTGS = "RTGS"
    UPI = "UPI"
    IMPS = "IMPS"
    CASH = "CASH"

class TransactionPattern(str, Enum):
    NORMAL = "NORMAL"
    STRUCTURING = "STRUCTURING"
    LAYERING = "LAYERING"
    ROUND_TRIP = "ROUND_TRIP"

class EvidenceSourceType(str, Enum):
    FIR = "FIR"
    CDR = "CDR"
    BANK_STATEMENT = "BANK_STATEMENT"
    SURVEILLANCE = "SURVEILLANCE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    TIP_OFF = "TIP_OFF"
    FORENSIC = "FORENSIC"

class WeaponType(str, Enum):
    FIREARM = "FIREARM"
    BLADE = "BLADE"
    EXPLOSIVE = "EXPLOSIVE"
    CHEMICAL = "CHEMICAL"
    IMPROVISED = "IMPROVISED"

class WeaponLicenseStatus(str, Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    UNLICENSED = "UNLICENSED"
    SEIZED = "SEIZED"

class SocialPlatform(str, Enum):
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"
    TWITTER = "TWITTER"
    TELEGRAM = "TELEGRAM"
    WHATSAPP = "WHATSAPP"
    SIGNAL = "SIGNAL"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    INVESTIGATOR = "INVESTIGATOR"
    ANALYST = "ANALYST"

class AlertPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class AlertType(str, Enum):
    SHADOW_KINGPIN = "SHADOW_KINGPIN"
    HAWALA_LOOP = "HAWALA_LOOP"
    BURNER_PHONE_CHAIN = "BURNER_PHONE_CHAIN"
    PRE_CRIME_SPIKE = "PRE_CRIME_SPIKE"
    POST_CRIME_SILENCE = "POST_CRIME_SILENCE"
    FINANCIAL_STRUCTURING = "FINANCIAL_STRUCTURING"
    CROSS_STATE_MOVEMENT = "CROSS_STATE_MOVEMENT"
    NEW_GANG_MEMBER = "NEW_GANG_MEMBER"
    COLOCATION_EVENT = "COLOCATION_EVENT"
    EVIDENCE_TAMPERING = "EVIDENCE_TAMPERING"

class CaseStatus(str, Enum):
    NEW = "NEW"
    UNDER_ANALYSIS = "UNDER_ANALYSIS"
    LEADS_GENERATED = "LEADS_GENERATED"
    CHARGESHEET_READY = "CHARGESHEET_READY"
