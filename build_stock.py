import csv
import re
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
SOURCE = ROOT / "Marketplace - Jellycat.csv"
OUTPUT = ROOT / "stock.csv"

KNOWN = {
    "woodland babe bunny (medium)": {
        "name": "Bashful Woodland Bunny",
        "sku": "CTM3B",
        "official_price_usd": "33.00",
        "official_url": "https://us.jellycat.com/bashful-woodland-bunny/",
        "image_url": "https://modernnaturalbaby.com/cdn/shop/products/BAS3BW_1800x1800_f46254be-879b-449b-9c25-62c1c74c4d45.jpg?v=1679068061",
    },
    "merry mouse": {
        "sku": "MER3M",
        "official_url": "https://us.jellycat.com/merry-mouse/",
        "image_url": "https://cdn11.bigcommerce.com/s-c73x07v66v/images/stencil/1280x1280/products/15703/25655/mer3m__88194.1699063955.jpg?c=1",
    },
    "peanut keychain": {
        "name": "Amuseables Peanut Bag Charm",
        "sku": "APN4BC",
        "official_price_usd": "28.00",
        "official_url": "https://us.jellycat.com/amuseables-peanut-bag-charm/",
        "image_url": "https://i0.wp.com/spencerthorn.com/wp-content/uploads/2024/10/APN4BC__73766.jpg?fit=1000%2C1000&ssl=1",
    },
    "amuseables rose bouquet": {
        "sku": "A2BROSE",
        "official_price_usd": "55.00",
        "official_url": "https://us.jellycat.com/amuseables-rose-bouquet/",
        "image_url": "https://image.floranext.com/instances/lehifloral_com/catalog/product/s/c/screenshot_2025-01-29_at_5.05.10_pm_679ac25dc7549.png.webp?h=700&w=700&r=255&g=255&b=255",
    },
}


def clean(value):
    return re.sub(r"^\s*\d+\|", "", value or "").strip()


def number(value):
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


with SOURCE.open(newline="", encoding="utf-8-sig") as file:
    rows = list(csv.reader(file))

products = {}
for row in rows[3:]:
    row += [""] * (17 - len(row))
    raw_name = clean(row[2])
    if not raw_name:
        continue

    key = raw_name.casefold()
    item = products.setdefault(key, {
        "name": raw_name,
        "sku": "",
        "statuses": [],
        "my_price_cad": "",
        "official_price_usd": "",
        "official_url": "",
        "image_url": "",
    })
    item["statuses"].append(clean(row[10]))
    item["my_price_cad"] = number(row[6]) or item["my_price_cad"]

for key, item in products.items():
    statuses = item.pop("statuses")
    in_stock = statuses.count("2-In stock")
    if in_stock:
        item["status"] = "In stock"
        item["quantity"] = str(in_stock)
    elif "0-Keep" in statuses:
        item["status"] = "Keep"
        item["quantity"] = str(statuses.count("0-Keep"))
    elif statuses and all(status == "1-Sold" for status in statuses):
        item["status"] = "Sold"
        item["quantity"] = "0"
    else:
        item["status"] = "Not in stock"
        item["quantity"] = "0"

    item.update(KNOWN.get(key, {}))
    if not item["official_url"]:
        item["official_url"] = f"https://us.jellycat.com/search.php?search_query={quote_plus(item['name'])}"
    if not item["image_url"]:
        # ponytail: name search can pick a variant; add a curated KNOWN entry when exact matching matters.
        query = quote_plus(f"Jellycat {item['name']}")
        item["image_url"] = f"https://tse2.mm.bing.net/th?q={query}&w=800&h=800&c=7&rs=1&p=0"

fields = [
    "name", "sku", "status", "quantity", "my_price_cad",
    "official_price_usd", "official_url", "image_url",
]
with OUTPUT.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted(products.values(), key=lambda item: item["name"].casefold()))

print(f"Wrote {len(products)} designs to {OUTPUT.name}")
