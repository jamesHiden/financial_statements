"""Thin client for TSETMC's (Tehran Stock Exchange) public, unauthenticated
API - reverse-engineered from tsetmc.com's own JS bundle (api/Instrument/*,
api/ClosingPrice/*, api/Index/*). Like Codal, it silently stalls on requests
without browser-like headers, and the sandbox this runs in can't reach it
directly - needs the same VPN used for Codal.
"""
from __future__ import annotations

from dataclasses import dataclass

import requests

BASE_URL = "https://cdn.tsetmc.com/api"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    "Referer": "https://www.tsetmc.com/",
}

# Well-known instrument codes for the two headline indices.
INDEX_TOTAL = "32097828799138957"  # شاخص کل (TEDPIX)
INDEX_EQUAL_WEIGHT = "67130298613737946"  # شاخص هم‌وزن


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


@dataclass(frozen=True)
class InstrumentMatch:
    ins_code: str
    symbol: str  # lVal18AFC
    name: str  # lVal30
    flow: int  # 1 = بازار بورس (main market) - what we want for equities


def search_instrument(symbol: str, session: requests.Session | None = None) -> list[InstrumentMatch]:
    """Search TSETMC by (partial) symbol text."""
    session = session or new_session()
    resp = session.get(f"{BASE_URL}/Instrument/GetInstrumentSearch/{symbol}", timeout=30)
    resp.raise_for_status()
    results = resp.json().get("instrumentSearch", [])
    return [
        InstrumentMatch(
            ins_code=r["insCode"], symbol=r["lVal18AFC"], name=r["lVal30"], flow=r["flow"]
        )
        for r in results
    ]


def find_exact_matches(symbol: str, session: requests.Session | None = None) -> list[InstrumentMatch]:
    """Every exact-symbol candidate on Iran's two regulated equity markets -
    flow=1 (Tehran Stock Exchange) or flow=2 (Iran Fara Bourse, the
    secondary market where plenty of large, legitimate companies list
    instead) - ordered flow=1 first. Usually there's exactly one; a
    reorganized/relisted company can leave more than one behind, including
    stale duplicates that 500 on price lookups, so callers should be
    prepared to try each in order rather than assume the first works."""
    matches = search_instrument(symbol, session=session)
    exact = [m for m in matches if m.symbol == symbol and m.flow in (1, 2)]
    return sorted(exact, key=lambda m: m.flow)


@dataclass(frozen=True)
class ClosingPriceInfo:
    last_price: float
    closing_price: float
    price_change_pct: float
    day_low: float
    day_high: float
    volume: float
    trade_value: float
    trade_count: float


def get_closing_price_info(ins_code: str, session: requests.Session | None = None) -> ClosingPriceInfo:
    session = session or new_session()
    resp = session.get(f"{BASE_URL}/ClosingPrice/GetClosingPriceInfo/{ins_code}", timeout=30)
    resp.raise_for_status()
    d = resp.json()["closingPriceInfo"]
    return ClosingPriceInfo(
        last_price=d["pDrCotVal"],
        closing_price=d["pClosing"],
        price_change_pct=d["priceChange"],
        day_low=d["priceMin"],
        day_high=d["priceMax"],
        volume=d["qTotTran5J"],
        trade_value=d["qTotCap"],
        trade_count=d["zTotTran"],
    )


@dataclass(frozen=True)
class InstrumentIdentity:
    sector: str | None
    isin: str | None
    name_en: str | None  # e.g. "Khalij Fars"
    mnemonic_en: str | None  # e.g. "PKLJ1" - a Latin ticker-ish code


def get_instrument_identity(ins_code: str, session: requests.Session | None = None) -> InstrumentIdentity:
    session = session or new_session()
    resp = session.get(f"{BASE_URL}/Instrument/GetInstrumentIdentity/{ins_code}", timeout=30)
    resp.raise_for_status()
    d = resp.json()["instrumentIdentity"]
    return InstrumentIdentity(
        sector=(d.get("sector") or {}).get("lSecVal"),
        name_en=d.get("lVal18"),
        mnemonic_en=d.get("cValMne"),
        isin=d.get("cIsin"),
    )


def get_shares_outstanding(ins_code: str, session: requests.Session | None = None) -> float | None:
    """Current share count, from the most recent entry in TSETMC's share
    change history (GetInstrumentIdentity's own zTitad field is unreliable -
    it comes back empty)."""
    session = session or new_session()
    resp = session.get(f"{BASE_URL}/Instrument/GetInstrumentShareChange/{ins_code}", timeout=30)
    resp.raise_for_status()
    changes = resp.json().get("instrumentShareChange", [])
    if not changes:
        return None
    latest = max(changes, key=lambda c: c["dEven"])
    return latest["numberOfShareNew"]


@dataclass(frozen=True)
class IndexSnapshot:
    value: float
    change_pct: float


def get_index_snapshot(index_ins_code: str, session: requests.Session | None = None) -> IndexSnapshot:
    """Latest value for an index, from today's intraday series."""
    session = session or new_session()
    resp = session.get(f"{BASE_URL}/Index/GetIndexB1LastDay/{index_ins_code}", timeout=30)
    resp.raise_for_status()
    points = resp.json()["indexB1"]
    last = next((p for p in points if p.get("last")), points[-1])
    return IndexSnapshot(value=last["xDrNivJIdx004"], change_pct=last["xVarIdxJRfV"])
