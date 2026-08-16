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
    session = session or requests.Session()
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
    session = session or requests.Session()
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content
