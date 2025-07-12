import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_latest_mailchimp_url():
    print("🚀 Fetching Hanggroup price page...")
    main_url = 'https://www.hanggroup.com/price/'
    response = requests.get(main_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    iframe = soup.select_one('.entry-content iframe')
    if not iframe:
        raise Exception("❌ Mailchimp iframe not found on the page.")
    
    iframe_url = iframe['src']
    print(f"📝 Found Mailchimp URL: {iframe_url}")
    return iframe_url

def fetch_mailchimp_table(url):
    print("🌐 Fetching Mailchimp price list page...")
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, "html.parser")

    # Look for the first <table> that has "iPhone" in any row
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for tr in rows:
            if "iPhone" in tr.get_text():
                # Found the right table. Parse all rows.
                data = []
                for tr in rows:
                    cols = [td.get_text(strip=True).replace("\u3000", "") for td in tr.find_all(["td", "th"])]
                    if any(cols):
                        data.append(cols)
                return data

    raise ValueError("❌ Could not find a pricing table containing 'iPhone'.")

def save_to_excel(data, filename="hanggroup_prices.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, header=False)
    print(f"✅ Saved {len(data)} rows to {filename}")

def main():
    try:
        url = get_latest_mailchimp_url()
        rows = fetch_mailchimp_table(url)
        print(f"✅ Found {len(rows)} rows. Sample:")
        for row in rows[:3]:
            print(row)
        save_to_excel(rows)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
