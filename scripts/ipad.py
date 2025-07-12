import pandas as pd
import re

# Load file
df = pd.read_excel("sections/ipad.xlsx", header=None)

# Helper to extract clean price
def clean_price(val):
    match = re.search(r"-?\d+(?:\.\d+)?", str(val))
    return float(match.group(0)) if match else None

# Initialization
records = []

for _, row in df.iterrows():
    first_col = str(row[0]).strip()
    if not first_col.lower().startswith("ipad"):
        continue

    # Skip rows with less than 6 price cells
    if row[1:7].isnull().all():
        continue

    prices = [clean_price(p) for p in row[1:7]]

    # Parse model parts
    parts = first_col.split()
    make = "iPad"
    storage = ""
    carrier = ""
    model_parts = []

    for part in parts:
        if "gb" in part.lower() or "tb" in part.lower():
            storage = part.upper()
        elif part.lower() == "verizon":
            carrier = "Verizon"
        else:
            model_parts.append(part)

    model = " ".join(model_parts).replace("Verizon", "").strip()

    # Construct records
    record_list = [
        {"box_status": "Sealed", "category": "tablets", "make": make, "model": model, "storage": storage,
         "color": "", "grade": "", "lock_status": "", "active_status": "N/A", "carrier": carrier, "price": prices[0]},
        {"box_status": "Unsealed", "category": "tablets", "make": make, "model": model, "storage": storage,
         "color": "", "grade": "", "lock_status": "", "active_status": "Active", "carrier": carrier, "price": prices[1]},
        {"box_status": "Unsealed", "category": "tablets", "make": make, "model": model, "storage": storage,
         "color": "", "grade": "A", "lock_status": "", "active_status": "Active", "carrier": carrier, "price": prices[2]},
        {"box_status": "Unsealed", "category": "tablets", "make": make, "model": model, "storage": storage,
         "color": "", "grade": "B", "lock_status": "", "active_status": "Active", "carrier": carrier, "price": prices[3]},
        {"box_status": "Unsealed", "category": "tablets", "make": make, "model": model, "storage": storage,
         "color": "", "grade": "B+", "lock_status": "", "active_status": "Active", "carrier": carrier, "price": prices[3]},
        {"box_status": "Unsealed", "category": "tablets", "make": make, "model": model, "storage": storage,
         "color": "", "grade": "C", "lock_status": "", "active_status": "Active", "carrier": carrier, "price": prices[4]}
    ]

    # Only append records with valid price
    for rec in record_list:
        if rec["price"] is not None:
            records.append(rec)

# Save output
final_df = pd.DataFrame(records)
final_df = final_df[[
    "box_status", "category", "make", "model", "storage", "color",
    "grade", "lock_status", "active_status", "carrier", "price"
]]

final_df.to_excel("processed/ipad_Final.xlsx", index=False)
print(f"✅ Saved {len(final_df)} records to ../processed/ipad_Final.xlsx")
