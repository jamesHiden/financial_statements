"""CLI: fetch current TSETMC market data (price, volume, market cap) for
every company we track, plus the two headline indices.

Requires VPN access to reach TSETMC from this sandbox (same as Codal).

Usage:
    python fetch_market_data.py
"""
import sys

import db
import tsetmc_client


def fetch_company_snapshot(session, http, company: db.Company) -> None:
    # Try the previously-matched code first (skips a search call on repeat
    # runs), then fall back to a fresh search - covers both the common case
    # and a stored code that's gone stale (e.g. a relisted instrument).
    candidates = [company.tsetmc_ins_code] if company.tsetmc_ins_code else []
    candidates += [
        m.ins_code for m in tsetmc_client.find_exact_matches(company.symbol, session=http)
    ]

    if not candidates:
        print(f"  [{company.symbol}] no clean TSETMC match, skipping", file=sys.stderr)
        return

    price = shares_outstanding = identity = ins_code = None
    for candidate in candidates:
        try:
            price = tsetmc_client.get_closing_price_info(candidate, session=http)
            shares_outstanding = tsetmc_client.get_shares_outstanding(candidate, session=http)
            identity = tsetmc_client.get_instrument_identity(candidate, session=http)
            ins_code = candidate
            break
        except Exception:
            continue

    if price is None:
        print(f"  [{company.symbol}] all {len(candidates)} candidate(s) failed to fetch", file=sys.stderr)
        return

    if ins_code != company.tsetmc_ins_code:
        db.set_tsetmc_ins_code(session, company.id, ins_code)
    if identity.sector and identity.sector != company.industry:
        db.set_industry(session, company.id, identity.sector)
    if identity.name_en and identity.name_en != company.name_en:
        db.set_english_identity(session, company.id, identity.name_en, identity.mnemonic_en)

    market_cap = price.closing_price * shares_outstanding if shares_outstanding else None

    db.upsert_market_snapshot(
        session,
        company_id=company.id,
        last_price=price.last_price,
        closing_price=price.closing_price,
        price_change_pct=price.price_change_pct,
        day_low=price.day_low,
        day_high=price.day_high,
        volume=price.volume,
        trade_value=price.trade_value,
        trade_count=price.trade_count,
        market_cap=market_cap,
    )
    print(f"  [{company.symbol}] closing={price.closing_price} volume={price.volume} market_cap={market_cap}")


def main() -> None:
    http = tsetmc_client.new_session()

    with db.get_session() as session:
        companies = session.query(db.Company).order_by(db.Company.symbol).all()
        company_data = [(c.id, c.symbol, c.tsetmc_ins_code) for c in companies]

    print(f"Fetching market data for {len(company_data)} companies...")
    for company_id, symbol, ins_code in company_data:
        try:
            with db.get_session() as session:
                company = session.get(db.Company, company_id)
                fetch_company_snapshot(session, http, company)
        except Exception as exc:
            # A single flaky request (TSETMC returns transient 5xx sometimes)
            # shouldn't abort the whole batch - same lesson as ingest.py.
            print(f"  [{symbol}] unexpected error, skipping: {exc!r}", file=sys.stderr)

    print("Fetching indices...")
    with db.get_session() as session:
        total = tsetmc_client.get_index_snapshot(tsetmc_client.INDEX_TOTAL, session=http)
        db.upsert_market_index(session, "total", total.value, total.change_pct)
        print(f"  total index: {total.value} ({total.change_pct}%)")

        equal_weight = tsetmc_client.get_index_snapshot(tsetmc_client.INDEX_EQUAL_WEIGHT, session=http)
        db.upsert_market_index(session, "equal_weight", equal_weight.value, equal_weight.change_pct)
        print(f"  equal-weight index: {equal_weight.value} ({equal_weight.change_pct}%)")

    print("done.")


if __name__ == "__main__":
    main()
