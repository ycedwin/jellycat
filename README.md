# My Jellycat Shelf

Personal Jellycat stock catalog on GitHub Pages, edited through Google Sheets, plus an official Soft Toys / Animals / Bag Charms browser.

## Links

| | URL |
| --- | --- |
| **Live site** | https://ycedwin.github.io/jellycat/ |
| **Official tab** | https://ycedwin.github.io/jellycat/#official |
| **Repo** | https://github.com/ycedwin/jellycat |
| **Edit stock (Google Sheet)** | https://docs.google.com/spreadsheets/d/1xr_M3_GrhcJzxosVEvrk6IhMysEDxpx1AeZ3_pa4vBk/edit?gid=419836162#gid=419836162 |

## Tabs

### My stock

Reads the published Google Sheet first, then falls back to `stock.csv`.

Required columns for new rows: `name`, `status`, `quantity`, `my_price_cad`.

Optional: `sku`, `official_price_usd`, `official_url`, `image_url` (blank = automatic name image), `source_*`.

### Official listing

Lists Soft Toys, Animals, and Bag Charms from [us.jellycat.com](https://us.jellycat.com/shop-all).

Each card shows:

- product image
- official USD price
- CAD price using fixed FX `1.41`
- profit price = CAD × `1.2`

Profit filters are **dynamic** thirds of the current catalog (labels like `< $42`), so each bucket stays roughly even as prices change.

**Refresh listings** reloads `official-catalog.json` from the site. It does **not** scrape Jellycat in the browser.

## Refresh official catalog (new listings only)

Existing rows are kept as-is. Only missing products are appended.

### Locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python refresh_official_catalog.py
```

Then commit/push `official-catalog.json`, or open the local site and hit **Refresh listings**.

### Daily on GitHub

`.github/workflows/refresh-official-catalog.yml` runs once a day and pushes new products when found. You can also run it from **Actions → Refresh official catalog → Run workflow**.

Change FX or markup in `refresh_official_catalog.py` (`USD_TO_CAD`, `PROFIT_MARKUP`).

## Rebuild stock from marketplace CSV (optional)

```sh
python3 build_stock.py
python3 check.py
```

## Notes

- Not affiliated with or endorsed by Jellycat.
- Product names, images, and official prices belong to their respective owners.
- Sheet, `stock.csv`, and `official-catalog.json` are publicly readable.
