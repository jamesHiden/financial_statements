"""CLI: fetch and store the full USD/IRR free-market rate history.

Usage:
    python fetch_fx_rates.py

Cheap to re-run any time to pick up new days - tgju.org's API returns the
whole history in one request and this just upserts on top of what's there.
"""
import db
import fx_rates


def main() -> None:
    rates = fx_rates.fetch_usd_irr_history()
    print(f"fetched {len(rates)} daily rates ({rates[0].day} to {rates[-1].day})")
    with db.get_session() as session:
        db.upsert_fx_rates(session, rates)
    print("stored.")


if __name__ == "__main__":
    main()
