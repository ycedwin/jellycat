import csv
from pathlib import Path

EXPECTED = [
    "name", "sku", "status", "quantity", "my_price_cad",
    "official_price_usd", "official_url", "image_url",
]

with Path(__file__).with_name("stock.csv").open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    assert reader.fieldnames == EXPECTED, "stock.csv columns changed"
    rows = list(reader)

assert rows, "stock.csv has no products"
for line, row in enumerate(rows, 2):
    assert row["status"] in {"In stock", "Sold", "Keep", "Not in stock"}, f"row {line} has an invalid status"
    assert row["quantity"].isdigit(), f"row {line} has an invalid quantity"
    assert row["official_url"].startswith("https://us.jellycat.com/"), f"row {line} needs an official URL"
    assert not row["image_url"] or row["image_url"].startswith("https://"), f"row {line} has an invalid image URL"

print(f"stock.csv OK: {len(rows)} products")
