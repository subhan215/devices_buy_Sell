import pandas as pd
import re
import os

def main():
    # Check if input file exists
    input_file = "sections/samsung_phones.xlsx"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    # Load file
    df = pd.read_excel(input_file, header=None)

    # Helper to extract numeric price
    def clean_price(val):
        match = re.search(r"-?\d+(?:\.\d+)?", str(val))
        return float(match.group(0)) if match else None

    # Constants
    known_carriers = ["Verizon", "Xfinity", "Sprint", "T-Mobile", "AT&T"]
    grade_slots = [
        (0, [""]),          # Sealed (no grade)
        (1, ["A+"]),
        (2, ["B", "B+"]),
        (3, ["C"]),
        (4, ["D", "D+"]),
        (5, ["E"]),
    ]

    records = []

    # Loop over each row in the Excel file
    for _, row in df.iterrows():
        first_col = str(row[0]).strip()

        # Skip empty rows
        if not first_col or first_col.isnumeric():
            continue

        # Skip styled header rows (gray)
        if any("228, 228, 228" in str(cell) or "224, 233, 243" in str(cell) for cell in row):
            continue

        parts = first_col.split()
        make = "Samsung"
        storage = ""
        lock_status = "Locked"  # Default to Locked
        carriers = []
        model_parts = []

        for part in parts:
            low = part.lower()
            if "gb" in low or "tb" in low:
                storage = part.upper()
            elif low == "unlocked":
                lock_status = "Unlocked"
            elif part in known_carriers:
                carriers.append(part)
            elif any(car in part for car in known_carriers):
                for car in known_carriers:
                    if car in part:
                        carriers.append(car)
                        part = part.replace(car, "")
            else:
                model_parts.append(part)

        if not carriers:
            carriers = [""]

        model = " ".join(model_parts).strip()
        price_values = [clean_price(row[i]) for i in range(1, 7)]

        for i, grades in grade_slots:
            if i >= len(price_values):
                continue
            price = price_values[i]
            if price is None:
                continue

            for carrier in carriers:
                for grade in grades:
                    record = {
                        "box_status": "Sealed" if grade == "" else "Unsealed",
                        "category": "cellphones",
                        "make": make,
                        "model": model,
                        "storage": storage,
                        "color": "",
                        "grade": grade,
                        "lock_status": lock_status,
                        "active_status": "",
                        "carrier": carrier,
                        "price": price
                    }
                    records.append(record)

    # Create output directory
    output_dir = "processed"
    os.makedirs(output_dir, exist_ok=True)

    # Define final column order
    final_df = pd.DataFrame(records)
    final_df = final_df[[
        "box_status", "category", "make", "model", "storage", "color",
        "grade", "lock_status", "active_status", "carrier", "price"
    ]]

    # Save output
    final_df.to_excel("processed/samsung_Final.xlsx", index=False)
    print(f"✅ Saved {len(final_df)} records to processed/samsung_Final.xlsx")

if __name__ == "__main__":
    main()
