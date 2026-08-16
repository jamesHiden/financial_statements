"""CLI entrypoint: fetch, parse, and store Codal filings for a list of companies.

Usage:
    python ingest.py                          # ingest every symbol in companies.csv
    python ingest.py --symbols فولاد,وبملت      # ingest just these symbols
    python ingest.py --limit 5                 # first 5 symbols in the file (smoke test)
    python ingest.py --seed-mappings-only       # just sync line_item_mapping table
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import requests

import codal_client
import db
import parser as filing_parser

DEFAULT_COMPANIES_FILE = Path(__file__).parent / "companies.csv"


def load_symbols(companies_file: Path) -> list[str]:
    with open(companies_file, newline="", encoding="utf-8") as f:
        return [row["ticker"].strip() for row in csv.DictReader(f) if row["ticker"].strip()]


def ingest_symbol(session, symbol: str, http: requests.Session, unmapped_labels: set[tuple[str, str]]) -> None:
    company = db.upsert_company(session, symbol=symbol)

    try:
        filings = codal_client.search_filings(symbol, session=http)
    except requests.RequestException as exc:
        print(f"  [{symbol}] could not list filings: {exc}", file=sys.stderr)
        return

    print(f"  [{symbol}] {len(filings)} filings found")

    for meta in filings:
        try:
            content = codal_client.fetch_filing_content(meta.excel_url, session=http)
            statements = filing_parser.parse_filing(content)
        except (requests.RequestException, ValueError) as exc:
            print(f"    could not process '{meta.title}': {exc}", file=sys.stderr)
            continue

        for statement in statements:
            db.store_parsed_statement(
                session,
                company_id=company.id,
                statement=statement,
                audited=meta.audited,
                amended=meta.amended,
                consolidated=meta.consolidated,
                source_url=meta.excel_url,
            )
            for row in statement.rows:
                if row.canonical_key is None:
                    unmapped_labels.add((statement.statement_type, row.label_fa))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--companies-file", type=Path, default=DEFAULT_COMPANIES_FILE)
    parser.add_argument("--symbols", type=str, help="comma-separated symbols, overrides --companies-file")
    parser.add_argument("--limit", type=int, default=None, help="only ingest the first N symbols")
    parser.add_argument("--seed-mappings-only", action="store_true", help="sync line_item_mapping table and exit")
    args = parser.parse_args()

    with db.get_session() as session:
        db.seed_line_item_mappings(session)
    print("line_item_mapping table synced.")
    if args.seed_mappings_only:
        return

    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = load_symbols(args.companies_file)
    if args.limit:
        symbols = symbols[: args.limit]

    print(f"Ingesting {len(symbols)} companies...")
    unmapped_labels: set[tuple[str, str]] = set()
    http = requests.Session()

    for symbol in symbols:
        with db.get_session() as session:
            ingest_symbol(session, symbol, http, unmapped_labels)

    if unmapped_labels:
        print(f"\n{len(unmapped_labels)} unmapped labels encountered (stored with canonical_key=NULL):")
        for statement_type, label_fa in sorted(unmapped_labels):
            print(f"  [{statement_type}] {label_fa}")
    else:
        print("\nAll line items mapped to a canonical key.")


if __name__ == "__main__":
    main()
