# My Jellycat Shelf

A static personal stock catalog designed for GitHub Pages.

## Update stock

Open `stock.csv` on GitHub, click the pencil icon, make a change, and commit it.

- `status`: use `In stock`, `Sold`, or `Keep`
- `quantity`: number currently owned
- `my_price_cad`: your selling price in CAD
- `official_price_usd`: price shown on the official US Jellycat site
- Add one row for each new design

The website updates a few minutes after the commit. The **Edit stock** button on the published site opens the same GitHub editor.

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
