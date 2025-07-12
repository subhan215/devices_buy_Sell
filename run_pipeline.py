import pandas as pd
import os
from supabase import create_client
from datetime import date
from pathlib import Path

# STEP 0: Import pipeline stages
from scripts import extractor
from scripts import cleaner
from scripts import filer
from scripts import google_phones
from scripts import ipad
from scripts import iphone_new
from scripts import iphone_used
from scripts import macbook
from scripts import samsung

# STEP 1: Setup Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("❌ SUPABASE_URL and SUPABASE_KEY must be set as environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# STEP 2: Constants
FOLDER_PATH = "processed"
EXPECTED_COLUMNS = [
    "box_status", "category", "make", "model", "storage", "color",
    "grade", "lock_status", "active_status", "carrier", "price", "serial"
]

def clean_column_names(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df

def upload_file(filepath):
    print(f"\n📄 Uploading: {filepath}")
    try:
        df = pd.read_excel(filepath)
        if df.empty:
            print("⚠️ Skipped: Empty file.")
            return

        df = clean_column_names(df)
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = None

        df = df[EXPECTED_COLUMNS]
        df["fetched_at"] = date.today()

        for row in df.to_dict(orient="records"):
            supabase.table("mobile_prices").insert(row).execute()

        print(f"✅ Uploaded {len(df)} rows from {Path(filepath).name}")
    except Exception as e:
        print(f"❌ Error uploading {filepath}: {e}")

def main():
    print("🚀 Starting full Hanggroup pipeline...")

    try:
        extractor.main()
        cleaner.main()
        filer.main()
        iphone_new.main()
        samsung.main()
        ipad.main()
        google_phones.main()
        macbook.main()
        iphone_used.main()
    except Exception as e:
        print(f"❌ Pipeline step failed: {e}")
        return

    print("\n📤 Uploading cleaned files to Supabase...")

    if not os.path.exists(FOLDER_PATH):
        print(f"❌ Folder not found: {FOLDER_PATH}")
        return

    for file in os.listdir(FOLDER_PATH):
        if file.endswith(".xlsx"):
            upload_file(os.path.join(FOLDER_PATH, file))

    print("🎉 All data uploaded successfully.")

if __name__ == "__main__":
    main()
