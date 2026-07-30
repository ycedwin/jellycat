#!/usr/bin/env python3
"""Fetch Soft Toys / Animals / Bag Charms from us.jellycat.com and append new listings only."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import cloudscraper
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
OUTPUT = ROOT / "official-catalog.json"
# Fixed USD→CAD rate from marketplace spreadsheet (edit here if FX changes).
USD_TO_CAD = 1.41
PROFIT_MARKUP = 1.2

CATEGORIES = [
    ("Soft Toys", "https://us.jellycat.com/collections/all-soft-toys"),
    ("Animals", "https://us.jellycat.com/animals"),
    ("Bag Charms", "https://us.jellycat.com/bags-bag-charms/bag-charms"),
]

PRICE_RE = re.compile(r"\$([0-9]+(?:\.[0-9]{2})?)\s*USD", re.I)
SKU_RE = re.compile(r"/products/\d+/[^/]+/([A-Za-z0-9_-]+?)(?:__|\.)")
BOOK_RE = re.compile(r"\b(book|board book)\b", re.I)


def is_book(item: dict) -> bool:
    sku = item.get("sku", "")
    name = item.get("name", "")
    url = item.get("official_url", "")
    if sku.startswith(("BK", "BB44", "SETBK", "SETBB")):
        return True
    if BOOK_RE.search(name) or "-book" in url or "_book" in url:
        return True
    return False


def load_catalog() -> dict:
    if OUTPUT.exists():
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    return {
        "fx_usd_to_cad": USD_TO_CAD,
        "profit_markup": PROFIT_MARKUP,
        "updated_at": None,
        "products": [],
    }


def money(value: float) -> str:
    return f"{value:.2f}"


def normalize_url(href: str) -> str:
    parsed = urlparse(urljoin("https://us.jellycat.com", href))
    path = parsed.path.rstrip("/") + "/"
    return f"https://us.jellycat.com{path}"


def parse_card(card, category: str) -> dict | None:
    link = card.select_one("a.card-figure__link[href], a.card-title[href], a[href]")
    if not link:
        return None
    url = normalize_url(link.get("href", ""))
    if not url.startswith("https://us.jellycat.com/"):
        return None
    skip = ("/cart", "/login", "/wishlist", "/search", "/page=", "/collections/", "/animals?", "/bags-")
    if any(part in url for part in ("/cart", "/login", "/wishlist", "/search.php")):
        return None
    # Category index pages only
    if url.rstrip("/").count("/") <= 3 and url.rstrip("/").endswith(
        ("animals", "bag-charms", "bags-bag-charms", "all-soft-toys", "shop-all")
    ):
        return None

    label = " ".join((link.get("aria-label") or "").split())
    title_el = card.select_one(".card-title, h3, h4")
    name = (title_el.get_text(" ", strip=True) if title_el else "") or label.split(",")[0].strip()
    name = re.sub(r"\s+", " ", name).strip(" ,")
    if not name:
        return None

    price_match = PRICE_RE.search(label) or PRICE_RE.search(card.get_text(" ", strip=True))
    if not price_match:
        return None
    usd = float(price_match.group(1))

    img = card.select_one("img.card-image[src], img.lazyload[src], img[src]")
    image = ""
    sku = ""
    if img:
        image = img.get("src") or ""
        srcset = img.get("data-srcset") or img.get("srcset") or ""
        # Prefer a mid-size CDN image when available.
        for candidate in re.findall(r"(https://cdn11\.bigcommerce\.com/[^\s,]+)", srcset):
            if "/640w/" in candidate or "/500x" in candidate or "/400x" in candidate:
                image = candidate
                break
        sku_match = SKU_RE.search(image) or SKU_RE.search(srcset)
        if sku_match:
            sku = sku_match.group(1)

    cad = usd * USD_TO_CAD
    return {
        "name": name,
        "sku": sku,
        "category": category,
        "official_url": url,
        "image_url": image,
        "official_price_usd": money(usd),
        "official_price_cad": money(cad),
        "profit_price_cad": money(cad * PROFIT_MARKUP),
        "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def next_page_url(current_url: str, soup: BeautifulSoup) -> str | None:
    for a in soup.select(".pagination a[href], .pagination-item a[href]"):
        label = a.get_text(strip=True).casefold()
        rel = (a.get("rel") or [""])[0].casefold() if isinstance(a.get("rel"), list) else str(a.get("rel") or "").casefold()
        if label == "next" or rel == "next":
            return urljoin(current_url, a.get("href"))
    return None


def fetch_category(scraper, category: str, base_url: str) -> list[dict]:
    products = []
    seen = set()
    url = base_url
    page = 1

    while url and page <= 80:
        response = scraper.get(url, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        before = len(products)
        for card in soup.select("li.product"):
            item = parse_card(card, category)
            if not item or is_book(item) or item["official_url"] in seen:
                continue
            seen.add(item["official_url"])
            products.append(item)
        print(f"  {category} page {page}: +{len(products) - before} (total {len(products)})")
        if len(products) == before:
            break
        url = next_page_url(url, soup)
        page += 1
        if url:
            time.sleep(0.7)

    return products


def main() -> None:
    catalog = load_catalog()
    catalog["fx_usd_to_cad"] = USD_TO_CAD
    catalog["profit_markup"] = PROFIT_MARKUP
    existing = {item["official_url"]: item for item in catalog.get("products", []) if not is_book(item)}

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}
    )
    discovered = []
    for category, url in CATEGORIES:
        print(f"Fetching {category}…")
        discovered.extend(fetch_category(scraper, category, url))

    added = 0
    for item in discovered:
        if is_book(item):
            continue
        url = item["official_url"]
        if url in existing:
            # Append-only: keep first-seen record; merge category tags if needed.
            old = existing[url]
            cats = {c.strip() for c in old.get("category", "").split("|") if c.strip()}
            cats.add(item["category"])
            old["category"] = " | ".join(sorted(cats))
            continue
        existing[url] = item
        added += 1

    products = sorted(existing.values(), key=lambda item: item["name"].casefold())
    catalog["products"] = products
    catalog["updated_at"] = datetime.now(timezone.utc).isoformat()
    catalog["counts"] = {
        "total": len(products),
        "added_this_run": added,
        "fetched_this_run": len(discovered),
    }
    OUTPUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.name}: {len(products)} products ({added} new)")


if __name__ == "__main__":
    main()
