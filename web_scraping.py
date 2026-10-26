
# STEP 1: IMPORT REQUIRED LIBRARIES

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import matplotlib.pyplot as plt

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_FILE = "scraped_books.csv"
MAX_PAGES = 50
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 0.2

print("Project configuration completed.")

# STEP 3: TEST WEBSITE CONNECTION

url = "https://books.toscrape.com/"

try:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    print("Website connected successfully!")
    print("Status Code:", response.status_code)

except requests.RequestException as error:
    print("Website connection failed:", error)


soup = BeautifulSoup(response.text, "html.parser")

books = []

 
# STEP 4: AUTOMATED MULTI-PAGE DATA EXTRACTION

all_books = []

for page in range(1, MAX_PAGES + 1):
    page_url = BASE_URL.format(page)

    try:
        page_response = requests.get(
            page_url,
            timeout=REQUEST_TIMEOUT
        )
        page_response.raise_for_status()

        page_soup = BeautifulSoup(
            page_response.text,
            "html.parser"
        )

        book_items = page_soup.select("article.product_pod")

        if not book_items:
            print(f"No books found on page {page}. Stopping.")
            break

        for book in book_items:
            title_tag = book.select_one("h3 a")
            price_tag = book.select_one(".price_color")
            availability_tag = book.select_one(".availability")

            if title_tag and price_tag and availability_tag:
                all_books.append({
                    "Title": title_tag.get("title", "").strip(),
                    "Price": price_tag.get_text(strip=True),
                    "Availability": availability_tag.get_text(
                        " ", strip=True
                    )
                })

        print(
            f"Page {page}: {len(book_items)} books collected"
        )

        time.sleep(REQUEST_DELAY)

    except requests.RequestException as error:
        print(f"Error on page {page}: {error}")
        break

print("\nTotal books collected:", len(all_books))
# STEP 5: DATA CLEANING AND PROCESSING

df = pd.DataFrame(all_books)

print("\n--- BEFORE CLEANING ---")
print("Dataset shape:", df.shape)
print("Missing values:\n", df.isnull().sum())
print("Duplicate rows:", df.duplicated().sum())

# Clean text columns
df["Title"] = df["Title"].astype(str).str.strip()
df["Availability"] = df["Availability"].astype(str).str.strip()

# Clean prices and convert them to numbers
df["Price"] = (
    df["Price"]
    .astype(str)
    .str.replace("Â£", "", regex=False)
    .str.replace("£", "", regex=False)
    .str.strip()
)

df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

# Remove invalid and duplicate records
df.dropna(subset=["Title", "Price", "Availability"], inplace=True)
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)

print("\n--- AFTER CLEANING ---")
print("Clean dataset shape:", df.shape)
print("Missing values:\n", df.isnull().sum())
print("Duplicate rows:", df.duplicated().sum())
print("\nFirst 5 cleaned records:")
print(df.head().to_string(index=False))
# STEP 6: SAVE CLEANED DATA TO CSV

OUTPUT_FILE = "scraped_books.csv"

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\n--- DATA EXPORT SUMMARY ---")
print("File saved successfully:", OUTPUT_FILE)
print("Total records saved:", len(df))
print("Total columns:", len(df.columns))
print("Column names:", list(df.columns))
# STEP 7: DATA ANALYSIS

print("\n--- PRICE ANALYSIS ---")
print("Average book price:", round(df["Price"].mean(), 2))
print("Highest book price:", round(df["Price"].max(), 2))
print("Lowest book price:", round(df["Price"].min(), 2))

print("\n--- AVAILABILITY SUMMARY ---")
print(df["Availability"].value_counts())
# STEP 8: PRICE DISTRIBUTION VISUALIZATION

plt.figure(figsize=(10, 6))
plt.hist(df["Price"], bins=20, edgecolor="black")

plt.title("Distribution of Book Prices")
plt.xlabel("Price (£)")
plt.ylabel("Number of Books")

plt.tight_layout()
plt.savefig("book_price_distribution.png", dpi=300)
plt.show()

print("Price distribution chart saved successfully!")