\
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUT_RESULTS = ROOT / "outputs" / "results"
OUT_FIGURES = ROOT / "outputs" / "figures"
OUT_TABLES = ROOT / "outputs" / "tables"
LOGS = ROOT / "logs"
CHECKPOINTS = ROOT / "checkpoints"
REPRO = ROOT / "reproducibility"

for p in [DATA_RAW, DATA_PROCESSED, OUT_RESULTS, OUT_FIGURES, OUT_TABLES, LOGS, CHECKPOINTS, REPRO]:
    p.mkdir(parents=True, exist_ok=True)

SEED = 19019
N_JOBS = -1
ALPHA = 0.10  # nominal 90% prediction interval
CAL_FRAC = 0.25

WAW_COLLECTION_CSV = (
    "https://data360files.worldbank.org/data360-data/data/WB_WAW/WM_COL_COV.csv"
)
WAW_TREATMENT_CSV = (
    "https://data360files.worldbank.org/data360-data/data/WB_WAW/WM_MSW_TREAT.csv"
)
WORLD_BANK_API = "https://api.worldbank.org/v2"

WDI_INDICATORS = {
    "gdp_ppp_pc": "NY.GDP.PCAP.PP.KD",
    "urban_pct": "SP.URB.TOTL.IN.ZS",
    "population": "SP.POP.TOTL",
    "pop_density": "EN.POP.DNST",
}

PRIMARY_UNIT_PRIORITY = {
    "PT_MSW": 1,
    "PT_POP": 2,
    "PT_HH": 3,
}

STRICT_CONTROLLED_TREATMENTS = {
    "Controlled landfill",
    "Sanitary landfill",
    "Anaerobic digestion (AD)",
    "Composting",
    "Recycling",
    "Incineration",
    "Mechanical biological treatment (MBT)",
    "Refuse-derived fuel (RDF)",
}

PERMISSIVE_EXTRA_TREATMENTS = {
    "Unspecified landfill",
    "Other",
}

INCOME_ORDER = [
    "Low income",
    "Lower middle income",
    "Upper middle income",
    "High income",
]
