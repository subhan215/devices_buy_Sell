import pandas as pd
import re
import os

def main():
    # Check if input file exists
    input_file = "sections/iphone_new_(us_spec).xlsx"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    # Load file
    df = pd.read_excel(input_file, header=None)

    # Helper functions
    def is_price(val):
        if isinstance(val, str):
            return re.search(r"\$\d+", val)
        elif isinstance(val, (int, float)):
            return not pd.isna(val)
        return False

    def extract_price_num(text):
        match = re.search(r"\$(-?\d+)", str(text))
        return int(match.group(1)) if match else 0

    def extract_storage(text):
        match = re.search(r"(\d+GB|\d+TB)", text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    def extract_color(text):
        known_colors = ["Red", "Desert", "Black", "White", "Gold", "Silver", "Blue", "Green", "Purple", "Yellow"]
        for color in known_colors:
            if color.lower() in text.lower():
                return color
        return "Other"

    def clean_model(text):
        text = re.sub(r"iPhone", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(\d+GB|\d+TB)\b", "", text)
        text = re.sub(rf"\b({'|'.join(['Red', 'Desert', 'Black', 'White', 'Gold', 'Silver', 'Blue', 'Green', 'Purple', 'Yellow', 'Others'])})\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # Initialization
    records = []
    current_lock_status = None
    current_flex = None
    current_cricket = None
    current_red = None

    # Main loop
    for idx, row in df.iterrows():
        name = str(row[0]) if pd.notna(row[0]) else ""
        price1 = row[1]
        price2 = row[2]
        col4 = str(row[3]) if pd.notna(row[3]) else ""

        # Always update flex/cricket modifiers if found
        if "flex" in col4.lower():
            current_flex = extract_price_num(col4)
        if "cricket" in col4.lower():
            current_cricket = extract_price_num(col4)
        if "red" in col4.lower():
            current_red = extract_price_num(col4)

        if not name.lower().startswith("iphone"):
            continue

        # Update lock status from headers
        if "unlocked" in name.lower():
            current_lock_status = "Unlocked"
            continue
        elif "locked" in name.lower():
            current_lock_status = "Locked"
            current_red = None
            continue

        # Process valid iPhone rows with prices
        if is_price(price1) and is_price(price2):
            storage = extract_storage(name)
            color = extract_color(name)
            model = clean_model(name)
            base_price1 = extract_price_num(price1)
            base_price2 = extract_price_num(price2)

            # Base rows
            records.append({
                "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                "Color": color, "Box Status": "Sealed", "Activate Status": "Non-Active",
                "Category": "Cellphone", "Grade": "", "Lock Status": current_lock_status,
                "Carrier": None, "Price": base_price1
            })

            records.append({
                "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                "Color": color, "Box Status": "Unsealed", "Activate Status": "Active",
                "Category": "Cellphone", "Grade": "", "Lock Status": current_lock_status,
                "Carrier": None, "Price": base_price2
            })

            if current_lock_status == "Unlocked":
                current_flex = None
                current_cricket = None
                if current_red is not None:
                    records.append({
                        "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                        "Color": "Red", "Box Status": "Sealed", "Activate Status": "Non-Active",
                        "Category": "Cellphone", "Grade": "", "Lock Status": "Unlocked",
                        "Carrier": None, "Price": base_price1 - current_red
                    })
                    records.append({
                        "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                        "Color": "Red", "Box Status": "Unsealed", "Activate Status": "Active",
                        "Category": "Cellphone", "Grade": "", "Lock Status": "Unlocked",
                        "Carrier": None, "Price": base_price2 - current_red
                    })

            # Apply modifiers only if in Locked mode
            if current_lock_status == "Locked":
                if current_flex is not None:
                    records.append({
                        "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                        "Color": color, "Box Status": "Sealed", "Activate Status": "Non-Active",
                        "Category": "Cellphone", "Grade": "", "Lock Status": "Locked",
                        "Carrier": "Flex", "Price": base_price1 + current_flex
                    })
                    records.append({
                        "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                        "Color": color, "Box Status": "Unsealed", "Activate Status": "Active",
                        "Category": "Cellphone", "Grade": "", "Lock Status": "Locked",
                        "Carrier": "Flex", "Price": base_price2 + current_flex
                    })

                if current_cricket is not None:
                    records.append({
                        "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                        "Color": color, "Box Status": "Sealed", "Activate Status": "Non-Active",
                        "Category": "Cellphone", "Grade": "", "Lock Status": "Locked",
                        "Carrier": "Cricket", "Price": base_price1 - current_cricket
                    })
                    records.append({
                        "S.No": "", "Make": "iPhone", "Model": model, "Storage": storage,
                        "Color": color, "Box Status": "Unsealed", "Activate Status": "Active",
                        "Category": "Cellphone", "Grade": "", "Lock Status": "Locked",
                        "Carrier": "Cricket", "Price": base_price2 - current_cricket
                    })

    # Create output directory
    output_dir = "processed"
    os.makedirs(output_dir, exist_ok=True)

    # Save output
    final_df = pd.DataFrame(records)
    final_df.to_excel("processed/iPhone_New_Final.xlsx", index=False)

    print("✅ iPhone_New_Final.xlsx created with Carrier column and clean Lock Status.")

if __name__ == "__main__":
    main()
