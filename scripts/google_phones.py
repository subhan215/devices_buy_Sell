import pandas as pd
import re
from pathlib import Path

# Load Excel file
df = pd.read_excel("sections/google_phones.xlsx", header=None)

def clean_price(val):
    match = re.search(r"-?\d+(?:\.\d+)?", str(val))
    return float(match.group(0)) if match else None

def extract_storage(text):
    match = re.search(r"\b\d+(GB|TB)\b", text, re.IGNORECASE)
    return match.group(0).upper() if match else ""

def extract_lock_status(text):
    if "unlocked" in text.lower():
        return "Unlocked"
    elif "locked" in text.lower():
        return "Locked"
    return ""

def clean_model_name(text):
    text = re.sub(r"\b\d+(GB|TB)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bUnlocked\b|\bLocked\b", "", text, flags=re.IGNORECASE)
    return " ".join(text.strip().split())

records = []

for _, row in df.iterrows():
    col0 = str(row[0]) if pd.notna(row[0]) else ""
    if "pixel" not in col0.lower():
        continue

    storage = extract_storage(col0)
    lock_status = extract_lock_status(col0)
    model = clean_model_name(col0)

    prices = [clean_price(row[i]) for i in range(1, 5)]
    if all(p is None for p in prices):
        continue

    box_statuses = ["Sealed", "Unsealed", "Unsealed", "Unsealed", "Unsealed"]
    grades = ["", "", "A+", "B+", "B"]
    active_statuses = ["not active", "active", "active", "active", "active"]
    price_values = [
        prices[0],  # Sealed
        prices[1],  # Open
        prices[2],  # A+
        prices[3],  # B+
        prices[3],  # B uses same as B+
    ]

    for i in range(5):
        if price_values[i] is not None:
            records.append({
                "box_status": box_statuses[i],
                "category": "cellphones",
                "make": "Google",
                "model": model,
                "storage": storage,
                "color": "",
                "grade": grades[i],
                "lock_status": lock_status,
                "active_status": active_statuses[i],
                "carrier": "",
                "serial_number": "",
                "price": price_values[i]
            })

# Save to Excel
final_df = pd.DataFrame(records)
final_df = final_df[[  # enforce column order
    "box_status", "category", "make", "model", "storage", "color",
    "grade", "lock_status", "active_status", "carrier", "serial_number", "price"
]]

Path("processed").mkdir(exist_ok=True)
final_df.to_excel("processed/google_Final.xlsx", index=False)

print("✅ Saved to processed/google_Final.xlsx")
