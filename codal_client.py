"""Thin client for Codal's public search API.

Replaces codal_api.py: same unauthenticated search.codal.ir endpoint, but
returns structured results in memory instead of downloading files to a
hardcoded local folder. Synchronous + requests is plenty fast for the
MVP scope (a few dozen companies); revisit with aiohttp if the company
list grows much larger.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import requests

SEARCH_URL = "https://search.codal.ir/api/search/v2/q"

# Codal's API hangs (no response, no error) on requests that don't look like
# they came from a browser - plain `requests` with its default User-Agent
# gets silently stalled. Mimic the headers the real codal.ir site sends.
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
    "Referer": "https://codal.ir/",
    "Origin": "https://codal.ir",
}


def new_session() -> requests.Session:
    """A requests Session pre-configured with browser-like headers."""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session

# Isic=571919 + Category=1 mirrors the filter the original script used to
# scope results to periodic financial statements.
SEARCH_PARAMS = {
    "Audited": "true",
    "AuditorRef": "-1",
    "Category": "1",
    "Childs": "false",
    "CompanyState": "0",
    "CompanyType": "-1",
    "Consolidatable": "true",
    "IsNotAudited": "false",
    "Isic": "571919",
    "Length": "-1",
    "LetterType": "-1",
    "Mains": "true",
    "NotAudited": "true",
    "NotConsolidatable": "true",
    "Publisher": "false",
    "TracingNo": "-1",
    "search": "true",
}


@dataclass(frozen=True)
class FilingMeta:
    symbol: str
    title: str
    publish_datetime: str  # e.g. '1402/03/15 10:22:00'
    excel_url: str
    audited: bool
    amended: bool
    consolidated: bool


def _parse_title_flags(title: str) -> tuple[bool, bool, bool]:
    audited = "حسابرسی نشده" not in title
    amended = "اصلاحیه" in title
    consolidated = "تلفیقی" in title
    return audited, amended, consolidated


def search_filings(symbol: str, session: requests.Session | None = None) -> list[FilingMeta]:
    """Return all periodic-statement filings Codal has for a ticker symbol."""
    session = session or new_session()
    filings: list[FilingMeta] = []

    page = 1
    while True:
        params = {**SEARCH_PARAMS, "Symbol": symbol, "PageNumber": page}
        resp = session.get(SEARCH_URL, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()

        letters = payload.get("Letters", [])
        if not letters:
            break

        for letter in letters:
            title = letter["Title"]
            audited, amended, consolidated = _parse_title_flags(title)
            filings.append(
                FilingMeta(
                    symbol=letter["Symbol"],
                    title=title,
                    publish_datetime=letter["PublishDateTime"],
                    excel_url=letter["ExcelUrl"],
                    audited=audited,
                    amended=amended,
                    consolidated=consolidated,
                )
            )

        if page >= payload.get("Page", 1):
            break
        page += 1

    return filings


def fetch_filing_content(url: str, session: requests.Session | None = None) -> bytes:
    """Download a filing's "Excel" export (actually an HTML table document)."""
    session = session or new_session()
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content
