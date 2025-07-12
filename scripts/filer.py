import pandas as pd
import os

def main():
    # Load the cleaned Excel file
    input_file = "hanggroup_prices_cleaned.xlsx"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    df = pd.read_excel(input_file, header=None)

    # Define the headings we want to split on
    section_headers = [
        "iPhone New (US Spec)",
        "Others",
        "iPad",
        "MacBook",
        "Samsung Phones",
        "Google Phones",
        """iCloud Activation Lock / MDM Configuration Lock / Zip Code SSN Lock 
                        iPhone""",
        "iPhone Used (US Spec)"
    ]

    # Normalize headers to match format in the sheet
    normalized_headers = [header.lower().strip() for header in section_headers]

    # Track where each section starts
    section_indices = {}

    for idx, row in df.iterrows():
        cell_text = str(row[0]).lower().strip()
        if cell_text in normalized_headers:
            section_indices[cell_text] = idx

    # Sort the section starts by index
    sorted_sections = sorted(section_indices.items(), key=lambda x: x[1])

    # Save each section to a new Excel file
    output_dir = "sections"
    os.makedirs(output_dir, exist_ok=True)

    for i, (header, start_idx) in enumerate(sorted_sections):
        end_idx = sorted_sections[i + 1][1] if i + 1 < len(sorted_sections) else len(df)
        section_df = df.iloc[start_idx:end_idx].reset_index(drop=True)
        filename = os.path.join(output_dir, f"{header.replace('/', '_').replace(' ', '_')}.xlsx")
        section_df.to_excel(filename, index=False)

    print("✅ Done! All sections saved separately.")

if __name__ == "__main__":
    main()
