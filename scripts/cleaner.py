import pandas as pd
import os

def main():
    # Check if input file exists
    input_file = "hanggroup_prices.xlsx"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    # Load the Excel file
    df = pd.read_excel(input_file, header=None)

    # Refined unwanted phrases — removed Xfinity, Verizon unlocked
    unwanted_phrases = [
        "Hanggroup", "Kwun Tong", "Group of", "WhatsApp", "Telegram", "Minor Price Update",
        "Dish Boost", "Fedex", "bulk", "Bank Wire", "PayPal", "China Bank", "USDT",
        "NY", "Florida", "Chicago", "Texas", "Price Update",
        "Room", "Hong Kong", "We DONT", "payment", "model iPads"
        # DO NOT include Verizon/Xfinity/Sprint etc.
    ]

    # Filter function
    def keep_row(row):
        row_text = " ".join(str(cell) for cell in row if pd.notna(cell)).lower()
        return not any(word.lower() in row_text for word in unwanted_phrases)

    # Apply filter
    cleaned_df = df[df.apply(keep_row, axis=1)]

    # Drop fully empty rows
    cleaned_df = cleaned_df.dropna(how="all")

    # Save cleaned output
    cleaned_df.to_excel("hanggroup_prices_cleaned.xlsx", index=False, header=False)

    print("✅ Cleaned file saved as 'hanggroup_prices_cleaned.xlsx'")

if __name__ == "__main__":
    main()
