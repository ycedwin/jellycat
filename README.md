# My Jellycat Shelf

A static personal stock catalog designed for GitHub Pages.

## Update stock

Open `stock.csv` on GitHub, click the pencil icon, make a change, and commit it.

- `status`: use `In stock`, `Sold`, `Keep`, or `Not in stock`
- `quantity`: number currently owned
- `my_price_cad`: your selling price in CAD
- `official_price_usd`: price shown on the official US Jellycat site
- Add one row for each new design

The website updates a few minutes after the commit. The **Edit stock** button on the published site opens the same GitHub editor.

To rebuild `stock.csv` from the private marketplace spreadsheet, run:

```sh
python3 build_stock.py
```

The rebuild keeps manually verified product images and generates a name-based image lookup for the remaining designs. Similar product names can occasionally return the wrong variation; add a verified entry to `KNOWN` in `build_stock.py` to override one.

Verified official USD prices and exact product links live in `official_prices.json`. Products with ambiguous names, retired pages, or no displayed official price remain `Not listed` rather than using an estimate.

The `source_*` columns preserve every column from the latest matching row in the private marketplace export. They include costs, profit, status, and owner/type data and are intentionally public in `stock.csv`.

## Transactions and profit

Sales are saved privately in the current browser. Revenue, total cost, and profit are calculated automatically.

Use **Export backup** to download the transaction history before clearing browser data or moving to another device. Use **Import backup** to restore it. Browser storage does not sync between devices.

## Publish with GitHub Pages

1. Create a GitHub repository and upload this folder.
2. Open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select `main`, `/ (root)`, then **Save**.

GitHub will show the public site URL when deployment finishes.

## Check the CSV

Run:

```sh
python3 check.py
```

The original marketplace spreadsheet is intentionally excluded from the public catalog because it contains private cost and profit information.
