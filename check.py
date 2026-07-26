import csv
import json
from pathlib import Path

EXPECTED = [
    "name", "sku", "status", "quantity", "my_price_cad",
    "official_price_usd", "official_url", "image_url",
]

root = Path(__file__).parent
with (root / "stock.csv").open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    assert reader.fieldnames == EXPECTED, "stock.csv columns changed"
    rows = list(reader)

assert rows, "stock.csv has no products"
for line, row in enumerate(rows, 2):
    assert row["status"] in {"In stock", "Sold", "Keep", "Not in stock"}, f"row {line} has an invalid status"
    assert row["quantity"].isdigit(), f"row {line} has an invalid quantity"
    assert row["official_url"].startswith("https://us.jellycat.com/"), f"row {line} needs an official URL"
    assert not row["image_url"] or row["image_url"].startswith("https://"), f"row {line} has an invalid image URL"
    if row["official_price_usd"]:
        assert float(row["official_price_usd"]) > 0, f"row {line} has an invalid official price"
        assert "/search.php?" not in row["official_url"], f"row {line} price needs an exact official page"

prices = json.loads((root / "official_prices.json").read_text(encoding="utf-8"))
priced_rows = {row["name"]: row for row in rows if row["official_price_usd"]}
assert priced_rows.keys() == prices.keys(), "stock.csv verified prices are out of sync"
for name, price in prices.items():
    assert priced_rows[name]["official_price_usd"] == price["price"], f"{name} has the wrong official price"
    assert priced_rows[name]["official_url"] == price["official_url"], f"{name} has the wrong official URL"

print(f"stock.csv OK: {len(rows)} products")
