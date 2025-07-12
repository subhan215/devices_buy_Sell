# Hanggroup Data Extractor

A Python pipeline for extracting, processing, and uploading mobile device pricing data from Hanggroup to Supabase.

## Project Structure

```
devices_buy_Sell/
├── upload_to_supabase.py    # Main pipeline script
├── requirements.txt         # Python dependencies
├── scripts/                 # Individual processing scripts
│   ├── extractor.py        # Extracts data from Hanggroup website
│   ├── cleaner.py          # Cleans raw data
│   ├── filer.py            # Splits data into sections
│   ├── iphone_new.py       # Processes new iPhone data
│   ├── iphone_used.py      # Processes used iPhone data
│   ├── samsung.py          # Processes Samsung data
│   ├── ipad.py             # Processes iPad data
│   ├── macbook.py          # Processes MacBook data
│   └── google_phones.py    # Processes Google Pixel data
└── README.md               # This file
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_KEY="your_supabase_key"
   ```

## Usage

Run the complete pipeline:
```bash
python upload_to_supabase.py
```

Or run individual scripts:
```bash
python scripts/extractor.py
python scripts/cleaner.py
python scripts/filer.py
# etc.
```

## Pipeline Flow

1. **Extractor**: Fetches pricing data from Hanggroup website
2. **Cleaner**: Removes unwanted content and empty rows
3. **Filer**: Splits data into device-specific sections
4. **Device Processors**: Process each device type (iPhone, Samsung, etc.)
5. **Upload**: Uploads processed data to Supabase

## Output

Processed files are saved in the `processed/` directory and then uploaded to the Supabase `mobile_prices` table.

## Data Schema

The final data includes these columns:
- box_status
- category
- make
- model
- storage
- color
- grade
- lock_status
- active_status
- carrier
- price
- serial (for some devices)
- fetched_at (added during upload)
