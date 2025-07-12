import pandas as pd
import re
from pathlib import Path

# Load the MacBook Excel file
df = pd.read_excel("sections/macbook.xlsx", header=None)

def clean_price(val):
    match = re.search(r"-?\d+(?:\.\d+)?", str(val))
    return float(match.group(0)) if match else None

def extract_serials(text):
    return re.findall(r"\b[A-Z0-9]{5,}\b", text)

records = []
current_model_header = ""

# Loop through each row in the DataFrame
for _, row in df.iterrows():
    first_col = str(row[0]) if pd.notna(row[0]) else ""

    # Update current model header
    if "macbook" in first_col.lower() and not re.search(r"\b[A-Z0-9]{5,}\b", first_col):
        current_model_header = first_col.strip()
        continue

    # Skip non-data rows
    if any("228, 228, 228" in str(cell) or "224, 233, 243" in str(cell) for cell in row):
        continue
    if "-" not in first_col:
        continue

    # Split storage and serial part
    try:
        storage_part, serial_part = map(str.strip, first_col.split("-", 1))
    except ValueError:
        continue
    storage = storage_part.upper()
    serials = extract_serials(serial_part)
    if not serials:
        continue

    # Try 2nd to 5th columns, else 3rd to 6th
    possible_price_sets = [
        [row[1], row[2], row[3], row[4]],
        [row[2], row[3], row[4], row[5]]
    ]
    prices = None
    for price_set in possible_price_sets:
        if all(clean_price(p) is not None for p in price_set):
            prices = [clean_price(p) for p in price_set]
            break

    if not prices:
        continue

    model = current_model_header.strip()
    box_statuses = ["Sealed", "Unsealed", "Unsealed", "Unsealed", "Unsealed"]
    grades = ["", "", "A", "B", "mdm"]
    active_statuses = ["not active", "active", "active", "active", "active"]

    for serial in serials:
        records.append({
            "box_status": "Sealed",
            "category": "laptops",
            "make": "Apple",
            "model": model,
            "storage": storage,
            "color": "",
            "grade": "",
            "lock_status": "",
            "active_status": "not active",
            "carrier": "",
            "serial_number": serial,
            "price": prices[0]
        })
        records.append({
            "box_status": "Unsealed",
            "category": "laptops",
            "make": "Apple",
            "model": model,
            "storage": storage,
            "color": "",
            "grade": "",
            "lock_status": "",
            "active_status": "active",
            "carrier": "",
            "serial_number": serial,
            "price": prices[1]
        })
        records.append({
            "box_status": "Unsealed",
            "category": "laptops",
            "make": "Apple",
            "model": model,
            "storage": storage,
            "color": "",
            "grade": "A",
            "lock_status": "",
            "active_status": "active",
            "carrier": "",
            "serial_number": serial,
            "price": prices[2]
        })
        records.append({
            "box_status": "Unsealed",
            "category": "laptops",
            "make": "Apple",
            "model": model,
            "storage": storage,
            "color": "",
            "grade": "B",
            "lock_status": "",
            "active_status": "active",
            "carrier": "",
            "serial_number": serial,
            "price": prices[2]  # Same as A
        })
        records.append({
            "box_status": "Unsealed",
            "category": "laptops",
            "make": "Apple",
            "model": model,
            "storage": storage,
            "color": "",
            "grade": "mdm",
            "lock_status": "",
            "active_status": "active",
            "carrier": "",
            "serial_number": serial,
            "price": prices[3]
        })


# Create DataFrame and reorder columns
final_df = pd.DataFrame(records)
final_df = final_df[[ 
    "box_status", "category", "make", "model", "storage", "color",
    "grade", "lock_status", "active_status", "carrier", "serial_number", "price"
]]

# Save to Excel
Path("processed").mkdir(exist_ok=True)
output_path = "processed/macbook_Final.xlsx"
final_df.to_excel(output_path, index=False)

print("✅ Saved to processed/macbook_Final.xlsx")
