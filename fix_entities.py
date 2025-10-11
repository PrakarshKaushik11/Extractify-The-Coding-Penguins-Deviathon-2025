import sys, os, re, json, pandas as pd

IN = sys.argv[1] if len(sys.argv) > 1 else r"D:\The Coding Penguins\data\entities.json"
OUT_DIR = os.path.join(os.path.dirname(IN), "fixed")
os.makedirs(OUT_DIR, exist_ok=True)

NOISE = [
    "admission","apply now","contact us","careers","download",
    "privacy","terms","campus course","course list",
    "mathura campus","noida campus course","home","login","register"
]
ROLE_NORMALIZE = {
    "Vice Chancellor": "Vice-Chancellor",
    "Pro Vice Chancellor": "Pro Vice-Chancellor",
    "Chief Justice": "Chief Justice",
    "Judge": "Judge",
    "Director": "Director",
    "Registrar": "Registrar",
    "Dean": "Dean",
    "Professor": "Professor",
}

def noisy_name(s):
    return (not isinstance(s,str)) or any(t in s.lower() for t in NOISE)

def boiler(sn):
    if not isinstance(sn, str): return True
    s = sn.lower()
    keys = ["admission","careers","contact us","select state","select branch"]
    return sum(k in s for k in keys) >= 2

def fix_url(u):
    if not isinstance(u,str) or not u: return None
    u = u.strip()
    if not re.match(r"^https?://", u): u = "https://" + u.lstrip("/")
    return u

rows = json.load(open(IN, "r", encoding="utf-8"))
df = pd.DataFrame(rows)

# Map expected fields
df["url"]  = df.get("context_url")
df["type"] = df.get("title")
df["type"] = df["type"].map(lambda x: ROLE_NORMALIZE.get(x, x) if isinstance(x,str) else x)
df["url"]  = df["url"].map(fix_url)

# Remove noise
df = df[~df["name"].map(noisy_name)]
df = df[~df["snippet"].map(boiler)]

# Deduplicate
if "score" not in df: df["score"] = 0.0
df = df.sort_values(["name","url","score"], ascending=[True,True,False]) \
       .drop_duplicates(subset=["name","url"], keep="first")

# Save
cols = [c for c in ["name","type","org","url","snippet","score"] if c in df.columns]
OUT_JSON = os.path.join(OUT_DIR, "entities_fixed.json")
OUT_CSV  = os.path.join(OUT_DIR, "entities_fixed.csv")
OUT_JSONL= os.path.join(OUT_DIR, "entities_fixed.jsonl")

os.makedirs(OUT_DIR, exist_ok=True)

df[cols].to_csv(OUT_CSV, index=False, encoding="utf-8")

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(df[cols].to_dict(orient="records"), f, ensure_ascii=False, indent=2)

with open(OUT_JSONL, "w", encoding="utf-8") as f:
    for rec in df[cols].to_dict(orient="records"):
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print("\n✅ Fixed files written to:", OUT_DIR)
print(" -", OUT_JSON)
print(" -", OUT_CSV)
print(" -", OUT_JSONL)
