"""Fetch the historical USD/IRR free-market ("دلار آزاد") daily rate from
tgju.org's public API - no auth, no VPN needed (unlike Codal, tgju.org is
reachable directly). Used to convert Rial-denominated financial statement
figures to USD so cross-period comparisons aren't dominated by Iran's
inflation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import requests

HISTORY_URL = "https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl"

# Table columns, in order: بازگشایی(Open), کمترین(Low), بیشترین(High),
# پایانی(Close), میزان تغییر, درصد تغییر, تاریخ/میلادی, تاریخ/شمسی.
_CLOSE_INDEX = 3
_GREGORIAN_DATE_INDEX = 6


@dataclass(frozen=True)
class DailyRate:
    day: date
    close_rial: float


def _parse_number(text: str) -> float:
    return float(text.replace(",", ""))


def fetch_usd_irr_history() -> list[DailyRate]:
    """Every daily close tgju has for the free-market USD/IRR rate, oldest first."""
    resp = requests.get(HISTORY_URL, params={"lang": "fa", "order_dir": "asc"}, timeout=30)
    resp.raise_for_status()
    rows = resp.json()["data"]

    rates = []
    for row in rows:
        close = _parse_number(row[_CLOSE_INDEX])
        day_str = row[_GREGORIAN_DATE_INDEX]  # 'YYYY/MM/DD'
        year, month, day_num = (int(p) for p in day_str.split("/"))
        rates.append(DailyRate(day=date(year, month, day_num), close_rial=close))
    return rates
