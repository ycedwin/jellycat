# My Jellycat Shelf

Personal Jellycat stock catalog on GitHub Pages, edited through Google Sheets.

## Links

| | URL |
| --- | --- |
| **Live site** | https://ycedwin.github.io/jellycat/ |
| **Repo** | https://github.com/ycedwin/jellycat |
| **Edit stock (Google Sheet)** | https://docs.google.com/spreadsheets/d/1xr_M3_GrhcJzxosVEvrk6IhMysEDxpx1AeZ3_pa4vBk/edit?gid=419836162#gid=419836162 |

The site loads stock from the published Google Sheet first, then falls back to `stock.csv` in this repo.

## Add or update a listing

1. Open **Edit stock** on the site (or the Google Sheet link above).
2. Add a new row, or change an existing one.
3. Refresh the live site after a few minutes.

### Required columns

| Column | Example | Notes |
| --- | --- | --- |
| `name` | `Amuseables Peanut` | Product name |
| `status` | `In stock` | One of: `In stock`, `Sold`, `Keep`, `Not in stock` |
| `quantity` | `1` | Whole number |
| `my_price_cad` | `50.00` | Your selling price in CAD |

### Optional columns

| Column | Notes |
| --- | --- |
| `sku` | Official SKU if known |
| `official_price_usd` | Verified USD price from [us.jellycat.com](https://us.jellycat.com) |
| `official_url` | Exact product page. If blank, the site uses a Jellycat search link |
| `image_url` | Leave blank for automatic name-based image search. Fill in to override a wrong image |
| `source_*` | Original marketplace columns (cost, GST, profit, type, etc.) |

Do not rename the header row.

## Images and official prices

- **Images:** If `image_url` is empty, the page searches online by `Jellycat + name`. Wrong variants can be fixed by pasting a correct URL into `image_url`.
- **Official prices:** Enter verified USD prices manually in the Sheet. Jellycat has no public price API for live auto-fetch on GitHub Pages.
- Verified prices already researched live in `official_prices.json`.

## Rebuild from marketplace CSV (optional)

```sh
python3 build_stock.py
python3 check.py
```

`Marketplace - Jellycat.csv` stays local and is gitignored. Rebuild overwrites `stock.csv` from that export plus `official_prices.json`.

## Notes

- Not affiliated with or endorsed by Jellycat.
- Product names, images, and official prices belong to their respective owners.
- Sheet and `stock.csv` are publicly readable.
