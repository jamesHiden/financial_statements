# Iranian Listed-Company Financial Statements Pipeline

A Python pipeline that builds a clean, comparable financial-statements database for companies listed on the
Tehran Stock Exchange. It does this by scraping **Codal** (the official disclosure system) and **TSETMC** (market data),
then standardizing everything to a global statement template and converting it to USD.

## Why

Codal filings are HTML tables in Persian, and line-item labels differ between companies and years. Rial figures also
lose comparability quickly because of inflation. This project turns those filings into one schema where
*Revenue*, *Operating Income* or *Total Assets* mean the same thing for every company and every period, in rial and in USD.

## Pipeline

```
Codal search ─► fetch filing HTML ─► parse statement tables ─► map Persian labels → canonical keys
                                                                        │
TSETMC ─► price, volume, market cap, indices                            ▼
tgju.org ─► daily free-market USD/IRR ───────────► PostgreSQL ◄── aggregate to standard line items
```

| Module | Role |
|---|---|
| `codal_client.py` | search filings per symbol and download statement content |
| `parser.py` | classify tables (balance sheet / income / cash flow), normalize headers and period columns |
| `line_items.py` | about 600 Persian label variants mapped to canonical keys (normalized for Arabic/Persian characters and spacing) |
| `standard_items.py` | canonical keys mapped onto a global template (Revenue, Gross Profit, EBIT, Net Income, Total Assets, CFO…), with no double-counting |
| `tsetmc_client.py`, `fetch_market_data.py` | instrument matching, closing prices, market cap, headline indices, English names |
| `fx_rates.py`, `fetch_fx_rates.py` | USD/IRR free-market history, used to express statements in USD |
| `jalali.py`, `numeric.py` | Jalali↔Gregorian dates and Persian-digit and parenthesized-negative number parsing |
| `db.py`, `db/schema.sql` | SQLAlchemy models and upserts (companies, filings, line items, mappings, FX, market snapshots) |
| `ingest.py` | CLI entry point |

## Run

```bash
pip install -r requirements.txt
cp .env.example .env            # set DATABASE_URL (PostgreSQL)
psql "$DATABASE_URL" -f db/schema.sql

python ingest.py --limit 5      # smoke test on 5 companies from companies.csv
python ingest.py --symbols فولاد,وبملت
python fetch_market_data.py
python fetch_fx_rates.py
```

Codal and TSETMC may require an Iranian IP. tgju.org is reachable from anywhere.

Unmapped labels are collected during ingestion, so the mapping table can be extended over time.
