import pandas as pd
import re
import os

def main():
    # Check if input file exists
    input_file = "sections/iPhone_Used_(US_Spec).xlsx"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    # Load file
    df = pd.read_excel(input_file, header=None)

    # Helper function to check if value is a price
    def is_price(val):
        return bool(re.search(r"\$?\d+", str(val)))

    # Extract price number from string like "$30"
    def extract_price_num(text):
        match = re.search(r"-?\d+", str(text))
        return int(match.group(0)) if match else 0

    # Grade labels
    grade_labels = ["A+", "B+", "B", "C", "D", "HSO/Swap"]

    # Extract storage from model
    def extract_storage(text):
        match = re.search(r"\b(\d+(GB|TB))\b", text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    # Extract lock status
    def extract_lock_status(text):
        if "unlocked" in text.lower():
            return "Unlocked"
        elif "locked" in text.lower():
            return "Locked"
        return "-"

    # Clean model text
    def clean_model(text):
        text = re.sub(r"\b\d+(GB|TB)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\bUnlocked\b|\bLocked\b", "", text, flags=re.IGNORECASE)
        return " ".join(text.strip().split())

    # Init
    records = []
    sno = 1
    current_flex = None
    current_cricket = None

    # Loop
    for idx, row in df.iterrows():
        col0 = str(row[0]).strip()
        col1 = str(row[1]).strip() if pd.notna(row[1]) else ""

        # Detect and store Flex and Cricket modifiers
        if "flex" in col0.lower():
            current_flex = extract_price_num(col0)
        if "cricket" in col1.lower():
            current_cricket = extract_price_num(col1)
        if col0 == "" or col0.lower().startswith("used") or "grade" in col0.lower() or "flex" in col0.lower():
            continue

        # Process data rows with 6 prices
        if all(is_price(row[i]) for i in range(1, 7)):
            storage = extract_storage(col0)
            lock_status = extract_lock_status(col0)
            model = clean_model(col0)

            if model == "0" or model == None:
                continue

            base_prices = []
            for i in range(6):
                price_val = re.sub(r"[^\d.]", "", str(row[i + 1]))
                price_val = float(price_val) if price_val else 0
                base_prices.append(price_val)

                # Base row (no carrier)
                records.append({
                    "S.No": "",
                    "Make": "iPhone",
                    "Model": model,
                    "Storage": storage,
                    "Color": None,
                    "Box Status": "Used",
                    "Activate Status": "Active",
                    "Category": "Cellphone",
                    "Grade": grade_labels[i],
                    "Lock Status": lock_status,
                    "Carrier": None,
                    "Price": price_val
                })
                sno += 1

            if lock_status == "Unlocked":
                current_flex = None
                current_cricket = None

            # For locked phones, apply Flex and Cricket modifiers
            if lock_status == "Locked":
                if current_flex is not None:
                    for i in range(6):
                        records.append({
                            "S.No": "",
                            "Make": "iPhone",
                            "Model": model,
                            "Storage": storage,
                            "Color": None,
                            "Box Status": "Used",
                            "Activate Status": "Active",
                            "Category": "Cellphone",
                            "Grade": grade_labels[i],
                            "Lock Status": "Locked",
                            "Carrier": "Flex",
                            "Price": base_prices[i] + current_flex
                        })
                        sno += 1

                if current_cricket is not None:
                    for i in range(6):
                        records.append({
                            "S.No": "",
                            "Make": "iPhone",
                            "Model": model,
                            "Storage": storage,
                            "Color": None,
                            "Box Status": "Used",
                            "Activate Status": "Active",
                            "Category": "Cellphone",
                            "Grade": grade_labels[i],
                            "Lock Status": "Locked",
                            "Carrier": "Cricket",
                            "Price": base_prices[i] - current_cricket
                        })
                        sno += 1

    # Create output directory
    output_dir = "processed"
    os.makedirs(output_dir, exist_ok=True)

    # Save result
    final_df = pd.DataFrame(records)
    final_df.to_excel("processed/iPhone_Used_Final.xlsx", index=False)

    print("✅ iPhone_Used_Final.xlsx created with clean Lock Status and Carrier column.")

if __name__ == "__main__":
    main()
