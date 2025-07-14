import pandas as pd
import os
import psycopg2
from datetime import date, datetime
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

# STEP 1: Setup PostgreSQL connection string
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise EnvironmentError("❌ DATABASE_URL must be set as an environment variable.")

# STEP 2: Constants
FOLDER_PATH = "processed"
EXPECTED_COLUMNS = [
    "box_status", "category", "make", "model", "storage", "color",
    "grade", "lock_status", "active_status", "carrier", "price", "serial_number"
]

def clean_column_names(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df

def extract_date_from_url(url):
    try:
        slug = url.split("/")[-1]  # Get the last part of the URL
        parts = slug.split("-")
        for i in range(len(parts) - 1):
            if parts[i].isdigit() and parts[i+1].isalpha():
                day = int(parts[i])
                month_str = parts[i+1].capitalize()
                year = date.today().year
                return datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y").date()
    except Exception as e:
        print(f"⚠️ Could not extract date from URL: {e}")
    return date.today()

def upload_file(filepath, fetched_at):
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
        df["fetched_at"] = fetched_at  # ✅ Use extracted date

        # Connect to Postgres and insert
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        for row in df.to_dict(orient="records"):
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['%s'] * len(row))
            values = tuple(row.values())

            sql = f"INSERT INTO devices ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Uploaded {len(df)} rows from {Path(filepath).name}")
    except Exception as e:
        print(f"❌ Error uploading {filepath}: {e}")

def main():
    print("🚀 Starting full Hanggroup pipeline...")

    try:
        url = extractor.main()
        fetched_at = extract_date_from_url(url)
        print(f"📅 Extracted fetched_at date from URL: {fetched_at}")

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

    print("\n📤 Uploading cleaned files to PostgreSQL...")

    if not os.path.exists(FOLDER_PATH):
        print(f"❌ Folder not found: {FOLDER_PATH}")
        return

    for file in os.listdir(FOLDER_PATH):
        if file.endswith(".xlsx"):
            upload_file(os.path.join(FOLDER_PATH, file), fetched_at)

    print("🎉 All data uploaded successfully.")

if __name__ == "__main__":
    main()
